#!/usr/bin/env python3
"""
Domain availability checker using a three-layer query chain:
  1. RDAP (primary)
  2. DNS NS record validation
  3. WHOIS (fallback for unsupported TLDs)

Usage:
    python check_domain.py notion.com
    python check_domain.py example.io example.com myapp.ai

Output (one JSON per line):
    {"domain": "notion.com", "status": "TAKEN", "source": "rdap"}
"""

import json
import subprocess
import sys
import time
import urllib.request
import urllib.error
from typing import Optional


TIMEOUT = 5  # seconds per query
RDAP_DELAY = 0.5  # seconds between RDAP requests
WHOIS_DELAY = 1.5  # seconds between WHOIS requests
DNS_SERVER = "8.8.8.8"


def check_rdap(domain: str) -> Optional[str]:
    """Query RDAP. Returns 'TAKEN', 'NOT_FOUND', 'UNSUPPORTED', or None on error."""
    url = f"https://rdap.org/domain/{domain}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Accept", "application/rdap+json")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            if resp.status == 200:
                return "TAKEN"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "NOT_FOUND"
        if e.code in (400, 501):
            return "UNSUPPORTED"
        return None
    except Exception:
        return None


def check_dns_ns(domain: str) -> Optional[bool]:
    """Check DNS NS records. Returns True if NS records exist, False if not, None on error."""
    try:
        result = subprocess.run(
            ["dig", "+short", "NS", domain, f"@{DNS_SERVER}"],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
        output = result.stdout.strip()
        if result.returncode == 0:
            return len(output) > 0
        return None
    except Exception:
        return None


def check_whois(domain: str) -> Optional[str]:
    """Query WHOIS. Returns 'TAKEN', 'AVAILABLE', or None on error."""
    try:
        result = subprocess.run(
            ["whois", domain],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
        output = result.stdout.lower()
        not_found_indicators = [
            "no match",
            "not found",
            "domain not found",
            "no entries found",
            "no data found",
            "status: free",
            "status: available",
            "is available for registration",
        ]
        for indicator in not_found_indicators:
            if indicator in output:
                return "AVAILABLE"
        # If we got output and no "not found" indicators, it's likely taken
        if len(output) > 50:
            return "TAKEN"
        return None
    except Exception:
        return None


def check_domain(domain: str) -> dict:
    """Run the three-layer query chain for a single domain."""
    domain = domain.lower().strip()

    # Layer 1: RDAP
    rdap_result = check_rdap(domain)

    if rdap_result == "TAKEN":
        return {"domain": domain, "status": "TAKEN", "source": "rdap"}

    if rdap_result == "NOT_FOUND":
        # Layer 2: DNS NS validation (guard against RDAP false negatives)
        has_ns = check_dns_ns(domain)
        if has_ns is True:
            return {"domain": domain, "status": "TAKEN", "source": "dns"}
        if has_ns is False:
            return {"domain": domain, "status": "AVAILABLE", "source": "rdap+dns"}
        # DNS query failed — still lean towards AVAILABLE but mark uncertain
        return {"domain": domain, "status": "AVAILABLE", "source": "rdap"}

    if rdap_result == "UNSUPPORTED":
        # Layer 3: WHOIS fallback
        time.sleep(WHOIS_DELAY)
        whois_result = check_whois(domain)
        if whois_result in ("TAKEN", "AVAILABLE"):
            return {"domain": domain, "status": whois_result, "source": "whois"}
        return {"domain": domain, "status": "UNCERTAIN", "source": "whois"}

    # RDAP returned None (error/timeout) — try DNS then WHOIS
    has_ns = check_dns_ns(domain)
    if has_ns is True:
        return {"domain": domain, "status": "TAKEN", "source": "dns"}

    time.sleep(WHOIS_DELAY)
    whois_result = check_whois(domain)
    if whois_result in ("TAKEN", "AVAILABLE"):
        return {"domain": domain, "status": whois_result, "source": "whois"}

    return {"domain": domain, "status": "UNCERTAIN", "source": "none"}


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_domain.py <domain> [domain2] [domain3] ...")
        sys.exit(1)

    domains = sys.argv[1:]
    for i, domain in enumerate(domains):
        result = check_domain(domain)
        print(json.dumps(result))
        # Rate limiting between queries
        if i < len(domains) - 1:
            time.sleep(RDAP_DELAY)


if __name__ == "__main__":
    main()
