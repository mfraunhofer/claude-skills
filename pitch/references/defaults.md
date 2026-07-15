# Defaults when no project context is present

Used when no `CONTEXT.md` and no recognizable project root is found in the cwd tree.

## Q2: Audience (default MC options)
- End user
- Admin / operator
- Internal team
- Multiple actors

## Q5: Out of scope (default suggestions)
No CONTEXT.md, so no context-specific suggestions are possible.
→ Offer free text only. Note in chat: "No CONTEXT.md found: please enter manually what shouldn't be part of this version."

## Q6: No-goes (default candidates)
- Storing personal data without a legal basis (GDPR)
- External API dependencies without a fallback (when reliability is critical)
- → free text

## Output header note

If defaults were used, write this at the top of pitch.md:

```
> ⚠️ No CONTEXT.md found. Actors and out-of-scope suggestions are generic defaults.
> Your planning step should establish the project's CONTEXT.md.
```
