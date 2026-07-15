# pitch.md Template

```markdown
# Pitch: {Title: 4–6 words from the problem}
_Created: YYYY-MM-DD_

## Problem
{Concrete situation: who does what, what goes wrong. 2–4 sentences.}

## Audience
{Who hits the problem, from CONTEXT.md actors or free text.}

## Rough Solution
{Rough shape of the solution, 2–4 sentences. No wireframe, no user stories.}

## Scope
{MVP | Polished | Undecided}

## Out of Scope
{What is explicitly not part of this, comes later or never.}
- {Item 1}
- {Item 2}

## No-Goes
{Hard exclusion criteria: compliance, hard limits, rejected alternatives.}
- {Item 1}

---
_Next step: hand this file to your planning/spec step as the starting point._
```

## Output rules

- **Problem:** a story, not a feature description. "A dispatcher scrolls through 40 orders to find the 3 waiting for confirmation" is good. "Users need a better overview" is bad.
- **Rough Solution:** rough enough that the planning step still has something to challenge. No DB schema, no API endpoints.
- **Scope:** exactly one value: not "MVP with some polished parts".
- **Out of Scope:** only the explicit items from Q5, invent nothing.
- **No-Goes:** if Q6 was left empty → drop the section entirely, don't fill it with "none".
