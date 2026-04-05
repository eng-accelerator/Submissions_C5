from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers import PydanticOutputParser
from agents.base_agent import BaseCyberAgent
from tools.scan_tools import bandit_scan_tool, safety_check_tool, trivy_scan_tool
from schemas.outputs import ScanResult

SYSTEM_PROMPT = """You are a Vulnerability Scanner Agent. You analyze source code, dependencies, and container configurations for vulnerabilities.
Use your tools:
1. bandit_scan_tool for Python source code analysis (SAST).
2. safety_check_tool for checking requirements.txt or dependencies.
3. trivy_scan_tool for Dockerfile or container image audits.

Classify issues by CWE ID and provide fix recommendations.
Format:
{format_instructions}"""


class VulnScannerAgent(BaseCyberAgent):
    def __init__(self):
        super().__init__(
            "Vuln Scanner", "SAST, dependency audit, and container security scanning."
        )
        self.llm = self.get_llm(temperature=0)
        self.parser = PydanticOutputParser(pydantic_object=ScanResult)
        self.tools = [bandit_scan_tool, safety_check_tool, trivy_scan_tool]

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", "Scan this target:\n{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        ).partial(format_instructions=self.parser.get_format_instructions())

        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        self.executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    def run(self, state: dict) -> dict:
        print(f"[*] Running {self.name} Agent...")
        result = self.executor.invoke({"input": state["input_data"]})
        try:
            output_text = result["output"]
            if "```json" in output_text:
                output_text = output_text.split("```json")[1].split("```")[0].strip()

            scan_result = self.parser.parse(output_text)
            state["scan_results"] = [scan_result.model_dump()]
            state["severity_level"] = (
                "HIGH" if scan_result.risk_score >= 60 else "MEDIUM"
            )
        except Exception as e:
            print(f"Error parsing VulnScanner result: {e}")
            state["scan_results"] = [{"error": str(e)}]

        return state
