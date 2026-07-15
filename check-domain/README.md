# check-domain

Check whether domain names are free to register, with a direct `whois` lookup against the official registrars: DENIC for `.de`, EURid for `.eu`, Verisign for `.com`/`.net`, PIR for `.org`. No API keys, no third-party lookup sites.

## Install

```bash
npx degit --force mfraunhofer/claude-skills/check-domain ~/.claude/skills/check-domain
```

Requires the system `whois` command (`brew install whois` on macOS, `apt install whois` on Debian/Ubuntu).

## Usage

Ask Claude "is mybrand.de available?" or run the script directly:

```bash
python3 ~/.claude/skills/check-domain/scripts/check_domain.py mybrand.de mybrand.com
python3 ~/.claude/skills/check-domain/scripts/check_domain.py --all mybrand   # .de .com .eu .org .net
```

```
mybrand.de         FREE
mybrand.com        TAKEN  (registered: 2019-06-28, expires: 2026-06-28)
mybrand.eu         FREE
```

## Why direct whois

Third-party WHOIS sites cache results and get `.de` domains wrong, and the `python-whois` pip package can report registered `.de` domains as free (its error text sometimes contains `Status: free`). Querying the registrars directly is the only reliable source. Details in [SKILL.md](SKILL.md).

## Files

| File | Purpose |
|---|---|
| [SKILL.md](SKILL.md) | Skill definition: triggers, parsing rules per TLD, pitfalls |
| [scripts/check_domain.py](scripts/check_domain.py) | The lookup script (stdlib only) |
