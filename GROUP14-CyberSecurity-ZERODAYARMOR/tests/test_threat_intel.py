import pytest
from unittest.mock import patch, MagicMock
from agents.threat_intel import ThreatIntelAgent


@pytest.fixture
def agent():
    return ThreatIntelAgent()


class TestThreatIntelAgent:

    @patch("langchain.agents.AgentExecutor.invoke")
    @patch("rag.retriever.CVERetriever.get_context")
    def test_log4shell_lookup(self, mock_get_context, mock_invoke, agent):
        mock_get_context.return_value = "CVE-2021-44228: Apache Log4j2 JNDI RCE"
        mock_invoke.return_value = {
            "output": """{"cve_ids":["CVE-2021-44228"],"cvss_score":10.0,
                "exploit_available":true,"affected_versions":["2.0-beta9 to 2.15.0"],
                "patch_available":true,"summary":"Critical Log4j vulnerability"}"""
        }
        state = {
            "input_type": "cve_query",
            "input_data": "Log4j RCE",
            "threat_reports": [],
        }
        result = agent.run(state)
        report = result["threat_reports"][0]
        assert "CVE-2021-44228" in report["cve_ids"]
        assert report["cvss_score"] == 10.0
        assert result["severity_level"] == "HIGH"
