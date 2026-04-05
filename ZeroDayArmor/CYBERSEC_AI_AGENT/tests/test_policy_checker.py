import pytest
from unittest.mock import patch, MagicMock
from agents.policy_checker import PolicyCheckerAgent


@pytest.fixture
def agent():
    return PolicyCheckerAgent()


class TestPolicyCheckerAgent:

    @patch("langchain.agents.AgentExecutor.invoke")
    def test_nist_compliance(self, mock_invoke, agent):
        mock_invoke.return_value = {
            "output": """{"framework":"NIST_CSF","compliance_score":45.0,
                "gaps":[{"control_id":"PR.AC-7","framework":"NIST_CSF",
                "control_title":"MFA","status":"non_compliant",
                "remediation":"Enable MFA","evidence_required":["MFA Log"]}],
                "priority_fixes":["Fix MFA"],"audit_ready":false}"""
        }
        state = {
            "input_type": "config",
            "input_data": "{'mfa': false}",
            "compliance_reports": [],
        }
        result = agent.run(state)
        report = result["compliance_reports"][0]
        assert report["compliance_score"] == 45.0
        assert "MFA" in report["gaps"][0]["control_title"]
