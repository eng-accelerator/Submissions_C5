import pytest
from unittest.mock import patch, MagicMock
from agents.incident_response import IncidentResponseAgent


@pytest.fixture
def agent():
    return IncidentResponseAgent()


class TestIncidentResponseAgent:

    @patch("langchain.agents.AgentExecutor.invoke")
    def test_ransomware_playbook(self, mock_invoke, agent):
        mock_invoke.return_value = {
            "output": """{"incident_type":"ransomware","severity":"CRITICAL",
                "playbook":[{"step":1,"phase":"containment","description":"Isolate server",
                "owner":"SOC Team","eta_minutes":5,"priority":"IMMEDIATE"}],
                "containment_commands":["iptables -A OUTPUT -j DROP"],
                "notification_list":["CISO","Legal"],"estimated_resolution_hours":4}"""
        }
        state = {
            "input_type": "incident",
            "input_data": "Ransomware on FS01",
            "playbooks": [],
        }
        result = agent.run(state)
        assert result["severity_level"] == "CRITICAL"
        assert "Legal" in result["playbooks"][0]["notification_list"]
