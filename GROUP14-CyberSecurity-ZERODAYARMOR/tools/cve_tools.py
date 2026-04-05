import json
import requests
from langchain.tools import tool


@tool
def nvd_cve_lookup(keyword: str) -> list:
    """Queries the NVD API for CVEs based on a keyword search (demo)."""
    # For a real implementation, this would use requests to query nvd.nist.gov
    # Using sample CVE data for the hackathon demo
    sample_cves = [
        {
            "id": "CVE-2021-44228",
            "description": "Apache Log4j2 JNDI remote code execution",
        },
        {
            "id": "CVE-2022-22965",
            "description": "Spring Framework RCE via Data Binding (Spring4Shell)",
        },
        {"id": "CVE-2023-44487", "description": "HTTP/2 Rapid Reset Attack"},
    ]
    return [cve for cve in sample_cves if keyword.lower() in cve["description"].lower()]


@tool
def mitre_attack_lookup(technique_id: str) -> dict:
    """Look up MITRE ATT&CK technique details (simulated)."""
    techniques = {
        "T1110.001": {
            "name": "Brute Force: Password Guessing",
            "description": "Adversaries may attempt to guess passwords.",
        },
        "T1190": {
            "name": "Exploit Public-Facing Application",
            "description": "Adversaries may exploit a vulnerability in a public-facing application.",
        },
        "T1059": {
            "name": "Command and Scripting Interpreter",
            "description": "Adversaries may abuse interpreters to execute malicious commands.",
        },
    }
    return techniques.get(
        technique_id, {"name": "Unknown", "description": "No details available."}
    )


@tool
def cisa_kev_check(cve_id: str) -> bool:
    """Checks if a CVE is in the CISA Known Exploited Vulnerabilities (KEV) list (simulated)."""
    kev_list = ["CVE-2021-44228", "CVE-2022-22965"]
    return cve_id in kev_list
