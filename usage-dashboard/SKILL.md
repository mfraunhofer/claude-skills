---
name: usage-dashboard
description: Local token-usage dashboard for Claude Code. Parses all session transcripts (~/.claude/projects/**/*.jsonl), aggregates usage per day / model / project / session / time-of-day / main-chat-vs-subagent, and renders a self-contained HTML dashboard with a USD cost equivalent (API list prices). Use when you want to see how much you've spent, what a day/project/model cost, or your token usage over time. NOT for the rate-limit status line (the harness renders that itself).
---

# Usage Dashboard

One command, no setup:

```bash
python3 ~/.claude/skills/usage-dashboard/scripts/build_dashboard.py --open
```

Builds `~/.claude/cache/usage-dashboard/index.html` and opens it in your browser.
Without `--open` it only builds the file.

## What it shows
- **KPIs:** cost today / 7 days / 30 days / avg per day / total, plus tokens (30d)
- **Cost per day** stacked by model (Opus / Fable / Sonnet / Haiku)
- **Tokens per day** (output / input / cache writes) — cache reads shown separately, because they dominate the volume but cost only 0.1x
- **Time-of-day profile** (when you spend the most)
- **Tables:** per model, per project (incl. subagent share), top 15 sessions

"Cost" = the API list-price equivalent in USD. If you're on a flat-rate plan, the number is the value you're getting out of the subscription, not a bill.

## How it works
- **Data source:** every `assistant` line in the transcripts carries `message.usage` (input / output / cache_creation 5m+1h / cache_read), `model`, `timestamp` (UTC), `sessionId`, `isSidechain` (subagent), and the project = top-level folder name. Subagent transcripts are nested (`<session>/subagents/agent-*.jsonl`), so the scan is **recursive** (`rglob`).
- **Dedupe:** over `(message.id, requestId)` — streamed responses appear as several JSONL lines with identical usage; without dedupe you'd double-count.
- **Cache = long-term history:** `~/.claude/cache/usage-dashboard/cache.json.gz` stores per-file records (mtime/size check → incremental, later runs take seconds). Claude Code **deletes transcripts after ~30 days** — entries for deleted files stay in the cache (`archived: true`), so your history grows from first install onward. Never delete the cache, or everything older than 30 days is gone.
- **Prices** (`PRICING` in the script): Fable 10/50 · Opus 4.5+ 5/25 · Opus 4.0/4.1 15/75 · Sonnet 3/15 · Haiku 1/5 USD per 1M tokens. Cache writes 5m = 1.25x input, 1h = 2x input, cache reads = 0.1x input. For a new model, add a line at the top of `PRICING` (substring match, order = priority) — costs are recomputed from raw tokens on every run, so price changes apply retroactively.
- `<synthetic>` models (error placeholders) are filtered out.

## Time zone
Day bucketing and the time-of-day chart use your system local time zone. Override with the `TZ` env var, e.g. `TZ="America/New_York" python3 .../build_dashboard.py`.

## Notes
- The first run scans every transcript (can be a couple of GB) — a line prefilter (`'"usage"' in line`) before `json.loads` keeps it to ~2 min; later runs use the mtime/size cache and finish in seconds.
- Recursive scanning is required: a flat `<project>/*.jsonl` scan misses every subagent transcript.
