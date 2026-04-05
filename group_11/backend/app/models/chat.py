"""Chat request/response models."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatMessage(BaseModel):
    role: str  # user, assistant
    content: str
    agent_name: str | None = None


class ChatResponse(BaseModel):
    message: str
    agent_name: str
    agent_display_name: str
    session_id: str
