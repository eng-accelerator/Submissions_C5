from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from agents.base_agent import BaseCyberAgent
from schemas.outputs import ComplianceReport

SYSTEM_PROMPT = """You are a Policy Checker Agent. Your role is:
1. Conduct compliance gap analysis against security frameworks (NIST CSF, ISO 27001, SOC2, PCI-DSS).
2. Compare the provided configuration against these frameworks relying purely on your core knowledge.
3. Provide remediation steps and evidence requirements for auditors.

Format your output as structured JSON matching ComplianceReport schema.
Format:
{format_instructions}"""


class PolicyCheckerAgent(BaseCyberAgent):
    def __init__(self):
        super().__init__(
            "Policy Checker", "Compliance gap analysis against security frameworks."
        )
        self.llm = self.get_llm(temperature=0)
        self.parser = PydanticOutputParser(pydantic_object=ComplianceReport)
        self.tools = []

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", "Analyze compliance for this config:\n{input}"),
            ]
        ).partial(format_instructions=self.parser.get_format_instructions())

        self.chain = prompt | self.llm

    def run(self, state: dict) -> dict:
        print(f"[*] Running {self.name} Agent...")
        result = self.chain.invoke({"input": state["input_data"]})
        try:
            output_text = result.content
            if "```json" in output_text:
                output_text = output_text.split("```json")[1].split("```")[0].strip()

            report = self.parser.parse(output_text)
            state["compliance_reports"] = [report.model_dump()]
            state["severity_level"] = (
                "HIGH" if report.compliance_score < 50 else "MEDIUM"
            )
        except Exception as e:
            print(f"Error parsing PolicyChecker result: {e}")
            state["compliance_reports"] = [{"error": str(e)}]

        return state
