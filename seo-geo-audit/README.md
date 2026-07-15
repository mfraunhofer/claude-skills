# seo-geo-audit

Audit and optimize a website for classic SEO **and** GEO (generative-engine optimization: visibility and citability in ChatGPT search, Perplexity, Google AI Overviews) in one workflow. Measure first, then implement, ordered strictly by effort vs. payoff.

## Install

```bash
npx degit --force mfraunhofer/claude-skills/seo-geo-audit ~/.claude/skills/seo-geo-audit
```

## Usage

Say "run an SEO/GEO audit for example.com" or "is example.com AI-search ready?". The workflow:

1. **Audit**: `scripts/audit.sh <domain>` checks the live site deterministically (robots/crawler policy, soft-404, sitemap, headers, schema presence, render-blocking JS, canonical). In parallel: keyword strategy, competition, off-site footprint.
2. **Optimize**, in phases: clean re-deploy and a real 404 first, then WebP images and JSON-LD schema, then dedicated landing pages per keyword cluster, then the off-site/local plan (Google Business Profile, reviews, NAP consistency).
3. **Verify**: the audit's acceptance criteria re-checked as curl probes against the live site.

## The one GEO distinction that matters

Training bots and search bots are not the same thing. Block all AI bots and you drop out of AI search; block only training bots (GPTBot, Google-Extended, CCBot, ...) and you stay citable through the search/grounding bots (OAI-SearchBot, PerplexityBot, Claude-SearchBot, ...). The bundled [robots.txt template](references/robots.txt.template) encodes that policy.

## Iron rules

Never invent facts for schema or copy (a fabricated star rating is a manual-action risk), always verify against the deployed site instead of the repo, and keep strategic forks (crawler policy, landing pages vs. single page) as human decisions.

## Files

| File | Purpose |
|---|---|
| [SKILL.md](SKILL.md) | Full workflow spec, phases, rules |
| [scripts/audit.sh](scripts/audit.sh) | Deterministic technical audit (curl-based) |
| [scripts/to-webp.sh](scripts/to-webp.sh) | Responsive WebP conversion via ffmpeg |
| [scripts/validate-schema.py](scripts/validate-schema.py) | Extracts and validates all JSON-LD blocks |
| [references/robots.txt.template](references/robots.txt.template) | GEO-positive robots policy |
| [references/llms.txt.template](references/llms.txt.template) | Optional llms.txt |
