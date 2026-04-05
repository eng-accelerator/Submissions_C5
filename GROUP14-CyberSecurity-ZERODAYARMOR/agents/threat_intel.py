from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers import PydanticOutputParser
from agents.base_agent import BaseCyberAgent
from tools.cve_tools import nvd_cve_lookup, mitre_attack_lookup, cisa_kev_check
from rag.retriever import CVERetriever
from schemas.outputs import ThreatReport

SYSTEM_PROMPT = """You are a Threat Intelligence Analyst. Your goal is to:
1. Search for CVEs related to the user's query.
2. Use nvd_cve_lookup for official data.
3. Check cisa_kev_check to see if vulnerabilities are actively being exploited.
4. Use mitre_attack_lookup for mapping to techniques.
5. Ground your answers in the provided RAG context if applicable.

Context from CVE Database:
{context}

Format:
{format_instructions}"""


class ThreatIntelAgent(BaseCyberAgent):
    def __init__(self):
        super().__init__(
            "Threat Intel", "Identify and analyze CVEs and threat patterns."
        )
        self.llm = self.get_llm(temperature=0)
        self.parser = PydanticOutputParser(pydantic_object=ThreatReport)
        self.tools = [nvd_cve_lookup, mitre_attack_lookup, cisa_kev_check]
        self.retriever = CVERetriever()

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        ).partial(format_instructions=self.parser.get_format_instructions())

        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        self.executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    def run(self, state: dict) -> dict:
        print(f"[*] Running {self.name} Agent...")
        context = self.retriever.get_context(state["input_data"])

        result = self.executor.invoke(
            {"input": state["input_data"], "context": context}
        )

        try:
            output_text = result["output"]
            if "```json" in output_text:
                output_text = output_text.split("```json")[1].split("```")[0].strip()

            report = self.parser.parse(output_text)
            state["threat_reports"] = [report.model_dump()]
            state["severity_level"] = "HIGH" if report.cvss_score >= 7.0 else "MEDIUM"
        except Exception as e:
            print(f"Error parsing ThreatIntel result: {e}")
            state["threat_reports"] = [{"error": str(e)}]

        return state
