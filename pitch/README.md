# pitch

Turn a fuzzy idea into a structured feature pitch before any deeper planning runs. Six questions, one at a time, with multiple-choice anchors drawn from your project context. The result is a `pitch.md` your next planning step (a PRD, a domain review) can actually challenge.

## Install

```bash
npx degit --force mfraunhofer/claude-skills/pitch ~/.claude/skills/pitch
```

## Usage

Say "/pitch", "I have an idea for ...", or "I want to build ...". The skill walks through:

1. The problem (a concrete situation, not a feature)
2. Audience (options generated from your `CONTEXT.md` if present)
3. Rough solution (whiteboard level, it pushes back if you get too detailed)
4. Scope of the first version (MVP / polished / undecided)
5. Out of scope
6. No-goes (candidates pulled from your ADRs if present)

Then it writes `docs/pitches/pitch-YYYY-MM-DD-<slug>.md` and hands off to your planning step.

## Why a pitch before a PRD

A planning step can only challenge something once there is something to challenge. Without a pitch, the first half of a planning session goes to figuring out what should even be built. Full spec in [SKILL.md](SKILL.md), templates in [references/](references/).
