---
project: <PROJECT-NAME>
state-file-version: 1
created: <YYYY-MM-DD>
last-updated: <YYYY-MM-DD>
current-phase: <e.g. Phase 1: Skeleton>
current-wave: <e.g. Wave 3: Backend>
next-wave-candidate: <e.g. Design migration>
---

# <PROJECT> PM State

Single source of truth for the PM chat. **When a new PM chat starts: read this file in full first, then answer.**

## How you + the PM chat work

**Core principle:** the PM chat does ONLY project management: maintain state, keep the overview, write the next wave, and hand out dispatch prompts. All real work (code, issue thinking, research) runs in **spawn chats**, which always report back through the **PM inbox** (`<workspace>/.scratch/pm-inbox/`).

1. The PM chat plans and writes the next wave directly, a queue of issues plus a short dispatch prompt for each.
2. You open each issue in its own spawn chat. The spawn chat does the work and writes its closing report to the **PM inbox**.
3. The PM chat reads the inbox, updates this file (active table + worktree section + logbook), and names the next action.
4. The PM chat actively says "you can close the chat for issue X" once the PR is merged + the worktree is empty.

**What the PM chat does itself:** maintain pm-state.md · recap · write the next wave (queue + dispatch prompts) · cleanup commands as text · read + integrate the PM inbox.

**What the PM chat NEVER does** (belongs in spawn chats): edit issue files / index files / code · research · TDD / implementation / audits / reviews · dig deep into issue contents.

## Legends

**Priority:** `1` today · `2` this week · `3` later · `–` no action

**Status:**

| Code | Meaning | Action |
|---|---|---|
| `todo` | Not started | yes |
| `doing` | Chat running, code in a worktree | yes |
| `review` | PR open, review running | yes |
| `ci` | CI running / waiting for green | yes |
| `merge-ready` | All green, just the merge click | yes |
| `merged` | Code in, bookkeeping open | yes |
| `done` | Truly everything done: no action left | `–` |
| `blocked` | Waiting on something else | yes |
| `manual` | Waiting on a human action | yes |
| `(chore)` | Maintenance task without an issue number | yes |

**PR:** `–` · `draft` · `open` · `red` · `ready` · `merged` · `closed`

**Action classes:**
- `You: …`: hands-on (terminal, browser, click-test, merge click, opening a new chat)
- `PM: …`: PM chat inline (maintain state, recap, command text, spawn-prompt text)

**Trigger phrases:**

| User says… | PM chat… |
|---|---|
| "recap" / "status?" / "where are we?" | gives a recap |
| "cleanup" / "clear everything" / "phase X GO" | builds a cleanup command |
| "prompt for #N" / "dispatch #N" | builds the dispatch (mini-)prompt pointing at the issue file |
| "wave plan" / "next wave" | writes the next wave directly (queue + dispatch prompts) |
| (report from a spawn chat) | updates state + names the next step |

---

## Current wave: <NAME>

**Goal:** <WHAT-THIS-WAVE-SHOULD-FINISH>

### Active table

| Prio | # | Title | Status | PR | Action |
|---|---|---|---|---|---|
| 1 | 01 | <issue title> | `todo` | `–` | **You:** … |

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
