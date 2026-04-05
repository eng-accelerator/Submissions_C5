from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers import PydanticOutputParser
from agents.base_agent import BaseCyberAgent
from tools.log_tools import regex_parser_tool, ip_reputation_tool, geo_lookup_tool
from schemas.outputs import LogAlert

SYSTEM_PROMPT = """You are a senior SOC analyst with 10+ years experience.
Analyze log entries and detect security threats. Use your tools to:
1. Parse logs with regex_parser_tool to find attack patterns
2. Check suspicious IPs with ip_reputation_tool
3. Look up geo-location with geo_lookup_tool for context
4. Return structured JSON matching LogAlert schema

Severity rules:
- CRITICAL: active RCE, data exfiltration in progress, ransomware
- HIGH: brute force success, privilege escalation, lateral movement
- MEDIUM: reconnaissance, failed brute force (>10 attempts), scanning
- LOW: single failed login, unusual hours access, new user agent

Always include MITRE ATT&CK technique IDs (e.g., T1110.001 for brute force).
CRITICAL: Your output MUST be strictly valid JSON. Do NOT include ANY generic text, markdown outside of the JSON block, or `// comments` anywhere inside the JSON. If a required value like `timestamp` is missing, output 'UNKNOWN'.

Format instructions:
{format_instructions}"""


class LogMonitorAgent(BaseCyberAgent):
    def __init__(self):
        super().__init__("Log Monitor", "Analyze system/network logs for anomalies.")
        self.llm = self.get_llm(temperature=0)
        self.parser = PydanticOutputParser(pydantic_object=LogAlert)
        self.tools = [regex_parser_tool, ip_reputation_tool, geo_lookup_tool]

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", "Analyze these logs:\n{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        ).partial(format_instructions=self.parser.get_format_instructions())

        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        self.executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    def run(self, state: dict) -> dict:
        print(f"[*] Running {self.name} Agent...")
        result = self.executor.invoke({"input": state["input_data"]})
        try:
            # The agent might return markdown-wrapped JSON, so we clean it
            output_text = result["output"]
            if "```json" in output_text:
                output_text = output_text.split("```json")[1].split("```")[0].strip()

            alert = self.parser.parse(output_text)
            state["log_alerts"] = [alert.model_dump()]
            state["severity_level"] = alert.severity.value
        except Exception as e:
            print(f"Error parsing LogMonitor result: {e}")
            state["log_alerts"] = [{"error": str(e), "raw": result["output"]}]
            state["severity_level"] = "LOW"

        return state
