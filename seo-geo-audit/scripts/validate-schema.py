#!/usr/bin/env python3
"""seo-geo-audit — JSON-LD validator.

Extracts every <script type="application/ld+json"> block from an HTML file OR a
URL, parses each as JSON, and lists @type. Catches the most common mistakes:
trailing commas, broken strings, and the classic `&amp;` in JSON-LD (HTML
entities are NOT decoded inside <script> content — it belongs as plain `&`,
otherwise the entity ends up literally in the schema value).

Usage:
  validate-schema.py page.html
  validate-schema.py https://example.com/
"""
import json
import re
import sys
import urllib.request

PAT = re.compile(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S | re.I)


def load(src: str) -> str:
    if src.startswith(("http://", "https://")):
        req = urllib.request.Request(src, headers={"User-Agent": "seo-geo-audit/validate-schema"})
        return urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
    with open(src, encoding="utf-8") as fh:
        return fh.read()


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    html = load(sys.argv[1])
    blocks = PAT.findall(html)
    if not blocks:
        print("No JSON-LD blocks found.")
        return 1
    bad = 0
    for i, raw in enumerate(blocks):
        ent = [e for e in ("&amp;", "&lt;", "&gt;", "&quot;", "&#") if e in raw]
        try:
            obj = json.loads(raw)
            t = obj.get("@type", "?") if isinstance(obj, dict) else "[array]"
            warn = f"  ! HTML entity inside JSON-LD ({', '.join(ent)}) — should be plain" if ent else ""
            print(f"OK   block {i}: @type={t}{warn}")
        except json.JSONDecodeError as exc:
            bad += 1
            print(f"FAIL block {i}: JSON error — {exc}")
            if ent:
                print(f"     hint: HTML entity found ({', '.join(ent)}) — common cause.")
    print(f"\n{'ALL VALID' if not bad else f'{bad} INVALID'} ({len(blocks)} blocks).")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
