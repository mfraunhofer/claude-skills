---
name: seo-geo-audit
description: Audit + optimize a website for classic SEO AND GEO (generative-engine / AI-search visibility) in one combined workflow. It audits the LIVE site (crawl headers, robots/crawler-policy, soft-404, sitemap, schema, Core-Web-Vitals signals) plus keyword/competitor/AI-readiness research, then IMPLEMENTS the fixes — clean re-deploy, a real 404, a training-vs-search-bot robots policy, image to WebP, JSON-LD schema (LocalBusiness/Service/GeoCircle/sameAs/AggregateRating), topic/service landing pages, sitemap + internal links, a de-AI humanizer pass on all generated copy, and an off-site/local action plan. Use when the user says "/seo-geo-audit", "run an SEO/GEO audit for <domain>", "audit the SEO of <site>", "optimize <site> for Google and AI search", "is <site> AI-search ready / will it get cited in ChatGPT/Perplexity", "why doesn't <site> rank (locally)", "GEO audit", "get <site> into AI search". NOT for — pure copywriting, pure performance profiling without SEO, or writing a single article.
argument-hint: "<domain-or-workspace> (e.g. example.com) — what should be audited/optimized?"
---

# seo-geo-audit

A combined **audit → optimization** workflow for classic SEO **and** GEO (Generative Engine Optimization — visibility and citability in ChatGPT search, Perplexity, Google AI Overviews, Claude). Measure first, then build. Both in one skill, because an audit without implementation is just a PDF, and implementation without an audit is blind.

**Guiding principle:** the biggest quick wins are often **not in the code** — they are (a) a clean deploy, (b) two crawler settings, and (c) off-site (for a local business: Google Business Profile + reviews). Website code is polish on top. So order everything strictly by **effort vs. payoff**.

## Iron rules (non-negotiable)

1. **Never invent facts.** `AggregateRating`, review counts, certifications, prices, awards, founding dates — only put them in schema/copy with a **verified** source. A fabricated star rating is a Google manual-action risk. Prefer an empty field (`sameAs: []`, no `AggregateRating`) over a wrong one.
2. **Always run generated copy through a de-AI / humanizer pass** before deploy (strip AI tells; target **zero em-dashes** `—`, deterministically verified). If the copy is in a personal/brand voice, apply that voice on top; for white-label client copy, do **not** impose your own voice — the client brand has its own.
3. **The live site is the truth.** Always `curl` the **deployed** page; don't assume the repo state — production is often a stale deploy. `WebFetch` is frequently blocked by bot protection (e.g. Cloudflare) → use `curl` with a header (`-I`, `-A`).
4. **Read the current file fresh from disk, change additively.** Sites are often touched in parallel sessions.
5. **Training bots ≠ search bots.** The single most important GEO distinction (see Phase 0.2). Block all AI bots and you drop out of AI search; block only training bots and you stay citable.

## Workflow

### Step A — Audit (measure)

Run `scripts/audit.sh <domain>` — the deterministic technical part (curl-based): crawl headers, robots.txt + crawler policy, soft-404 test, sitemap.xml (status + content-type), schema presence, render-blocking JS, image sizes, canonical/www behavior. It prints a findings table you triage into P0/P1/P2.

In parallel (a research agent / web search) handle the **non-technical** part:
- **Keyword strategy**: what should the site *naturally* be found for? For a local business: **geo rings** (Ring 1 neighborhood/district = top priority, Ring 2 adjacent districts, Ring 3 wider region only for premium/specialist services). Combine every service/topic term with a location modifier. Deliberately do NOT chase: generic head terms without conversion, competitor brand names, or terms the offering can't honestly serve.
- **Competition**: who ranks for the head terms, and where a small player wins (hyperlocal terms, quality differentiation, thin competitor schema).
- **GEO/AI readiness**: are the search/grounding bots allowed? Is there FAQ/structured content an LLM can extract?
- **Off-site footprint** (the biggest lever for a local business): is there a **Google Business Profile**? Reviews (count/average/recency)? NAP consistency across directories? **Never skip this strand** — it beats on-site for local queries. Use a research agent to find the real profiles; invent nothing — "not found" is a valid result.

