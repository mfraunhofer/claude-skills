---
project: <PROJECT-NAME>
state-file-version: 1
created: <YYYY-MM-DD>
last-updated: <YYYY-MM-DD>
current-phase: <e.g. Phase 1 — Skeleton>
current-wave: <e.g. Wave 3 — Backend>
next-wave-candidate: <e.g. Design migration>
---

# <PROJECT> PM State

Single source of truth for the PM chat. **When a new PM chat starts: read this file in full first, then answer.**

## How you + the PM chat work

**Core principle:** the PM chat does ONLY project management — maintain state, give the overview, write instructions. Code edits, issue thinking, research and status-sync edits run in **spawn chats** (which the PM chat prepares as prompt text; you open the new chat).

1. You kick off issues in their own chats (spawn-chat pattern).
2. When a spawn/issue chat is done, you paste its closing report into the PM chat.
3. The PM chat updates this file (active table + worktree section + logbook) and names the next action.
4. The PM chat actively says "you can close the chat for issue X" once the PR is merged + the worktree is empty.

**What the PM chat does itself:** maintain pm-state.md · recap · high-level wave plan · cleanup commands as text · spawn prompts as text.

**What the PM chat NEVER does** (belongs in spawn chats): edit issue files / index files / code · research · TDD / implementation / audits / reviews · dig deep into issue contents.

## Legends

**Priority:** `1` today · `2` this week · `3` later · `—` no action

**Status:**

| Code | Meaning | Action |
|---|---|---|
| `todo` | Not started | yes |
| `doing` | Chat running, code in a worktree | yes |
| `review` | PR open, review running | yes |
| `ci` | CI running / waiting for green | yes |
| `merge-ready` | All green, just the merge click | yes |
| `merged` | Code in, bookkeeping open | yes |
| `done` | Truly everything done — no action left | `—` |
| `blocked` | Waiting on something else | yes |
| `manual` | Waiting on a human action | yes |
| `(chore)` | Maintenance task without an issue number | yes |

**PR:** `—` · `draft` · `open` · `red` · `ready` · `merged` · `closed`

**Action classes:**
- `You: …` — hands-on (terminal, browser, click-test, merge click, opening a new chat)
- `PM: …` — PM chat inline (maintain state, recap, command text, spawn-prompt text)

**Trigger phrases:**

| User says… | PM chat… |
|---|---|
| "recap" / "status?" / "where are we?" | gives a recap |
| "cleanup" / "clear everything" / "phase X GO" | builds a cleanup command |
| "prompt for #N" / "spawn prompt for …" | builds a spawn prompt |
| "wave plan" / "next wave" | proposes a wave plan |
| (report from a spawn chat) | updates state + names the next step |

---

## Current wave: <NAME>

**Goal:** <WHAT-THIS-WAVE-SHOULD-FINISH>

### Active table

| Prio | # | Title | Status | PR | Action |
|---|---|---|---|---|---|
| 1 | 01 | <issue title> | `todo` | `—` | **You:** … |

### Worktree section

| Worktree | Branch | PR |
|---|---|---|
| … | … | … |

### Blockers / risks

- …

### Next up (after this wave)

Wave candidate: <NAME>.

---

## Phase-X done

| # | Issue | PR / when |
|---|---|---|

---

## Wave log

| Wave | Goal | Start | End | Outcome |
|---|---|---|---|---|

---

## Logbook

| Date | Event |
|---|---|
| <YYYY-MM-DD> | State file created. |
