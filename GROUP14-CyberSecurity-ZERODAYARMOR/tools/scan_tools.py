import subprocess
import os
from langchain.tools import tool


@tool
def bandit_scan_tool(code: str) -> str:
    """Runs Bandit SAST scan on Python source code (simulated)."""
    # In a real environment, this might write code to a file and call Bandit
    # For the hackathon, we simulate common Bandit findings
    if 'query = f"SELECT' in code:
        return "B608: Test for SQL injection (High severity)"
    if 'subprocess.check_output(f"ping' in code:
        return "B602: Test for shell injection (Low severity)"
    if "AWS_ACCESS_KEY" in code:
        return "B105: Hardcoded password string (High severity)"
    return "No Bandit findings detected."


@tool
def safety_check_tool(requirements: str) -> str:
    """Runs Safety check for vulnerable dependencies (simulated)."""
    if "requests==2.18.0" in requirements:
        return "Vulnerability in requests v2.18.0 (CVE-2018-18074). Upgrade to 2.22.0+."
    return "No safety vulnerabilities found."


@tool
def trivy_scan_tool(dockerfile: str) -> str:
    """Runs Trivy scan on Dockerfile for misconfigurations (simulated)."""
    if "USER root" in dockerfile or "USER" not in dockerfile:
        return "Misconfiguration: Running as root (High risk)."
    return "No Trivy findings."
