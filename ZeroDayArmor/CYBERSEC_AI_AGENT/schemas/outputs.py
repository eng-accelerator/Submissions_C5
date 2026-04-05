from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum
import uuid


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ── Log Monitor Output ─────────────────────────────────────
class LogAlert(BaseModel):
    alert_type: Literal["brute_force", "port_scan", "sqli", "rce", "exfil", "anomaly"]
    severity: Severity
    source_ip: str = Field(
        ..., pattern=r"^(?:\d{1,3}(\.\d{1,3}){3}|\[REDACTED_IPV4\])$"
    )
    affected_user: Optional[str] = Field(
        None,
        description="The user or email associated with the event (e.g., [REDACTED_EMAIL])",
    )
    timestamp: str
    affected_service: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    mitre_tactic: Optional[str] = None
    mitre_technique: Optional[str] = None
    raw_evidence: List[str] = Field(default_factory=list)


# ── Threat Intel Output ────────────────────────────────────
class ThreatReport(BaseModel):
    cve_ids: List[str]
    cvss_score: float = Field(..., ge=0.0, le=10.0)
    exploit_available: bool
    exploit_poc_url: Optional[str] = None
    affected_versions: List[str]
    patch_available: bool
    patch_url: Optional[str] = None
    threat_actors: List[str] = Field(default_factory=list)
    summary: str


# ── Vuln Scanner Output ────────────────────────────────────
class Vulnerability(BaseModel):
    cwe_id: str
    title: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    severity: Severity
    cvss_score: Optional[float] = None
    description: str
    fix_recommendation: str


class ScanResult(BaseModel):
    scan_target: str
    scan_type: Literal["sast", "dependency", "container", "api"]
    findings: List[Vulnerability]
    risk_score: int = Field(..., ge=0, le=100)
    remediation_priority: List[str]


# ── Incident Response Output ───────────────────────────────
class Action(BaseModel):
    step: int
    phase: Literal["detection", "containment", "eradication", "recovery"]
    description: str
    owner: str
    eta_minutes: int
    command: Optional[str] = None
    priority: Literal["IMMEDIATE", "URGENT", "NORMAL"]


class IncidentPlaybook(BaseModel):
    incident_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_type: str
    affected_user: Optional[str] = Field(
        None,
        description="Compromised user identity, email, or REDACTED token involved.",
    )
    severity: Severity
    playbook: List[Action]
    containment_commands: List[str]
    notification_list: List[str]
    estimated_resolution_hours: float


# ── Policy Checker Output ──────────────────────────────────
class ComplianceGap(BaseModel):
    control_id: str
    framework: Literal["NIST_CSF", "ISO27001", "SOC2", "PCI_DSS"]
    control_title: str
    status: Literal["compliant", "partial", "non_compliant", "unknown"]
    remediation: str
    evidence_required: List[str]


class ComplianceReport(BaseModel):
    framework: str
    compliance_score: float = Field(..., ge=0.0, le=100.0)
    gaps: List[ComplianceGap]
    priority_fixes: List[str]
    audit_ready: bool


# ── Vision Threat Analysis Output ───────────────────────────
class PhishingReport(BaseModel):
    is_phishing: bool
    risk_level: Severity
    detected_threats: List[str] = Field(
        description="Types of detected threats (e.g., Spear Phishing, BEC, Quishing, etc)"
    )
    social_engineering_tactics: List[str]
    suspicious_links_or_attachments: List[str]
    summary_analysis: str
