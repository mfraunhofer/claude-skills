# handover

Continue long chats in fresh sessions without losing state. When a chat gets too long (or you want to pick the work up tomorrow), the skill writes a structured handover file. In the next session, one sentence ("find the handover about the checkout redesign") loads it back.

## Install

```bash
npx degit --force mfraunhofer/claude-skills/handover ~/.claude/skills/handover
```

## Usage

Two modes, both triggered by plain language:

- **Create**: "/handover", "write me a handover", "let's continue tomorrow". Writes `~/.claude/handoffs/YYYY-MM-DD-<topic-slug>.md` with goal, current state, open steps, touched files, and context notes. The topic slug is the search anchor.
- **Search**: "find the handover where we discussed X", "didn't we talk about Y last week?". Finds the file by name or content and continues from its open steps.

Handover files older than 30 days are cleaned up automatically on every run.

## Design choices

No index file (filename search + grep is enough below ~50 files), no auto-trigger (the skill never runs on its own), and sensitive data (credentials, tax IDs, keys) is stripped by rule. Full spec in [SKILL.md](SKILL.md).
