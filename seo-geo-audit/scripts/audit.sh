#!/usr/bin/env bash
# seo-geo-audit — deterministic technical audit of a LIVE site (curl-based).
#
# Checks: reachability, robots.txt + AI-crawler policy, soft-404, sitemap.xml,
# canonical/www behavior, schema presence, render-blocking JS, large images.
# WebFetch is often blocked by bot protection (e.g. Cloudflare) — curl with a UA
# gets around that.
#
# Usage: ./audit.sh <domain>        e.g. ./audit.sh example.com
#
# Note: intentionally NO `pipefail` — `grep -q` closes the pipe early, which would
# SIGPIPE the left-hand `echo` and falsely break the `&&/||` checks.
set -u

DOM="${1:?Usage: audit.sh <domain>}"
DOM="${DOM#http://}"; DOM="${DOM#https://}"; DOM="${DOM%%/*}"
BASE="https://${DOM}"
UA="Mozilla/5.0 (seo-geo-audit; +curl)"
c() { curl -sS -A "$UA" "$@"; }
hdr() { curl -sSI -A "$UA" "$@"; }
code() { curl -sS -A "$UA" -o /dev/null -w '%{http_code}' "$@"; }
ct() { curl -sS -A "$UA" -o /dev/null -w '%{content_type}' "$@"; }

echo "════════════════════════════════════════════════════════"
echo " SEO/GEO technical audit — $BASE"
echo "════════════════════════════════════════════════════════"

echo; echo "── 1. Reachability / redirects ──"
printf 'http  -> %s\n' "$(hdr "http://$DOM/" | awk 'tolower($1)~/^http|^location/{print}' | tr -d '\r' | paste -sd' ' -)"
printf 'https -> %s\n' "$(code "$BASE/")"
printf 'www   -> %s' "$(code "https://www.$DOM/")"
WWWLOC=$(hdr "https://www.$DOM/" | awk 'tolower($1)=="location:"{print $2}' | tr -d '\r')
[ -n "$WWWLOC" ] && echo " (-> $WWWLOC)" || echo "  ! www returns a status with no 301 to apex (check canonical)"

echo; echo "── 2. Soft-404 test (P0 if 200) ──"
ZC=$(code "$BASE/zzz-nonexistent-$RANDOM")
ZT=$(ct "$BASE/zzz-nonexistent-$RANDOM")
if [ "$ZC" = "200" ]; then echo "FAIL  /<random> -> 200 ($ZT) = SOFT-404 (catch-all/SPA fallback). Needs a 404.html."
else echo "OK    /<random> -> $ZC ($ZT)"; fi

echo; echo "── 3. sitemap.xml ──"
SC=$(code "$BASE/sitemap.xml"); ST=$(ct "$BASE/sitemap.xml")
echo "Status $SC, content-type $ST"
[ "$SC" = "200" ] && case "$ST" in *xml*) echo "OK  real XML"; echo -n "URLs: "; c "$BASE/sitemap.xml" | grep -oc '<loc>' ;; *) echo "!   not an XML content-type (a soft-404 may be serving HTML)";; esac

echo; echo "── 4. robots.txt + AI-crawler policy ──"
ROB=$(c "$BASE/robots.txt")
if [ -z "$ROB" ]; then echo "!   no robots.txt"; else
  echo "$ROB" | grep -qi 'cloudflare managed' && echo "i  Cloudflare 'Managed robots.txt' active (prepends its block; does NOT overwrite yours)"
  echo "Training bots (should be Disallow):"
  for b in GPTBot ClaudeBot Google-Extended CCBot Bytespider Amazonbot Applebot-Extended meta-externalagent; do
    echo "$ROB" | grep -qi "User-agent: *$b" && st="listed" || st="—"
    printf '  %-20s %s\n' "$b" "$st"
  done
  echo "Search/grounding bots (MUST be allowed for AI citations):"
  for b in OAI-SearchBot ChatGPT-User PerplexityBot Perplexity-User Claude-SearchBot Claude-User; do
    if echo "$ROB" | awk -v b="$b" 'tolower($0)==tolower("User-agent: "b){f=1;next} /^[Uu]ser-agent:/{f=0} f&&/[Dd]isallow: \//{print "BLOCK"}' | grep -q BLOCK; then st="BLOCKED!"; else st="OK allowed"; fi
    printf '  %-20s %s\n' "$b" "$st"
  done
  echo "$ROB" | grep -qi '^sitemap:' && echo "OK  Sitemap directive present" || echo "!   no Sitemap directive in robots.txt"
fi

echo; echo "── 5. On-page / schema (homepage) ──"
PAGE=$(c "$BASE/")
echo "$PAGE" | grep -qiE '<link[^>]+rel="canonical"' && echo "OK  canonical: $(echo "$PAGE" | grep -oiE 'rel="canonical"[^>]*href="[^"]*"' | grep -oE 'https?://[^"]*' | head -1)" || echo "!   no canonical"
echo "$PAGE" | grep -qi 'lang="' && echo "OK  lang set" || echo "!   no lang attribute"
echo -n "Title: "; echo "$PAGE" | grep -oiE '<title>[^<]*' | head -1 | sed 's/<title>//I'
echo -n "JSON-LD blocks: "; echo "$PAGE" | grep -c 'application/ld+json'
for t in LocalBusiness Organization FAQPage Service BreadcrumbList AggregateRating GeoCircle sameAs; do
  echo "$PAGE" | grep -q "$t" && printf '  OK %s\n' "$t"
done

echo; echo "── 6. Performance signals ──"
echo "$PAGE" | grep -oiE '<script[^>]+src="[^"]*"[^>]*>' | grep -viE 'defer|async' | grep -oE 'src="[^"]*"' | sed 's/^/  ! render-blocking JS: /' | head -10
echo "$PAGE" | grep -qiE '<(picture|source)[^>]+webp|\.webp' && echo "  OK WebP in use" || echo "  ! no WebP found (check images)"
HERO=$(echo "$PAGE" | grep -oiE 'preload"[^>]*as="image"[^>]*href="[^"]*"' | grep -oE 'href="[^"]*"' | grep -oE 'https?://[^"]*|/[^"]*' | head -1)
[ -n "$HERO" ] && { case "$HERO" in /*) HERO="$BASE$HERO";; esac; echo -n "  hero preload size: "; curl -sS -A "$UA" -o /dev/null -w '%{size_download} bytes (%{content_type})\n' "$HERO"; }

echo; echo "════════════════════════════════════════════════════════"
echo " Next: triage findings into P0/P1/P2, do off-site (GBP/reviews/NAP)"
echo " separately via a research agent, and keyword/competitor research"
echo " separately. See SKILL.md."
echo "════════════════════════════════════════════════════════"
