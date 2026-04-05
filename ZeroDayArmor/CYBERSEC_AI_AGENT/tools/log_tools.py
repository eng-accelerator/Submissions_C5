import re
from langchain.tools import tool


@tool
def regex_parser_tool(log_entries: str) -> list:
    """Parses log entries for security patterns like brute force, SQLi, and RCE."""
    patterns = {
        "brute_force": r"Failed password for .* from (\d{1,3}(?:\.\d{1,3}){3})",
        "sqli": r"UNION\s+SELECT|SELECT\s+.*\s+FROM|DROP\s+TABLE",
        "rce": r";\s*(?:curl|wget|bash|sh|nc|python|perl|php)",
    }

    findings = []
    for category, pattern in patterns.items():
        matches = re.finditer(pattern, log_entries, re.IGNORECASE)
        for match in matches:
            findings.append(
                {
                    "category": category,
                    "evidence": match.group(0),
                    "source_ip": (
                        match.group(1) if category == "brute_force" else "unknown"
                    ),
                }
            )
    return findings


@tool
def ip_reputation_tool(ip: str) -> dict:
    """Checks the reputation of an IP address (simulated AbuseIPDB)."""
    # In a real scenario, this would call the AbuseIPDB API
    malicious_ips = ["185.220.101.45", "104.21.0.0"]
    if ip in malicious_ips:
        return {"ip": ip, "abuse_score": 98, "is_known_attacker": True}
    return {"ip": ip, "abuse_score": 0, "is_known_attacker": False}


@tool
def geo_lookup_tool(ip: str) -> dict:
    """Performs a geographic lookup for an IP address (simulated ip-api.com)."""
    # Simulated response
    if ip == "185.220.101.45":
        return {"country": "Romania", "city": "Bucharest", "isp": "Tor Exit Node"}
    return {"country": "US", "city": "New York", "isp": "Cloudflare"}
