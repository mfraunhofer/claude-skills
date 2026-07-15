---
name: pitch
description: Lightweight pre-planning skill that turns a fuzzy idea into a structured Feature Pitch (pitch.md) before any deeper planning or PRD step runs. Asks 6 questions one at a time with adaptive multiple-choice anchors, then writes the pitch file. Use when the user says "/pitch", "I have an idea for", "let's pitch this", "new feature idea", "I want to build", or whenever a software idea needs to be shaped before a domain/spec review. NOT for full PRDs, abstract strategy, or ideas that already have a detailed spec.
argument-hint: "A one-line idea (optional)"
---

## What this skill does

Asks 6 questions: one at a time, with multiple-choice anchors drawn from the project context, and then writes a `pitch.md`. That file is the input for your next planning step (a domain/spec review, a PRD, or a companion skill like `grill-with-docs` if you use one).

**Why not jump straight to planning?**
A planning/spec step can only challenge something once there's something to challenge. Without a pitch, the first half of the session goes to figuring out *what* should even be built. The pitch separates "what do we want" from "does it fit our domain model".

---

## Flow

### Step 1: Load context

Before the first question:
- Read `CONTEXT.md` in the current project (or `CONTEXT-MAP.md` if present): it supplies the actors for Q2 and the out-of-scope suggestions for Q5.
- Read `docs/adr/` if present: it supplies no-go candidates for Q6.
- If no project context is detectable: use the defaults (see [references/defaults.md](references/defaults.md)).

### Step 2: Ask the 6 questions

**Always:** one question per message. Name a recommendation. Confirm before moving on.

**Q1: The problem**
> "What's the concrete problem? Describe a situation, not a feature."
- No multiple choice: free text.
- If the answer is too abstract ("users are confused"): dig in with "Show me a concrete situation: who's doing what, and what goes wrong?"

**Q2: Audience**
> "Who is this for, who hits this problem?"
- Generate MC options from the actors in CONTEXT.md.
- If no CONTEXT.md: End user / Admin / Internal team / Multiple.
- Always: "+ Other (free text)" as the last option.

**Q3: Rough solution**
> "What's your rough idea for the solution? 2–3 sentences, no wireframe."
- No MC: free text, with a starter: "Imagine you're explaining it to someone at a whiteboard in 30 seconds."
- If the answer is too precise (user stories, DB schema): stop and say "That's already PRD-level: save it for the planning step. Rougher, please."

**Q4: Scope of the first version**
> "How built-out should the first version be?"
- MC:
  - **MVP**: fastest version that solves the problem, technical debt knowingly accepted
  - **Polished**: production-ready, all edge cases
  - **Undecided**: not settled yet

**Q5: Out of scope**
> "What's explicitly NOT part of this: things that might seem adjacent but aren't coming yet?"
- MC suggestions from CONTEXT.md: things marked there as "out of scope" or "phase X".
- Always include a free-text option.
- Recommendation: "I'd suggest [X from CONTEXT.md] as out of scope, because the phase plan puts it in phase Y."

**Q6: No-goes**
> "What's an absolute no-go, something that must under no circumstances be part of this solution?"
- MC candidates from ADRs (rejected alternatives) + known constraints.
- If no ADRs: compliance notes (GDPR, etc.), hard technical limits.
- Always include a free-text option.
- May be left empty, then drop the section from pitch.md.

### Step 3: Write pitch.md

Right after Q6: no further questions.

**Location:** `docs/pitches/pitch-YYYY-MM-DD-<slug>.md` in the project root.
If `docs/pitches/` doesn't exist: create it lazily.
If no project root is detectable: the current directory.

Slug = 3–4 words from the problem, kebab-case.

**Format:** see [references/pitch-template.md](references/pitch-template.md)

### Step 4: Handoff

After writing:
```
pitch.md is at docs/pitches/pitch-YYYY-MM-DD-<slug>.md.

Next step: hand it to your planning/spec step (a domain review, a PRD, or the
grill-with-docs skill if you use one), point it at that file.
```

---

## Edge cases

**User runs /pitch with text:** e.g. `/pitch I want SMS reminders for bookings`
→ Take that text as pre-context for Q1, but still ask Q1 and confirm.

**User already has a pitch.md:** ask whether to update it or start a new version.

**No CONTEXT.md present:** use defaults for Q2 + Q5 (see [references/defaults.md](references/defaults.md)). Note in the output: "No CONTEXT.md found: actors and out-of-scope suggestions are defaults."

**User skips a question:** ask once more. If still no input: leave the section empty and mark it in pitch.md as `_Not answered: resolve during planning_`.
