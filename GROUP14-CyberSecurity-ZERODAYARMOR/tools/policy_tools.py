from langchain.tools import tool


@tool
def compliance_mapper(control_id: str, framework: str) -> dict:
    """Maps a control ID to its full description in NIST, ISO, SOC2, or PCI frameworks."""
    # This would normally query a local JSON / Vector store of framework controls
    if framework == "NIST_CSF" and control_id == "PR.AC-7":
        return {
            "id": "PR.AC-7",
            "title": "Access control policy",
            "description": "Users, devices and other assets are authenticated.",
        }
    if framework == "ISO27001" and control_id == "A.10.1":
        return {
            "id": "A.10.1.1",
            "title": "Policy on the use of cryptographic controls",
            "description": "Implementation for protection of information.",
        }
    return {
        "id": control_id,
        "title": "Unknown Control",
        "description": "No description available.",
    }