Write the audit as Markdown (`docs/seo-geo-audit-<date>.md`): executive summary + findings table (severity / where it's fixed) + keyword clusters + off-site status + prioritized plan + product decisions for the human.

### Step B — Optimization (build), strictly by effort vs. payoff

**Phase 0 — Crawlability foundation (hours, P0).** Highest immediate impact.
- **Clean re-deploy.** Production is often stale. Remove dead asset references (404'ing scripts), redeploy, verify live.
- **Kill soft-404s.** Does an unknown URL (`/zzz`) return HTTP 200 + the homepage? → establish a real 404. On static hosts (Cloudflare Pages, Netlify) add a **`404.html`** to the repo (served with a real 404 status for unknown routes) **and** make sure no SPA catch-all (`/* /index.html 200`) is active. Verify: `curl -I .../zzz` → 404, `/sitemap.xml` → 200 `application/xml`.
- **Crawler policy (robots.txt).** Target default: **block training bots, allow search/grounding bots, allow classic search engines.** Template in `references/robots.txt.template`. Training-only (no loss of citability): GPTBot, ClaudeBot, Google-Extended, CCBot, Bytespider, Amazonbot, Applebot-Extended, meta-externalagent. Real-time search/grounding (MUST be allowed for AI citations): OAI-SearchBot, ChatGPT-User, PerplexityBot, Perplexity-User, Claude-SearchBot, Claude-User. Allow Googlebot/Bingbot under `*` (Google AI Overviews feeds from the normal Googlebot, not Google-Extended).
  - **Cloudflare gotcha:** Cloudflare's "Managed robots.txt" does **not** overwrite your deployed file — it prepends its managed block and appends your file. The managed block only blocks training bots, never search bots. → After deploying a correct repo robots.txt the policy is often already right, with no dashboard change. For a single clean file, disable Managed robots.txt in the dashboard.

**Phase 1 — Performance + Schema (days, P1).**
- **Images → WebP/AVIF.** `scripts/to-webp.sh <image> [widths…]` (ffmpeg/libwebp). Responsive hero (`<picture>` + `srcset` 1024/1600), target < 150 KB, set `width`/`height` (CLS), `loading="lazy"` below the fold, `fetchpriority="high"` + preload (on the WebP) for the LCP hero.
- **Render-blocking JS** out of the critical path: defer or lazy-load heavy/unused scripts (check it's actually used first).
- **Schema (JSON-LD).** For a local business: `LocalBusiness` (or an industry subtype) with full NAP/geo/opening-hours/offers. **`areaServed` as a `GeoCircle`** (midpoint = location, radius). One **`Service`** node per core service (`serviceType`, `areaServed`, `url` → landing page, `provider` ref). Fill **`sameAs`** with real profile URLs (GBP place URL, social) — **the single most valuable move for entity/AI linking**. **`AggregateRating`** only with real numbers. Keep `FAQPage` (rich-snippet deprecated, but ideal for LLM extraction + page understanding). Validate every JSON-LD block with `scripts/validate-schema.py <file>` (note: HTML entities are NOT decoded inside `<script>` JSON-LD — use plain `&`, not `&amp;`, in JSON strings).
- **www→apex / canonical** clean. A per-page canonical already mitigates duplicate content; a 301 www→apex is cleaner (often a host dashboard setting; via API only with a ruleset-scoped token).

**Phase 2 — Content architecture: topic/service landing pages (weeks, P2).** The structurally most important move for durable ranking/citation: turn ONE page into **dedicated URLs per keyword cluster**. ~300–600 words each, own `Service` + `BreadcrumbList` (+ optionally `FAQPage`) schema, internal links from the homepage and to each other, every new URL added to the real `sitemap.xml`. With many shared components, use a **shared, decoupled stylesheet** for the landing pages (no rebuild of the main site, brand-consistent). Derive copy only from verified site statements (rule 1) and run it through the humanizer (rule 2).

**Phase 3 — Off-site / local (ongoing, P1 for the business, mostly outside the repo).** For a local business this is **the** lever — it beats on-site for "near me" queries and drives AI local citations:
1. **Google Business Profile** fully built out (categories, exact NAP, exact hours, all services, photos, Q&A, posts). If none exists, creating it is the #1 action.
2. **Review system** (direct link after each job, reply within 48 h, encourage customers to name the service + location).
3. **NAP consistency** across directories (Google, Bing Places, Apple Business Connect + local directories) — exactly identical spelling.
4. **Close the entity graph**: GBP place URL ↔ website `sameAs` ↔ directories.
Record as an action doc (`docs/...-offsite.md`) + bundle the data only a human can provide (GBP URL, real review numbers) into one explicit ask — don't guess.

### Step C — Verify + report
After deploy, check live (the audit's acceptance criteria as curl checks): `/zzz`→404, sitemap 200 XML, robots correct, landing pages 200 + schema, hero WebP < 150 KB, internal links present. Report to the human in practical terms (what changes for the business/customer), not in code jargon — and list the manual/data-gated remainders (dashboard redirect, GBP, real numbers) as clear, bundled to-dos.

## Product decisions belong to the human
SEO/GEO is full of forks that are strategic, not technical: single page or landing pages? AI-crawler policy? own GBP or ride a sister brand? change the booking flow? → Present each as a multiple-choice **with a recommendation**; don't decide autonomously. The skill decides the technical forks itself.

## Bundled helpers
- `scripts/audit.sh <domain>` — deterministic technical audit (curl): robots/crawler policy, soft-404, sitemap, headers, schema presence, render-blocking, canonical/www.
- `scripts/to-webp.sh <image> [widths]` — responsive WebP via ffmpeg.
- `scripts/validate-schema.py <html-or-url>` — extracts + validates all JSON-LD blocks, lists `@type`.
- `references/robots.txt.template` — GEO-positive robots template (block training, allow search).
- `references/llms.txt.template` — optional `llms.txt` (low priority in 2026; schema + content + GBP matter more).

## Self-anneal
New crawler UAs, new schema types, new host gotchas, new AI-search factors → update this SKILL.md. GEO moves fast; the bot lists and the "what drives AI citations" ordering go stale.
