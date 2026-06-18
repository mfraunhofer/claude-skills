---
name: pm
description: Project-management chat skill for running parallel issue/spawn chats. Tracks them through a state file (`<workspace>/.scratch/pm-state.md`). The PM chat is pure overview — it never edits files except pm-state.md itself; the spawn chats do the actual work. Use when the user says "/pm", "status [project]", "recap", "what's next?", "where are we on [project]?", "pm status", or pastes a report from a spawn/issue chat that triggers a status change. NOT for deep issue thinking, code edits, research, TDD, or reviews (all spawn-chat work).
---

# pm — Project-Management Dispatcher

## Core principle

On complex projects you work in **three chat layers in parallel**:

1. **PM chat** (this skill): maintains `<workspace>/.scratch/pm-state.md`, gives the overview, writes instructions. Stays open for a long time.
2. **Planner chat**: kicks off one wave/batch of work after another. Stays open.
3. **Spawn / issue chats**: do the actual work (code, edits, research, TDD). Short-lived, closed once the PR is merged.

**Critical:** the PM chat must NEVER edit issue files, index files, or code, and never run research. Otherwise its context balloons and the whole advantage is gone.

When a task needs file edits / code / research: the PM chat produces a **spawn prompt** as text output, the user drops it into a new chat tab, the spawn chat executes, and the user brings the report back.

## What the PM chat **may** do

- Edit `<workspace>/.scratch/pm-state.md`
- Read `<workspace>/.scratch/pm-inbox/*.md` and move them to `pm-inbox/_archive/`
- Give recaps / status synthesis in the chat
- Propose a wave plan at a high level (which issues, in what order)
- Produce cleanup commands as text output (the user pastes them into a terminal)
- Produce spawn prompts as text output (the user pastes them into a new chat)
- Run `gh pr list` / `git log` / `git worktree list` / `git branch` as a read-only source for auto-resync

## What the PM chat **never** does

- Edit issue files / index files / code (except pm-state.md itself)
- Research, web lookups, WebFetch
- TDD / implementation / audits / reviews
- Dig deep into issue contents ("what needs to go into issue 13")
- Detailed wave planning (that's the planner's job)

## State-file schema

Lives at `<workspace>/.scratch/pm-state.md`. Frontmatter:

```yaml
---
project: <name>
state-file-version: <int>
created: <date>
last-updated: <date>
current-phase: <text>
current-wave: <text>
next-wave-candidate: <text>
---
```

Sections:

1. **How you + the PM chat work** — core principle + may/may-not
2. **Legends** — priority, status, PR, action classes, trigger phrases
3. **Current wave** — active table + worktree section + blockers + next-up
4. **Phase-X done** — compressed list of finished issues (action always `—`)
5. **Wave log** — history of waves
6. **Logbook** — chronological PM events

Full template: `templates/pm-state-template.md`

## Legends

### Priority
`1` today · `2` this week · `3` later · `—` no action

### Status

| Code | Meaning | has action |
|---|---|---|
| `todo` | Not started | yes |
| `doing` | Chat running, code in a worktree | yes |
| `review` | PR open, review running | yes |
| `ci` | CI running / waiting for green | yes |
| `merge-ready` | All green, just the merge click | yes |
| `merged` | Code in, **but bookkeeping still open** | yes |
| `done` | Truly everything done — moves to the done list | **no** (`—`) |
| `blocked` | Waiting on something else | yes |
| `manual` | Waiting on a human action (test, click-test, decision) | yes |
| `(chore)` | Maintenance task without an issue number | yes |

**Rule:** status `done` means **no action left**. If anything is still open (e.g. a worktree lying around), it's `merged`, not `done`.

### PR

| Code | Meaning |
|---|---|
| `—` | no PR open |
| `draft` | draft, not ready |
| `open` | open, CI/review running, not ready |
| `red` | CI red or findings blocking |
| `ready` | all green, just the merge click |
| `merged` | done |
| `closed` | closed, not merged |

### Action classes

**`You:`** — the user does it hands-on (terminal, browser, click-test, merge click, opening a new chat).

**`PM:`** — the PM chat does it inline (maintain state, recap, cleanup-command text, spawn-prompt text).

When a task needs file edits / code / research: `You: open a spawn chat` with an accompanying `PM: produce the spawn prompt`.

### Trigger phrases

| User says… | PM chat… |
|---|---|
| "recap" / "status?" / "where are we?" | gives a recap based on the active table |
| "resync" / "what did I miss?" / "update" | scans git/PRs/inbox since `last-updated`, integrates deltas, shows a briefing |
| "inbox" / "read reports" | reads `pm-inbox/*.md`, integrates into state, archives |
| "report from the other chat" + a spawn-output quote | mandatory inbox check BEFORE answering (see inbox-polling rule) |
| "cleanup" / "clear everything" / "phase X GO" | builds a cleanup-command block |
| "prompt for #N" / "spawn prompt for …" | builds spawn-prompt text **with the inbox closing line** |
| "inbox snippet" | produces the boilerplate snippet for manually started chats |
| "wave plan" / "next wave" | proposes a high-level wave plan |
| (report from a spawn chat) | updates state + names the next step |

## Workflow

### When a PM chat starts

1. Read `<workspace>/.scratch/pm-state.md` in full.
2. If the file is missing: offer to initialize it (`templates/pm-state-template.md` as the template, reconstruct state from `gh pr list` + `.scratch/` files).
3. **Run an auto-resync** — scan external signals since `last-updated` from the frontmatter:
   - `gh pr list --state all --limit 30` — new PRs / status changes
   - `git log --since="<last-updated>" --oneline` — new commits on main
   - `git worktree list` — new/vanished worktrees
   - `<workspace>/.scratch/pm-inbox/*.md` (not `_archive/`) — spawn-chat reports
