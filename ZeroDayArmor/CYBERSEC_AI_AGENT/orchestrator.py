from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Any, Optional
from agents.log_monitor import LogMonitorAgent
from agents.threat_intel import ThreatIntelAgent
from agents.vuln_scanner import VulnScannerAgent
from agents.incident_response import IncidentResponseAgent
from agents.policy_checker import PolicyCheckerAgent


class SecurityState(TypedDict):
    input_data: str
    input_type: str  # log | cve_query | code | config | incident
    log_alerts: List[Any]
    threat_reports: List[Any]
    scan_results: List[Any]
    playbooks: List[Any]
    compliance_reports: List[Any]
    final_summary: str
    severity_level: str  # aggregated max severity


def route_input(state: SecurityState) -> str:
    """Router: decides which agent runs based on input_type."""
    t = state["input_type"]
    if t == "log":
        return "log_monitor"
    if t == "cve_query":
        return "threat_intel"
    if t == "code":
        return "vuln_scanner"
    if t == "config":
        return "policy_checker"
    if t == "incident":
        return "incident_response"
    return "log_monitor"  # default


def should_escalate(state: SecurityState) -> str:
    """After log monitor: escalate CRITICAL to incident response."""
    for alert in state.get("log_alerts", []):
        if alert.get("severity") == "CRITICAL":
            return "incident_response"
    return END


def build_graph() -> StateGraph:
    graph = StateGraph(SecurityState)

    # Add nodes
    graph.add_node("log_monitor", LogMonitorAgent().run)
    graph.add_node("threat_intel", ThreatIntelAgent().run)
    graph.add_node("vuln_scanner", VulnScannerAgent().run)
    graph.add_node("incident_response", IncidentResponseAgent().run)
    graph.add_node("policy_checker", PolicyCheckerAgent().run)

    # Router node (dummy transformer node)
    graph.add_node("router_node", lambda s: s)

    # Entry point
    graph.set_entry_point("router_node")

    # Conditional Edges from router
    graph.add_conditional_edges(
        "router_node",
        route_input,
        {
            "log_monitor": "log_monitor",
            "threat_intel": "threat_intel",
            "vuln_scanner": "vuln_scanner",
            "policy_checker": "policy_checker",
            "incident_response": "incident_response",
        },
    )

    # Log monitor can auto-escalate
    graph.add_conditional_edges(
        "log_monitor",
        should_escalate,
        {
            "incident_response": "incident_response",
            END: END,
        },
    )

    # All others terminate
    graph.add_edge("threat_intel", END)
    graph.add_edge("vuln_scanner", END)
    graph.add_edge("incident_response", END)
    graph.add_edge("policy_checker", END)

    return graph.compile()


# Integration with main runner
if __name__ == "__main__":
    app = build_graph()
    test_state = {
        "input_type": "log",
        "input_data": "Jan 15 02:30:45 webserver sshd[12340]: Failed password for root from 185.220.101.45 port 42810 ssh2",
        "log_alerts": [],
        "threat_reports": [],
        "scan_results": [],
        "playbooks": [],
        "compliance_reports": [],
        "severity_level": "LOW",
    }
    result = app.invoke(test_state)
    print("Orchestrator Execution Completed.")
