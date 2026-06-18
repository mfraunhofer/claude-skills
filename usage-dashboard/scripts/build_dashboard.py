#!/usr/bin/env python3
"""Token usage dashboard for Claude Code.

Reads every session transcript (~/.claude/projects/**/*.jsonl), aggregates token
usage per day / model / project / session / time-of-day / main-chat-vs-subagent,
and renders a self-contained HTML dashboard with a USD cost equivalent (API list
prices).

Cache: per-file aggregates are persisted under ~/.claude/cache/usage-dashboard/.
Claude Code deletes transcripts after ~30 days; deleted files stay in the cache
(marked archived) so your history grows from first install onward.

Usage:
    python3 build_dashboard.py            # build (writes ~/.claude/cache/usage-dashboard/index.html)
    python3 build_dashboard.py --open     # build + open in the browser
"""

import gzip
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

PROJECTS_DIR = Path.home() / ".claude" / "projects"
CACHE_DIR = Path.home() / ".claude" / "cache" / "usage-dashboard"
CACHE_FILE = CACHE_DIR / "cache.json.gz"
HTML_FILE = CACHE_DIR / "index.html"

# Time zone for day bucketing + the time-of-day chart. Override with the TZ env
# var (e.g. TZ="America/New_York"); defaults to the system local time zone.
try:
    TZ = ZoneInfo(os.environ["TZ"]) if os.environ.get("TZ") else datetime.now().astimezone().tzinfo
except Exception:
    TZ = datetime.now().astimezone().tzinfo

# Home directory encoded the way Claude Code names project folders: the absolute
# path with slashes turned into dashes (e.g. a home dir becomes "-home-you").
# Used to strip that prefix from project labels.
HOME_ENC = str(Path.home()).replace("/", "-")

# API list prices per 1M tokens (USD). Order = match priority (substring).
# Cache writes: 5m TTL = 1.25x input, 1h TTL = 2x input. Cache reads = 0.1x input.
PRICING = [
    ("fable-5", 10.0, 50.0),
    ("opus-4-1", 15.0, 75.0),
    ("opus-4-0", 15.0, 75.0),
    ("opus-4-2", 15.0, 75.0),
    ("opus", 5.0, 25.0),
    ("sonnet", 3.0, 15.0),
    ("haiku", 1.0, 5.0),
]
FALLBACK_PRICE = (5.0, 25.0)


def price_for(model):
    for sub, inp, out in PRICING:
        if sub in model:
            return inp, out
    return FALLBACK_PRICE


def cost_of(model, inp, out, w5, w1h, read):
    p_in, p_out = price_for(model)
    return (
        inp * p_in
        + out * p_out
        + w5 * p_in * 1.25
        + w1h * p_in * 2.0
        + read * p_in * 0.1
    ) / 1_000_000


def project_label(folder):
    name = folder
    if name.startswith(HOME_ENC):
        name = name[len(HOME_ENC):]
    name = name.lstrip("-")
    if not name or folder.startswith("-private-"):
        return "tmp / other"
    if folder == "-claude":
        return ".claude (system)"
    return name


def model_label(model):
    return model.replace("claude-", "").replace("[1m]", "")


def parse_file(path):
    """One transcript file -> list of compact records."""
    records = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f):
                if '"usage"' not in line:
                    continue
                try:
                    obj = json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    continue
                if obj.get("type") != "assistant":
                    continue
                msg = obj.get("message") or {}
                usage = msg.get("usage") or {}
                model = msg.get("model") or ""
                if not model or model == "<synthetic>":
                    continue
                ts = obj.get("timestamp") or ""
                if not ts:
                    continue
                msgid = msg.get("id") or ""
                reqid = obj.get("requestId") or ""
                key = f"{msgid}|{reqid}" if (msgid or reqid) else f"{path.name}:{lineno}"
                cc = usage.get("cache_creation") or {}
                w_total = usage.get("cache_creation_input_tokens") or 0
                w1h = cc.get("ephemeral_1h_input_tokens")
                w5 = cc.get("ephemeral_5m_input_tokens")
                if w1h is None and w5 is None:
                    w5, w1h = w_total, 0  # old transcripts without the breakdown
                records.append([
                    key,
                    ts,
                    model,
                    usage.get("input_tokens") or 0,
                    usage.get("output_tokens") or 0,
                    w5 or 0,
                    w1h or 0,
                    usage.get("cache_read_input_tokens") or 0,
                    1 if obj.get("isSidechain") else 0,
                    obj.get("sessionId") or path.stem,
                ])
    except OSError:
        pass
    return records


