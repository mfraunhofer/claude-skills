# usage-dashboard

A local token-usage dashboard for Claude Code. Parses all session transcripts on your machine, aggregates usage per day, model, project, session, time of day, and main-chat vs. subagent, and renders a self-contained HTML dashboard with a USD cost equivalent (API list prices). No server, no upload, everything stays local.

## Install

```bash
npx degit --force mfraunhofer/claude-skills/usage-dashboard ~/.claude/skills/usage-dashboard
```

## Usage

One command, no setup:

```bash
python3 ~/.claude/skills/usage-dashboard/scripts/build_dashboard.py --open
```

Builds `~/.claude/cache/usage-dashboard/index.html` and opens it in your browser.

## What it shows

- Cost today / 7 days / 30 days / average per day / total, plus tokens
- Cost per day stacked by model, tokens per day (output / input / cache writes)
- Time-of-day profile, tables per model and per project (incl. subagent share), top sessions

If you are on a flat-rate plan, the USD number is the value you get out of the subscription, not a bill.

## Good to know

- The scan is recursive on purpose: subagent transcripts live nested under `<session>/subagents/`, a flat scan misses them.
- Streamed responses appear as several transcript lines with identical usage; the script dedupes over `(message.id, requestId)` so nothing is double-counted.
- Claude Code deletes transcripts after ~30 days. The dashboard keeps its own cache (`cache.json.gz`), so your history grows from first install onward. Don't delete the cache.
- Prices live in a `PRICING` table at the top of the script; costs are recomputed from raw tokens on every run, so price updates apply retroactively.

Full details in [SKILL.md](SKILL.md).