4. If there are deltas vs the active table: show them as a compact list, integrate into the state file, ask about anything unclear.
5. Give a short recap in the chat (priority-1 action first).

### Keep ground truth + repo hygiene in view (mandatory — PM core job)

Keeping the ACTUAL repo/deploy state in view is a PM core job. Two standing duties:

1. **Ground truth before assertions.** For any "is X deployed / merged / live?" statement, never quote the pm-state prose (it drifts) — query the source: `git log origin/main`, CI status, the production tip, live versions. Check first, then answer.
2. **Reconcile, don't append.** When integrating a deploy/merge/done report, also pull the load-bearing frontmatter fields (`current-phase`, `current-wave`, `next-wave-candidate`) up to the new state — not just a changelog line underneath. "Only append, fields go stale" is exactly what creates drift.

### When the user pastes a report from a spawn chat

1. **Check pm-inbox first** (see the inbox-polling rule) — the report may already be a file and the verbal note is just the teaser.
2. Identify which issue / task it concerns.
3. Update the state file (status, PR, worktree section if any).
4. If status moves to `done`: the entry moves out of the active table into the done list.
5. If cascading `blocked` rows clear: set them to `todo` and offer a spawn prompt.
6. If a worktree is empty (PR merged + bookkeeping done): actively say "you can close the chat for issue X, the worktree can go."
7. Name the next action in the chat.

### Inbox polling during a running session (mandatory)

Auto-resync at start is NOT enough. Spawn chats write reports while you + the PM chat run in parallel — the PM chat misses them if it doesn't poll the inbox periodically.

**Mandatory inbox check before every substantial PM answer** (recap, state update, spawn-prompt build). A `ls .scratch/pm-inbox/*.md` costs 50ms and blocks nothing. If a new file is there: read + integrate the report first, THEN answer — otherwise the answer is based on stale state.

What does NOT require a check: a status update the user mentions in passing (e.g. "I quickly verified F-18") — that gets maintained directly. The inbox check is only for reports FROM spawn chats.

### When a `PM:` trigger is called

Produce text output inline in the chat. No new chat needed.

### When an action needs file edits (spawn-prompt build)

Build a spawn prompt to this shape — **the inbox closing line is mandatory**:

```
You're working on the <project> repo. Working directory: <absolute-path>.

Task: <what to do, in 1-2 sentences>

Steps:
1. <step 1>
2. <step 2>
…

Acceptance:
- <criterion 1>
- <criterion 2>

Write your final report to:
<workspace>/.scratch/pm-inbox/<YYYY-MM-DD-HHMM>-<topic-slug>.md

with frontmatter:
---
topic: <short title>
issue: <issue no. or —>
pr: <pr no. after merge or —>
status: <merged | open | red | review | manual | done | blocked>
worktree: <path or —>
---
Body: 3-10 sentences on what was done + what's next.
```

The user drops it into a new chat, the spawn chat executes + writes the inbox report, and the PM chat reads it automatically on the next resync/trigger.

## PM-inbox pattern

So spawn-chat results don't have to be copy-pasted by hand, spawn chats write their final report to a file. The PM chat reads and archives it.

**Paths:**
- `<workspace>/.scratch/pm-inbox/` — new reports
- `<workspace>/.scratch/pm-inbox/_archive/` — processed reports

**File format:** `<YYYY-MM-DD-HHMM>-<topic-slug>.md`

**Processing on the `inbox` trigger or auto-resync:**
1. Read all `.md` files under `pm-inbox/` (not `_archive/`).
2. Per report: integrate into the active table (status, PR, worktree).
   - **Idempotency check:** if pm-state already tracks the issue correctly (same status, same PR no., history line exists), don't re-integrate — no second changelog line, no second version bump. Just archive and mark it as "already integrated" in the recap.
3. Move processed reports to `_archive/`.
4. Show a compact recap "N reports processed, status changes: …".

### Three ways spawn chats learn the inbox pattern

| Way | When |
|---|---|
| **A** — inbox closing line in the spawn prompt | when the PM chat builds the spawn prompt (default path) |
| **B** — boilerplate snippet handed over | when a chat was started without a PM-chat spawn prompt |
| **C** — auto-resync via git / PRs | catch-all for all uninstructed chats |

### Boilerplate snippet (way B)

On the `inbox snippet` trigger the PM chat produces:

```
Before you go: write a final report to
<workspace>/.scratch/pm-inbox/<YYYY-MM-DD-HHMM>-<topic-slug>.md

with frontmatter:
---
topic: <short>
issue: <no. or —>
pr: <no. or —>
status: <merged | open | red | review | manual | done | blocked>
worktree: <path or —>
---
Body: 3–10 sentences on what was done + what's open.
```

The user pastes that into an already-running spawn chat as the last instruction.

## Relation to other skills

| Skill | Role |
|---|---|
| `pm` (this) | **Dispatcher** — state file, overview, instructions |
| a planner | **Planner** — next wave as an issue list + copy-paste prompts |
| an executor | **Executor** — inner build/TDD loop per issue |
| a reviewer | **Reviewer** — plan stress-test against the domain |

## Safety rule

PM-chat context is expensive (long sessions). If you notice yourself starting file edits / research / deep thinking — STOP. That becomes a `You: open a spawn chat` with a spawn prompt. Better to spend 30 seconds writing a spawn prompt than 5 minutes inflating context.
