import pytest
from unittest.mock import patch, MagicMock
from agents.vuln_scanner import VulnScannerAgent


@pytest.fixture
def agent():
    return VulnScannerAgent()


class TestVulnScannerAgent:

    @patch("langchain.agents.AgentExecutor.invoke")
    def test_sqli_detection(self, mock_invoke, agent):
        mock_invoke.return_value = {
            "output": """{"scan_target":"insecure_app.py","scan_type":"sast",
                "findings":[{"cwe_id":"CWE-89","title":"SQL Injection",
                "severity":"HIGH","description":"SQL injection via concatenation",
                "fix_recommendation":"Use placeholders"}],
                "risk_score":85,"remediation_priority":["Fix SQLi"]}"""
        }
        state = {
            "input_type": "code",
            "input_data": "query = 'SELECT * FROM users WHERE id=' + id",
            "scan_results": [],
        }
        result = agent.run(state)
        findings = result["scan_results"][0]["findings"]
        assert findings[0]["cwe_id"] == "CWE-89"
        assert result["severity_level"] == "HIGH"
