import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load .env into os.environ BEFORE any LangChain import.
# LangChain reads LANGCHAIN_* vars directly from os.environ, not from Pydantic.
from app.settings import _BACKEND_ROOT
load_dotenv(_BACKEND_ROOT / ".env", override=True)

from fastapi.staticfiles import StaticFiles

from app.routes import blog, chat, dashboard, documents, plan
from app.settings import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log LangSmith status at startup
if os.environ.get("LANGCHAIN_TRACING_V2", "").lower() == "true":
    logger.info("LangSmith tracing ENABLED — project: %s", os.environ.get("LANGCHAIN_PROJECT", "default"))
else:
    logger.info("LangSmith tracing disabled")

app = FastAPI(
    title="DemoAI Financial Coach API",
    description="Multi-agent AI financial advisor with RAG",
    version="0.2.0",
)

_settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(chat.router)
app.include_router(dashboard.router)
app.include_router(documents.router)
app.include_router(blog.router)
app.include_router(plan.router)

# Serve generated blog media (images, audio) as static files
_media_dir = _BACKEND_ROOT / "app" / "data" / "blogs"
_media_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media/blogs", StaticFiles(directory=str(_media_dir)), name="blog-media")


@app.get("/health")
async def health_check() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "version": "0.2.0",
        "agents": ["orchestrator", "debt_analyzer", "savings_strategist", "budget_advisor", "payoff_optimizer"],
        "config": {
            "llm_provider": settings.llm_provider,
            "llm_model": settings.openrouter_model if settings.llm_provider == "openrouter" else settings.openai_model,
            "openrouter_connected": bool(settings.openrouter_api_key and settings.openrouter_api_key != "sk-or-REPLACE_ME"),
            "openai_connected": bool(settings.openai_api_key and settings.openai_api_key != "sk-REPLACE_ME"),
            "langsmith_enabled": settings.langchain_tracing_v2,
            "langsmith_project": settings.langchain_project if settings.langchain_tracing_v2 else None,
            "langsmith_key_set": bool(settings.langchain_api_key and settings.langchain_api_key != "lsv2_REPLACE_ME"),
            "supabase_connected": bool(settings.supabase_url and "your-project" not in settings.supabase_url),
        },
    }
