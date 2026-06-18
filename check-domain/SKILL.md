---
name: check-domain
description: Check domain availability with a whois lookup against the official registrars (DENIC for .de, EURid for .eu, Verisign for .com/.net, PIR for .org). Use when checking if a domain is available, during brand/naming research, or before registering a new domain.
---

# Check Domain Availability

Check whether domain names are available for registration. Uses the system `whois` command directly against official registrars for reliable results — no third-party libraries or lookup sites.

## When to use
- Checking if a domain is available
- Brand/naming research where domain availability matters
- Before registering a new domain

## Requirements
The system `whois` command. No API keys.
- macOS: `brew install whois` (or preinstalled)
- Debian/Ubuntu: `apt install whois`

## Usage

Check a single domain:
```bash
python3 ~/.claude/skills/check-domain/scripts/check_domain.py example.de
```

Check multiple domains:
```bash
python3 ~/.claude/skills/check-domain/scripts/check_domain.py example.de example.com example.eu example.org
```

Check one name across all major TLDs (.de .com .eu .org .net):
```bash
python3 ~/.claude/skills/check-domain/scripts/check_domain.py --all veritora
```

Output:
```
veritora.de        FREE
veritora.com       TAKEN  (registered: 2019-06-28, expires: 2026-06-28)
veritora.eu        FREE
```

## How it works
- Calls the `whois` CLI directly (not the `python-whois` library, which is unreliable for .de domains)
- Parses the raw WHOIS response per TLD:
  - .de (DENIC): `Status: free` = available
  - .com/.net (Verisign): `No match for` = available
  - .eu (EURid): `Status: AVAILABLE` = available
  - .org (PIR): `NOT FOUND` = available
- Returns registration dates where the registrar exposes them

## Notes
- Do NOT use the `python-whois` pip package for .de domains — its error text can contain `Status: free` even when the domain IS registered, and it sometimes reports registered domains as free.
- Do NOT use third-party WHOIS sites (who.is, whois.com) — they cache results and can be wrong.
- Always use the system `whois` command, which queries the official registrars directly. For .de, DENIC (whois.denic.de) is the only authoritative source; for .eu, EURid.
