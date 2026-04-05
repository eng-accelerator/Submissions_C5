from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from agents.base_agent import BaseCyberAgent
from schemas.outputs import IncidentPlaybook

SYSTEM_PROMPT = """You are an Incident Response Agent. Your role is to:
1. Analyze security alerts and create situational playbooks.
2. Provide containment, eradication, and recovery steps.
3. Classify the incident severity and estimate resolution time.
4. Ground your playbook in NIST SP 800-61 Rev 2 guidelines.

CRITICAL: Your output MUST be strictly valid JSON. Do NOT include ANY generic text, markdown outside of the JSON block, or `// comments` anywhere inside the JSON structure. If an identity or parameter is missing, output 'UNKNOWN'.

Format your output as structured JSON matching IncidentPlaybook schema.
Format:
{format_instructions}"""


class IncidentResponseAgent(BaseCyberAgent):
    def __init__(self):
        super().__init__(
            "Incident Response", "Playbook generation and containment guidance."
        )
        self.llm = self.get_llm(temperature=0)
        self.parser = PydanticOutputParser(pydantic_object=IncidentPlaybook)
        self.tools = (
            []
        )  # This agent primarily uses LLM reasoning and internal knowledge

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", "Alert received:\n{input}"),
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

            playbook = self.parser.parse(output_text)
            state["playbooks"] = [playbook.model_dump()]
            state["severity_level"] = playbook.severity.value
        except Exception as e:
            print(f"Error parsing IncidentResponse result: {e}")
            state["playbooks"] = [{"error": str(e)}]

        return state