def load_cache():
    if CACHE_FILE.exists():
        try:
            with gzip.open(CACHE_FILE, "rt", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass
    return {"version": 1, "files": {}}


def save_cache(cache):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_FILE.with_suffix(".tmp")
    with gzip.open(tmp, "wt", encoding="utf-8") as f:
        json.dump(cache, f, separators=(",", ":"))
    tmp.replace(CACHE_FILE)


def scan(cache):
    """Read all transcript files (incremental via cache)."""
    files = cache["files"]
    seen_paths = set()
    todo = []
    if not PROJECTS_DIR.exists():
        return 0
    for proj_dir in sorted(PROJECTS_DIR.iterdir()):
        if not proj_dir.is_dir():
            continue
        for path in proj_dir.rglob("*.jsonl"):
            rel = str(path.relative_to(PROJECTS_DIR))
            seen_paths.add(rel)
            try:
                st = path.stat()
            except OSError:
                continue
            entry = files.get(rel)
            if entry and entry["mtime"] == st.st_mtime and entry["size"] == st.st_size:
                continue
            todo.append((rel, path, st))

    total = len(todo)
    for i, (rel, path, st) in enumerate(todo):
        if total > 50 and i % 200 == 0:
            print(f"  parse {i}/{total} ...", flush=True)
        files[rel] = {
            "mtime": st.st_mtime,
            "size": st.st_size,
            "project": project_label(path.relative_to(PROJECTS_DIR).parts[0]),
            "records": parse_file(path),
        }
    # Deleted files stay in the cache (history!), just get marked.
    for rel, entry in files.items():
        entry["archived"] = rel not in seen_paths
    return total


def aggregate(cache):
    """Cache -> aggregates. Global dedupe over (message.id, requestId)."""
    seen = set()
    daily = defaultdict(lambda: defaultdict(float))             # date -> field -> val
    daily_model_cost = defaultdict(lambda: defaultdict(float))  # date -> model -> $
    model_tot = defaultdict(lambda: defaultdict(float))         # model -> field
    proj_tot = defaultdict(lambda: defaultdict(float))          # project -> field
    hour_cost = defaultdict(float)                              # 0..23 -> $
    sessions = defaultdict(lambda: {"first": None, "last": None, "msgs": 0,
                                    "cost": 0.0, "out": 0, "models": set(),
                                    "project": "", "tok": 0})
    side = {"main": 0.0, "side": 0.0}
    daily_sessions = defaultdict(set)

    for entry in cache["files"].values():
        proj = entry.get("project", "?")
        for rec in entry["records"]:
            key, ts, model, inp, out, w5, w1h, read, sidechain, sess = rec
            if key in seen:
                continue
            seen.add(key)
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(TZ)
            except ValueError:
                continue
            day = dt.strftime("%Y-%m-%d")
            cost = cost_of(model, inp, out, w5, w1h, read)
            ml = model_label(model)

            d = daily[day]
            d["in"] += inp; d["out"] += out; d["w"] += w5 + w1h
            d["read"] += read; d["cost"] += cost; d["msgs"] += 1
            daily_sessions[day].add(sess)
            daily_model_cost[day][ml] += cost

            m = model_tot[ml]
            m["in"] += inp; m["out"] += out; m["w"] += w5 + w1h
            m["read"] += read; m["cost"] += cost; m["msgs"] += 1

            p = proj_tot[proj]
            p["cost"] += cost; p["msgs"] += 1
            p["tok"] += inp + out + w5 + w1h

            hour_cost[dt.hour] += cost
            side["side" if sidechain else "main"] += cost

            s = sessions[sess]
            s["msgs"] += 1; s["cost"] += cost; s["out"] += out
            s["tok"] += inp + out + w5 + w1h
            s["models"].add(ml); s["project"] = proj
            iso = dt.isoformat()
            if s["first"] is None or iso < s["first"]:
                s["first"] = iso
            if s["last"] is None or iso > s["last"]:
                s["last"] = iso

    for day, sset in daily_sessions.items():
        daily[day]["sessions"] = len(sset)
    return {
        "daily": daily, "daily_model_cost": daily_model_cost,
        "model_tot": model_tot, "proj_tot": proj_tot,
        "hour_cost": hour_cost, "sessions": sessions, "side": side,
        "n_records": len(seen),
    }


# ---------------------------------------------------------------- formatting

def fmt_tok(v):
    if v >= 1e9:
        return f"{v / 1e9:.1f}B"
    if v >= 1e6:
        return f"{v / 1e6:.1f}M"
    if v >= 1e3:
        return f"{v / 1e3:.0f}k"
    return f"{v:.0f}"


def fmt_usd(v):
    return "$" + f"{v:,.2f}"


def fmt_int(v):
    return f"{int(v):,}"


MODEL_COLORS = {
    "opus": "#8b5fc9", "fable": "#c9a8ef", "sonnet": "#6fafe0",
    "haiku": "#7fd0a8",
}


def color_for_model(ml):
    for sub, c in MODEL_COLORS.items():
        if sub in ml:
            return c
    return "#9a93a8"


# ---------------------------------------------------------------- SVG charts

CHART_W, CHART_H, PAD_L, PAD_B, PAD_T = 960, 230, 56, 26, 10


def _grid(maxv, fmt):
    lines = []
    for i in range(1, 5):
        y = PAD_T + (CHART_H - PAD_T - PAD_B) * (1 - i / 4)
        val = maxv * i / 4
        lines.append(
            f'<line x1="{PAD_L}" y1="{y:.0f}" x2="{CHART_W}" y2="{y:.0f}" class="grid"/>'
            f'<text x="{PAD_L - 6}" y="{y + 4:.0f}" class="ylabel">{fmt(val)}</text>'
        )
    return "".join(lines)


def stacked_svg(days, layers, fmt=fmt_tok, tooltip_fmt=None):
    """layers: list of (label, color, {day: value})."""
    if not days:
        return "<p class='muted'>No data.</p>"
    totals = {d: sum(layer[2].get(d, 0) for layer in layers) for d in days}
    maxv = max(totals.values()) or 1
    plot_h = CHART_H - PAD_T - PAD_B
    slot = (CHART_W - PAD_L) / len(days)
    bw = max(2.0, slot * 0.72)
    parts = [f'<svg viewBox="0 0 {CHART_W} {CHART_H}" class="chart">', _grid(maxv, fmt)]
    label_every = max(1, len(days) // 12)
    for i, d in enumerate(days):
        x = PAD_L + i * slot + (slot - bw) / 2
        y = CHART_H - PAD_B
        tip = [d]
        for label, color, data in layers:
            v = data.get(d, 0)
            if v <= 0:
                continue
            h = v / maxv * plot_h
            y -= h
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{color}"/>'
            )
            tip.append(f"{label}: {(tooltip_fmt or fmt)(v)}")
        tip.append(f"Total: {(tooltip_fmt or fmt)(totals[d])}")
        parts.append(
            f'<rect x="{PAD_L + i * slot:.1f}" y="{PAD_T}" width="{slot:.1f}" '
            f'height="{plot_h}" fill="transparent"><title>{chr(10).join(tip)}</title></rect>'
        )
        if i % label_every == 0:
            parts.append(
                f'<text x="{x + bw / 2:.0f}" y="{CHART_H - 8}" class="xlabel">{d[5:]}</text>'
            )
    parts.append("</svg>")
    return "".join(parts)


def hour_svg(hour_cost):
    maxv = max(hour_cost.values() or [1]) or 1
    plot_h = CHART_H - PAD_T - PAD_B
    slot = (CHART_W - PAD_L) / 24
    bw = slot * 0.6
    parts = [f'<svg viewBox="0 0 {CHART_W} {CHART_H}" class="chart">', _grid(maxv, fmt_usd)]
    for h in range(24):
        v = hour_cost.get(h, 0)
        bh = v / maxv * plot_h
        x = PAD_L + h * slot + (slot - bw) / 2
        parts.append(
            f'<rect x="{x:.1f}" y="{CHART_H - PAD_B - bh:.1f}" width="{bw:.1f}" '
            f'height="{bh:.1f}" fill="#8b5fc9"><title>{h:02d}:00–{(h + 1) % 24:02d}:00: {fmt_usd(v)}</title></rect>'
            f'<text x="{x + bw / 2:.0f}" y="{CHART_H - 8}" class="xlabel">{h}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def legend(items):
    spans = "".join(
        f'<span class="leg"><i style="background:{c}"></i>{l}</span>' for l, c in items
    )
    return f'<div class="legend">{spans}</div>'


# ---------------------------------------------------------------- HTML

CSS = """
:root { --bg:#161220; --card:#1f1930; --border:#332a4a; --text:#ece7f4;
        --muted:#9a93a8; --accent:#b284e4; --accent-soft:#2c2244; }
* { box-sizing:border-box; margin:0; padding:0; }
body { background:var(--bg); color:var(--text);
       font:15px/1.5 -apple-system,'Segoe UI',sans-serif; padding:32px 24px 64px; }
.wrap { max-width:1020px; margin:0 auto; }
h1 { font-size:1.5rem; margin-bottom:4px; }
h2 { font-size:1.05rem; margin:36px 0 12px; color:var(--accent); }
.sub { color:var(--muted); font-size:.85rem; margin-bottom:24px; }
.kpis { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; }
.kpi { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:14px 16px; }
.kpi b { display:block; font-size:1.35rem; margin-top:2px; }
.kpi span { color:var(--muted); font-size:.78rem; }
.card { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:16px; }
.chart { width:100%; height:auto; display:block; }
.grid { stroke:#332a4a; stroke-width:1; }
.ylabel { fill:#9a93a8; font-size:11px; text-anchor:end; }
.xlabel { fill:#9a93a8; font-size:10px; text-anchor:middle; }
.legend { margin-top:10px; font-size:.8rem; color:var(--muted); }
.leg { margin-right:16px; white-space:nowrap; }
.leg i { display:inline-block; width:10px; height:10px; border-radius:2px; margin-right:5px; }
table { width:100%; border-collapse:collapse; font-size:.85rem; }
th { text-align:left; color:var(--muted); font-weight:500; padding:6px 10px;
     border-bottom:1px solid var(--border); }
td { padding:6px 10px; border-bottom:1px solid #2a2240; }
td.num, th.num { text-align:right; font-variant-numeric:tabular-nums; }
tr:last-child td { border-bottom:none; }
.muted { color:var(--muted); }
.bar { display:inline-block; height:8px; border-radius:4px; background:var(--accent);
       vertical-align:middle; margin-right:8px; }
.note { font-size:.78rem; color:var(--muted); margin-top:8px; }
"""


def build_html(agg):
    daily = agg["daily"]
    days = sorted(daily.keys())
    if not days:
        return "<html><body>No data found.</body></html>"
    show_days = days[-60:]

    today = datetime.now(TZ).strftime("%Y-%m-%d")
    cost_today = daily.get(today, {}).get("cost", 0)
    cost_7 = sum(daily[d]["cost"] for d in days[-7:])
    cost_30 = sum(daily[d]["cost"] for d in days[-30:])
    cost_all = sum(daily[d]["cost"] for d in days)
    tok_new_30 = sum(daily[d]["in"] + daily[d]["out"] for d in days[-30:])
    tok_read_30 = sum(daily[d]["read"] for d in days[-30:])
    avg_30 = cost_30 / min(30, len(days))

    kpis = [
        ("Today", fmt_usd(cost_today)),
        ("Last 7 days", fmt_usd(cost_7)),
        ("Last 30 days", fmt_usd(cost_30)),
        ("Avg/day (30d)", fmt_usd(avg_30)),
        ("Total tracked", fmt_usd(cost_all)),
        ("New tokens 30d (in+out)", fmt_tok(tok_new_30)),
        ("Cache reads 30d (0.1x, recycled)", fmt_tok(tok_read_30)),
    ]
    kpi_html = "".join(f'<div class="kpi"><span>{l}</span><b>{v}</b></div>' for l, v in kpis)

    # Chart 1: cost per day, stacked by model
    models_sorted = sorted(agg["model_tot"], key=lambda m: -agg["model_tot"][m]["cost"])
    layers1 = [(m, color_for_model(m), agg["daily_model_cost_by_model"][m])
               for m in models_sorted]
    chart1 = stacked_svg(show_days, layers1, fmt=fmt_usd)
    leg1 = legend([(m, color_for_model(m)) for m in models_sorted])

    # Chart 2: tokens per day (real work, excluding cache reads)
    layers2 = [
        ("Output", "#c9a8ef", {d: daily[d]["out"] for d in show_days}),
        ("Input (uncached)", "#8b5fc9", {d: daily[d]["in"] for d in show_days}),
        ("Cache writes", "#4a3a6e", {d: daily[d]["w"] for d in show_days}),
    ]
    chart2 = stacked_svg(show_days, layers2)
    leg2 = legend([(l, c) for l, c, _ in layers2])

    # Chart 3: cache reads separately (would otherwise dominate)
    layers3 = [("Cache reads", "#3d3552", {d: daily[d]["read"] for d in show_days})]
    chart3 = stacked_svg(show_days, layers3)

    chart_hours = hour_svg(agg["hour_cost"])

    # Model table
    rows = []
    for m in models_sorted:
        t = agg["model_tot"][m]
        rows.append(
            f"<tr><td>{m}</td><td class='num'>{fmt_int(t['msgs'])}</td>"
            f"<td class='num'>{fmt_tok(t['in'])}</td><td class='num'>{fmt_tok(t['out'])}</td>"
            f"<td class='num'>{fmt_tok(t['w'])}</td><td class='num'>{fmt_tok(t['read'])}</td>"
            f"<td class='num'>{fmt_usd(t['cost'])}</td></tr>"
        )
    model_table = (
        "<table><tr><th>Model</th><th class='num'>Responses</th><th class='num'>Input</th>"
        "<th class='num'>Output</th><th class='num'>Cache-W</th><th class='num'>Cache-R</th>"
        "<th class='num'>Cost</th></tr>" + "".join(rows) + "</table>"
    )

    # Project table
    projs = sorted(agg["proj_tot"].items(), key=lambda kv: -kv[1]["cost"])[:12]
    maxp = projs[0][1]["cost"] if projs else 1
    rows = []
    for name, t in projs:
        w = max(2, int(t["cost"] / maxp * 120))
        rows.append(
            f"<tr><td><span class='bar' style='width:{w}px'></span>{name}</td>"
            f"<td class='num'>{fmt_int(t['msgs'])}</td>"
            f"<td class='num'>{fmt_tok(t['tok'])}</td>"
            f"<td class='num'>{fmt_usd(t['cost'])}</td></tr>"
        )
    proj_table = (
        "<table><tr><th>Project</th><th class='num'>Responses</th>"
        "<th class='num'>Tokens (excl. cache-R)</th><th class='num'>Cost</th></tr>"
        + "".join(rows) + "</table>"
    )

    # Top sessions
    top_sess = sorted(agg["sessions"].values(), key=lambda s: -s["cost"])[:15]
    rows = []
    for s in top_sess:
        first = datetime.fromisoformat(s["first"])
        dur_h = (datetime.fromisoformat(s["last"]) - first).total_seconds() / 3600
        rows.append(
            f"<tr><td>{first.strftime('%b %d, %H:%M')}</td><td>{s['project']}</td>"
            f"<td>{', '.join(sorted(s['models']))}</td>"
            f"<td class='num'>{dur_h:.1f}h</td><td class='num'>{fmt_int(s['msgs'])}</td>"
            f"<td class='num'>{fmt_tok(s['out'])}</td><td class='num'>{fmt_usd(s['cost'])}</td></tr>"
        )
    sess_table = (
        "<table><tr><th>Start</th><th>Project</th><th>Models</th><th class='num'>Duration</th>"
        "<th class='num'>Responses</th><th class='num'>Output</th><th class='num'>Cost</th></tr>"
        + "".join(rows) + "</table>"
    )

    side_total = agg["side"]["main"] + agg["side"]["side"] or 1
    side_pct = agg["side"]["side"] / side_total * 100

    gen_ts = datetime.now(TZ).strftime("%Y-%m-%d %H:%M")
    span = f"{days[0]} to {days[-1]}"

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Claude Code -- Token Usage</title><style>{CSS}</style></head>
<body><div class="wrap">
<h1>Claude Code &mdash; Token Usage</h1>
<p class="sub">Range {span} &middot; {fmt_int(agg['n_records'])} API responses tracked &middot;
Generated {gen_ts} &middot; Cost = <strong>API list-price equivalent in USD</strong>
(if you're on a flat-rate plan, this is the value you're getting, not a bill)</p>
<div class="kpis">{kpi_html}</div>
<p class="note"><strong>New tokens</strong> = what's actually consumed (what Claude reads + writes).
<strong>Cache reads</strong> = the prior conversation re-read each turn &mdash; recycled context,
charged at only 0.1x and not what drives your rate limit. Shown separately for that reason.</p>

<h2>Cost per day &mdash; by model</h2>
<div class="card">{chart1}{leg1}</div>

<h2>Tokens per day &mdash; real work (excluding cache reads)</h2>
<div class="card">{chart2}{leg2}
<p class="note">Output = tokens written by Claude (the most expensive category and the basis of
rate limits). Cache reads are separate below &mdash; they dominate volume but cost only 10%.</p></div>

<h2>Cache reads per day &mdash; reused context</h2>
<div class="card">{chart3}
<p class="note">Every conversation turn re-reads the prior history from cache.
High values = long sessions, not high cost.</p></div>

<h2>Time-of-day profile &mdash; when do you spend the most?</h2>
<div class="card">{chart_hours}</div>

<h2>By model</h2>
<div class="card">{model_table}</div>

<h2>By project</h2>
<div class="card">{proj_table}
<p class="note">Subagent share of total cost: {side_pct:.0f}% (main chat {100 - side_pct:.0f}%).</p></div>

<h2>Top sessions by cost</h2>
<div class="card">{sess_table}</div>

<p class="note" style="margin-top:32px">Data source: ~/.claude/projects/**/*.jsonl &middot;
Claude Code deletes transcripts after ~30 days &mdash; this dashboard caches the aggregates
permanently, so history grows from now on. Dedupe over message/request ID.
Prices: Fable $10/$50 &middot; Opus 4.5+ $5/$25 &middot; Sonnet $3/$15 &middot; Haiku $1/$5 per 1M tokens;
cache writes 1.25-2x, cache reads 0.1x the input price.</p>
</div></body></html>"""


def main():
    print("Scanning transcripts ...", flush=True)
    cache = load_cache()
    n_new = scan(cache)
    print(f"  parsed {n_new} new/changed files, "
          f"{len(cache['files'])} total in cache.", flush=True)
    save_cache(cache)

    print("Aggregating ...", flush=True)
    agg = aggregate(cache)
    # Flip daily_model_cost: model -> {day: cost} (for chart layers)
    by_model = defaultdict(dict)
    for day, mc in agg["daily_model_cost"].items():
        for m, c in mc.items():
            by_model[m][day] = c
    agg["daily_model_cost_by_model"] = by_model

    html = build_html(agg)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    HTML_FILE.write_text(html, encoding="utf-8")
    print(f"Dashboard: {HTML_FILE}")

    if "--open" in sys.argv:
        if sys.platform == "darwin":
            os.system(f"open '{HTML_FILE}'")
        elif sys.platform.startswith("linux"):
            os.system(f"xdg-open '{HTML_FILE}' >/dev/null 2>&1 &")
        else:
            os.system(f'start "" "{HTML_FILE}"')


if __name__ == "__main__":
    main()
