# pm

A two-layer PM workflow for working with Claude on complex projects in parallel chats.

1. **PM chat**: keeps the overview, maintains a state file, plans the next wave of work, and hands out short dispatch prompts. It never touches code.
2. **Spawn chats**: do the actual work (code, research, TDD) and always report back through a shared **PM inbox** (`.scratch/pm-inbox/*.md`).

That one-way channel (spawn → inbox → PM) keeps the overview correct without inflating the PM chat's context. State lives in `.scratch/pm-state.md` with a status legend (`todo` / `doing` / `review` / `merged` / `done` / `blocked` / `manual`) and per-item actions.

## Install

```bash
npx degit --force mfraunhofer/claude-skills/pm ~/.claude/skills/pm
```

## Usage

In the PM chat: "status?", "recap", "inbox", "wave plan", "dispatch #12". The PM chat resyncs itself from ground truth on start (`gh pr list`, `git log`, worktrees, inbox files) instead of trusting its own notes.

When work needs file edits, the PM chat produces a minimal dispatch prompt that points at an issue file and requires the inbox report. You paste it into a new chat; the spawn chat executes and reports back.

## The "box" shortcut (optional hook)

Typing `box <project>` in any chat, regardless of working directory, drops Claude straight into PM mode for that project: it reads the project's `pm-state.md` plus the active inbox reports and answers with a compact status and the one next step. A bare `box` infers the project from the conversation and asks when unclear.

Bundled as [hooks/box-pm.sh](hooks/box-pm.sh):

1. Copy it to `~/.claude/hooks/box-pm.sh` and `chmod +x` it.
2. Edit the `PROJECTS` map at the top (one `name:path` pair per project).
3. Register it in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [{ "type": "command", "command": "~/.claude/hooks/box-pm.sh" }] }
    ]
  }
}
```

The hook fires only on exactly `box` or `box <known-project>` ("boxing" or "box status" do not fire), so it stays out of the way in normal chats. Requires `jq`.

## Files

| File | Purpose |
|---|---|
| [SKILL.md](SKILL.md) | Full spec: state-file schema, legends, inbox pattern, dispatch prompts |
| [templates/pm-state-template.md](templates/pm-state-template.md) | Starting template for `.scratch/pm-state.md` |
| [hooks/box-pm.sh](hooks/box-pm.sh) | Optional `box <project>` hook |
