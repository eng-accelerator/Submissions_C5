"""
Application settings — single source of truth for all configuration.
Every secret, URL, feature flag, and tunable lives in backend/.env.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    app_env: str = Field(default="development")
    app_debug: bool = Field(default=False)

    # --- CORS ---
    cors_allowed_origins: str = Field(
        ...,
        description="Comma-separated browser origins allowed to call this API.",
    )

    # --- Supabase ---
    supabase_url: str = Field(default="")
    supabase_anon_key: str = Field(default="")
    supabase_service_role_key: str = Field(default="")

    # --- LLM Provider ---
    llm_provider: str = Field(default="openrouter")  # openrouter | openai

    # --- OpenRouter (default, cheap models) ---
    openrouter_api_key: str = Field(default="")
    openrouter_model: str = Field(default="google/gemini-2.0-flash-001")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1")

    # --- OpenAI (optional, direct) ---
    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4o")
    openai_embedding_model: str = Field(default="text-embedding-3-small")

    # --- LangSmith ---
    langchain_tracing_v2: bool = Field(default=False)
    langchain_api_key: str = Field(default="")
    langchain_project: str = Field(default="demoai")

    # --- Agents ---
    agent_max_iterations: int = Field(default=15)
    agent_temperature: float = Field(default=0.1)
    agent_timeout_seconds: int = Field(default=120)

    # --- Session / Memory ---
    session_ttl_hours: int = Field(default=24)
    max_memory_messages: int = Field(default=50)

    # --- Documents ---
    max_upload_size_mb: int = Field(default=10)
    allowed_file_types: str = Field(default="pdf,csv,json,xlsx,png,jpg,jpeg,webp")

    @field_validator("supabase_url", mode="before")
    @classmethod
    def normalize_supabase_url(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip().rstrip("/")
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]

    @property
    def allowed_file_types_list(self) -> list[str]:
        return [t.strip() for t in self.allowed_file_types.split(",") if t.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
