# Claude Skills

A small collection of reusable [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) for Claude Code (and any other Claude surface that loads skills).

Each skill is a self-contained folder with a `SKILL.md`. Claude loads it automatically when the task matches the skill's description — no configuration, no glue code.

## Skills

| Skill | What it does |
|---|---|
| [`handover`](./handover) | Write a handover file when a chat gets too long or you want to continue in a fresh session — and search past handovers when you remember an earlier topic. |
| [`check-domain`](./check-domain) | Check whether a domain is available via a direct `whois` lookup against the official registrars (.de / .com / .eu / .org / .net). |
| [`usage-dashboard`](./usage-dashboard) | Local token-usage dashboard for Claude Code — parses your session transcripts and renders a self-contained HTML report with a USD cost equivalent. |
| [`pitch`](./pitch) | Turn a fuzzy idea into a structured Feature Pitch (pitch.md) via 6 guided questions, before any deeper planning or PRD step. |
| [`pm`](./pm) | Two-layer PM workflow — a PM chat that keeps the overview and writes the next wave, plus spawn chats that do all the work and report back through a shared PM inbox. The PM chat never touches code. |
| [`seo-geo-audit`](./seo-geo-audit) | Audit + optimize a website for classic SEO and GEO (AI-search visibility) in one workflow — live crawl/robots/soft-404/schema audit, then implements the fixes: real 404, training-vs-search-bot robots policy, WebP, JSON-LD, service landing pages, and an off-site/local plan. |

## Install

Grab a single skill straight into your personal skills directory — no clone, just that folder:

```bash
npx degit --force mfraunhofer/claude-skills/handover ~/.claude/skills/handover
```

Or clone the whole repo and copy what you want:

```bash
git clone https://github.com/mfraunhofer/claude-skills.git
cp -r claude-skills/handover ~/.claude/skills/      # personal — available in every project
# or: cp -r claude-skills/handover .claude/skills/   # project-scoped
```

That's it. Start a new Claude Code session and the skill is live — trigger it with the phrases listed in its `SKILL.md` description (e.g. `/handover`).

## License

[MIT](./LICENSE) © Max Fraunhofer · [mfraunhofer.de](https://mfraunhofer.de)
