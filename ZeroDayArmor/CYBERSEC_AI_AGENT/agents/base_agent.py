import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

# Load env variables globally
load_dotenv()


class BaseCyberAgent(ABC):
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.executor: AgentExecutor = None
        self.parser = None

    @abstractmethod
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the agent on the current SecurityState."""
        pass

    def _update_state(
        self, state: Dict[str, Any], key: str, value: Any
    ) -> Dict[str, Any]:
        """Utility to update the state dictionary."""
        if key not in state:
            state[key] = []
        state[key].append(value)
        return state

    @staticmethod
    def get_llm(temperature: float = 0):
        or_key = os.getenv("OPENROUTER_API_KEY")
        if or_key:
            return ChatOpenAI(
                model="openai/gpt-4o-mini",
                api_key=or_key,
                base_url="https://openrouter.ai/api/v1",
                temperature=temperature,
                max_tokens=4000,
            )

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key.startswith("sk-or-"):
            return ChatOpenAI(
                model="openai/gpt-4o-mini",
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                temperature=temperature,
                max_tokens=4000,
            )
        return ChatOpenAI(model="gpt-4o-mini", temperature=temperature, max_tokens=4000)
