# Claude Skills

A small collection of reusable [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) for Claude Code (and any other Claude surface that loads skills).

Each skill is a self-contained folder with a `SKILL.md`. Claude loads it automatically when the task matches the skill's description — no configuration, no glue code.

## Skills

| Skill | What it does |
|---|---|
| [`handover`](./handover) | Write a handover file when a chat gets too long or you want to continue in a fresh session — and search past handovers when you remember an earlier topic. |

## Install

Copy any skill folder into your personal skills directory:

```bash
# personal (available in every project)
cp -r handover ~/.claude/skills/

# or project-scoped (checked into a single repo)
cp -r handover .claude/skills/
```

That's it. Start a new Claude Code session and the skill is live — trigger it with the phrases listed in its `SKILL.md` description (e.g. `/handover`).

## License

[MIT](./LICENSE) © Max Fraunhofer · [mfraunhofer.de](https://mfraunhofer.de)
