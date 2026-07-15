#!/usr/bin/env python3
"""
Check domain availability using the system whois command.
Queries official registrars directly -- no third-party libraries or lookup sites.

Usage:
    python3 check_domain.py example.de example.com
    python3 check_domain.py --all mybrand         # checks .de .com .eu .org .net
"""

import subprocess
import sys
import re
from dataclasses import dataclass


@dataclass
class DomainResult:
    domain: str
    available: bool
    registrar: str = ""
    created: str = ""
    expires: str = ""
    error: str = ""


# TLD-specific parsing rules -- each TLD has a different WHOIS response format
TLD_RULES = {
    "de": {
        "free_pattern": r"Status:\s*free",
        "registrar_pattern": r"Organisation:\s*(.+)",
        "created_pattern": r"Changed:\s*(.+)",  # .de shows last change, not creation
        "expires_pattern": None,  # .de WHOIS doesn't show expiry
    },
    "com": {
        "free_pattern": r"^No match for",
        "registrar_pattern": r"Registrar:\s*(.+)",
        "created_pattern": r"Creation Date:\s*(.+)",
        "expires_pattern": r"Registry Expiry Date:\s*(.+)",
    },
    "net": {
        "free_pattern": r"^No match for",
        "registrar_pattern": r"Registrar:\s*(.+)",
        "created_pattern": r"Creation Date:\s*(.+)",
        "expires_pattern": r"Registry Expiry Date:\s*(.+)",
    },
    "org": {
        "free_pattern": r"NOT FOUND",
        "registrar_pattern": r"Registrar:\s*(.+)",
        "created_pattern": r"Creation Date:\s*(.+)",
        "expires_pattern": r"Registry Expiry Date:\s*(.+)",
    },
    "eu": {
        "free_pattern": r"Status:\s*AVAILABLE",
        "registrar_pattern": r"Registrar:\s*\n\s*Name:\s*(.+)",
        "created_pattern": None,
        "expires_pattern": None,
    },
}

# Fallback for unknown TLDs
DEFAULT_RULES = {
    "free_pattern": r"(No match|NOT FOUND|No entries found|Status:\s*free|Status:\s*AVAILABLE|DOMAIN NOT FOUND)",
    "registrar_pattern": r"Registrar:\s*(.+)",
    "created_pattern": r"Creation Date:\s*(.+)",
    "expires_pattern": r"Registry Expiry Date:\s*(.+)",
}

ALL_TLDS = ["de", "com", "eu", "org", "net"]


def get_tld(domain: str) -> str:
    """Extract TLD from domain name."""
    return domain.rsplit(".", 1)[-1].lower() if "." in domain else ""


def run_whois(domain: str) -> str:
    """Run system whois command and return raw output."""
    try:
        result = subprocess.run(
            ["whois", domain],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "ERROR: WHOIS timeout"
    except FileNotFoundError:
        return "ERROR: whois command not found"


def parse_whois(domain: str, raw: str) -> DomainResult:
    """Parse raw WHOIS output using TLD-specific rules."""
    if raw.startswith("ERROR:"):
        return DomainResult(domain=domain, available=False, error=raw)

    tld = get_tld(domain)
    rules = TLD_RULES.get(tld, DEFAULT_RULES)

    # Check if domain is free
    free_match = re.search(rules["free_pattern"], raw, re.MULTILINE | re.IGNORECASE)
    if free_match:
        return DomainResult(domain=domain, available=True)

    # Domain is registered -- extract details
    result = DomainResult(domain=domain, available=False)

    if rules.get("registrar_pattern"):
        m = re.search(rules["registrar_pattern"], raw, re.MULTILINE)
        if m:
            result.registrar = m.group(1).strip()

    if rules.get("created_pattern"):
        m = re.search(rules["created_pattern"], raw, re.MULTILINE)
        if m:
            result.created = m.group(1).strip()[:10]  # Just the date part

    if rules.get("expires_pattern"):
        m = re.search(rules["expires_pattern"], raw, re.MULTILINE)
        if m:
            result.expires = m.group(1).strip()[:10]

    return result


def check_domain(domain: str) -> DomainResult:
    """Check a single domain's availability."""
    raw = run_whois(domain)
    return parse_whois(domain, raw)


def format_result(result: DomainResult) -> str:
    """Format a single result for display."""
    status = "FREE" if result.available else "TAKEN"
    line = f"{result.domain:<30} {status}"

    if result.error:
        line += f"  ({result.error})"
    elif not result.available:
        details = []
        if result.created:
            details.append(f"registered: {result.created}")
        if result.expires:
            details.append(f"expires: {result.expires}")
        if result.registrar:
            details.append(f"at: {result.registrar[:40]}")
        if details:
            line += f"  ({', '.join(details)})"

    return line


def main():
    args = sys.argv[1:]

    if not args:
        print("Usage: python3 check_domain.py domain1.de domain2.com")
        print("       python3 check_domain.py --all brandname")
        sys.exit(1)

    domains = []

    if args[0] == "--all":
        if len(args) < 2:
            print("Usage: python3 check_domain.py --all brandname")
            sys.exit(1)
        name = args[1].replace(".", "")  # Strip any dots
        domains = [f"{name}.{tld}" for tld in ALL_TLDS]
    else:
        domains = args

    print(f"\n{'Domain':<30} {'Status'}")
    print("-" * 70)

    free_count = 0
    taken_count = 0

    for domain in domains:
        result = check_domain(domain)
        print(format_result(result))
        if result.available:
            free_count += 1
        else:
            taken_count += 1

    print("-" * 70)
    print(f"Result: {free_count} free, {taken_count} taken\n")


if __name__ == "__main__":
    main()
