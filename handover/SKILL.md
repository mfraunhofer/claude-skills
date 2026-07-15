---
name: handover
description: Write a handover file when a chat gets too long or you want to continue work in a fresh session, and search past handovers when you remember an earlier topic. Two modes: Create and Search. Use when the user says "/handover", "write me a handover", "this chat is getting too long, let's continue in a new one", "let's pick this up tomorrow", "I want to be able to continue this later". Search mode when the user says "find the handover where we discussed X", "didn't we talk about Y a few days ago, find that handover", "we had a handover about Z", "find last week's handover". NOT for permanent notes (use memory), project status, or plan files.
argument-hint: "What should the next session focus on? (optional)"
---

# Handover

Two modes: **Create** writes a new handover file. **Search** finds an old one.

Storage: `~/.claude/handoffs/`. TTL: 30 days. Self-cleaning.

## Pre-Run (always, both modes)

Before every run, drop anything older than 30 days. Keep the folder clean:

```bash
find ~/.claude/handoffs -name '*.md' -mtime +30 -delete 2>/dev/null
```

## Mode: Create

Trigger: "/handover", "write me a handover", "this chat is too long", "let's continue tomorrow", etc.

### 1. Filename

Format: `YYYY-MM-DD-<3-7-word-topic-slug>.md`

- Date: today
- Slug: from the chat's main topic. Lowercase, hyphens, no special characters.
- Good examples:
  - `2026-05-28-auth-refactor-oauth-migration.md`
  - `2026-05-28-checkout-flow-redesign.md`
  - `2026-05-28-postgres-rls-rollout.md`
- Bad examples (do NOT use):
  - `id-like-to-continue-tomorrow-vast-dijkstra.md` (auto-slug from the user's message)
  - `handover-2026-05-28.md` (no topic: not findable in Search mode)
  - `chat-summary.md` (generic)

The filename is the search anchor. If the user asks in 3 weeks "find the handover about the checkout redesign", the filename has to hit the topic.

### 2. Required structure

```markdown
---
date: YYYY-MM-DD
topic: [topic in 3-7 words]
status: [open|partial|done]
focus_next: [the user's argument if given, otherwise best inference]
---

# Handover: [Title]

## Goal of the next session
[1-3 sentences. What the follow-up chat should achieve. If the user passed an
argument (`/handover <text>`), work that in here.]

## Current state
[Bullet points of what happened in this chat. Narrative level, not file level,
Touched Files goes below separately.]

## Open / Next steps
[Concrete next steps in the order the follow-up chat should tackle them. Mark
blockers separately if there are any.]

## Touched Files
- `path/to/file.ext:line`: what was changed/created
- ...

(If nothing was edited: drop this section entirely.)

## Relevant Memory / Notes
- `[file.md]`: why it's relevant
- ...

(If you keep a memory/ directory or notes, point at the especially relevant files
here. Never duplicate their content, a pointer is enough.)

## Suggested Skills for the follow-up chat
- `skill-name`: what for
- ...

## Context notes
[Anything else. External URLs, background processes still running, decisions made
but not yet recorded anywhere, felt risks/uncertainties.]
```

### 3. Rules

- **No duplication:** If a PRD/plan/ADR/issue exists → link the path/URL, don't copy it.
- **Memory is the source of truth:** pointers are enough, never quote.
- **Strip sensitive data:** credentials, income figures, tax IDs, IBANs, API keys, secrets. If mentioned in the chat → do NOT mirror it into the handover. The handover is internal but keep it clean.
- **Plain text:** If the follow-up chat would take a wrong turn without a note, write it in. If not, leave it out.

### 4. Chat output

One line only. No summary, no "should I also":

```
Handover written → [2026-05-28-topic-slug.md](~/.claude/handoffs/2026-05-28-topic-slug.md)
```

The file is the documentation. If the user wants to see the content in chat, they'll ask.

## Mode: Search

Trigger: the user asks for an old handover ("find the handover where we discussed X", "didn't we talk about Y last week", "we had a handover about Z").

### 1. Search

First a filename match (fast, usually hits):

```bash
ls -t ~/.claude/handoffs/*.md
```

Then grep for the term in filename + content:

```bash
grep -lri "<search-term>" ~/.claude/handoffs/
```

### 2. Output by number of hits

**1 clear hit:** read the file, continue immediately. One line:

```
Loading handover [2026-05-15-topic.md](~/.claude/handoffs/2026-05-15-topic.md): state: [first open item from "Open / Next steps"]. Continuing.
```

Then work normally, as if continuing from the old chat.

**Multiple hits (show max 5):**

```
Several hits:
1. [2026-05-15-checkout-redesign.md](...): checkout flow redesign
2. [2026-05-22-pricing-model.md](...): pricing discussion
3. ...
Which one?
```

**No hit:**

If nothing in the last 30 days matches: say so honestly: "no handover found, it may have been older than 30 days and removed by the TTL cleanup". Ask what the user wants instead.

## Anti-Patterns

- **No index file:** No INDEX.md in the handover folder. Filename search + grep is enough below ~50 files. An index would just be extra trash.
- **No auto-trigger:** The skill NEVER runs on its own when a chat gets long. Only when the user explicitly invokes it.
- **No memory write:** The skill writes nothing into `memory/`. If a learning should persist long-term, the user asks for that separately.
- **No subagent spawn:** The skill is deterministic, no agent tool, no research.
