"""
api.py — FastAPI Backend for Multi-Agent Deep Researcher

Endpoints:
  POST /research/start         — Start a new research session
  POST /research/{id}/clarify  — Submit clarification answer
  GET  /research/{id}/stream   — SSE stream of agent progress
  GET  /research/{id}/status   — Current state summary
  GET  /research/{id}/report   — Final report (markdown)
  GET  /research/{id}/sources  — Verified sources list
  GET  /health                 — Health check

Design:
  - Each research job runs in a background thread
  - State is stored in-memory (replace with Redis for prod)
  - SSE streams agent log events to frontend in real-time
  - LangGraph MemorySaver handles graph checkpointing
"""

from __future__ import annotations

import asyncio
import json
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from loguru import logger
from pydantic import BaseModel

from graph import get_app
from state import AgentStatus, ResearchState

load_dotenv()

# ──────────────────────────────────────────────
# App setup
# ──────────────────────────────────────────────

app = FastAPI(
    title="Multi-Agent AI Deep Researcher",
    description=(
        "An AI-powered research assistant with specialized agents: "
        "Orchestrator, Query Clarifier, Contextual Retriever (with Agentic RAG), "
        "Critical Analyzer, Fact Checker, Insight Generator, Report Builder, "
        "and Visualizer."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# In-memory session store
# (swap for Redis / DB in production)
# ──────────────────────────────────────────────

class ResearchSession:
    def __init__(self, session_id: str, query: str):
        self.session_id = session_id
        self.query = query
        self.state: Optional[ResearchState] = None
        self.status: str = "initializing"   # initializing|clarifying|running|done|error
        self.events: List[Dict] = []         # SSE event log
        self.created_at: str = datetime.now(timezone.utc).isoformat()
        self.finished_at: Optional[str] = None
        self.thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def push_event(self, event_type: str, data: Any):
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with self._lock:
            self.events.append(event)


SESSIONS: Dict[str, ResearchSession] = {}

# ──────────────────────────────────────────────
# Request / Response models
# ──────────────────────────────────────────────

class StartRequest(BaseModel):
    query: str
    max_iterations: int = 2


class ClarifyRequest(BaseModel):
    answer: str


class StatusResponse(BaseModel):
    session_id: str
    status: str
    query: str
    agent_logs: List[Dict]
    clarification_questions: List[Dict]
    sources_count: int
    insights_count: int
    contradictions_count: int
    created_at: str
    finished_at: Optional[str]


# ──────────────────────────────────────────────
# Graph runner (runs in background thread)
# ──────────────────────────────────────────────

def _run_graph(session: ResearchSession, initial_state: dict, thread_id: str):
    """Execute the LangGraph pipeline in a background thread."""
    try:
        graph_app = get_app(checkpointing=True)
        config = {"configurable": {"thread_id": thread_id}}

        session.push_event("pipeline_start", {"message": "Research pipeline started"})

        prev_logs_count = 0

        for chunk in graph_app.stream(initial_state, config=config, stream_mode="values"):
            # Detect new agent log entries and push as events
            current_state = ResearchState(**chunk)
            current_logs = current_state.agent_logs

            if len(current_logs) > prev_logs_count:
                for log in current_logs[prev_logs_count:]:
                    session.push_event("agent_update", {
                        "agent": log.agent_name,
                        "status": log.status,
                        "notes": log.notes,
                        "error": log.error,
                    })
                prev_logs_count = len(current_logs)

            # Check for clarification pause
            if (
                current_state.clarification_needed
                and not current_state.clarification_complete
                and current_state.clarification_questions
            ):
                session.status = "clarifying"
                session.state = current_state
                session.push_event("clarification_needed", {
                    "questions": [
                        {"question": q.question, "purpose": q.purpose}
                        for q in current_state.clarification_questions
                    ]
                })
                logger.info(f"[Runner] Session {session.session_id} paused for clarification.")
                return  # stop streaming; will resume after user answers

            session.state = current_state

        # Final state
        session.state = current_state
        session.status = "done" if not current_state.error_message else "error"
        session.finished_at = datetime.now(timezone.utc).isoformat()

        session.push_event("pipeline_complete", {
            "report_path": current_state.final_report_path,
            "sources": len(current_state.verified_sources),
            "insights": len(current_state.insights),
            "visualizations": len(current_state.visualization_paths),
        })
        logger.info(f"[Runner] Session {session.session_id} completed.")

    except Exception as e:
        logger.exception(f"[Runner] Fatal error in session {session.session_id}: {e}")
        session.status = "error"
        session.finished_at = datetime.now(timezone.utc).isoformat()
        session.push_event("error", {"message": str(e)})


def _resume_graph(session: ResearchSession, thread_id: str):
    """Resume pipeline after clarification is answered."""
    try:
        graph_app = get_app(checkpointing=True)
        config = {"configurable": {"thread_id": thread_id}}

        # Get current checkpoint state and update with clarification
        state_dict = session.state.model_dump()
        state_dict["clarification_complete"] = True
        state_dict["clarification_needed"] = False

        session.status = "running"
        session.push_event("pipeline_resumed", {"message": "Continuing research after clarification"})

        prev_logs_count = len(session.state.agent_logs)

        for chunk in graph_app.stream(state_dict, config=config, stream_mode="values"):
            current_state = ResearchState(**chunk)
            current_logs = current_state.agent_logs

            if len(current_logs) > prev_logs_count:
                for log in current_logs[prev_logs_count:]:
                    session.push_event("agent_update", {
                        "agent": log.agent_name,
                        "status": log.status,
                        "notes": log.notes,
                        "error": log.error,
                    })
                prev_logs_count = len(current_logs)

            session.state = current_state

        session.status = "done"
        session.finished_at = datetime.now(timezone.utc).isoformat()
        session.push_event("pipeline_complete", {
            "report_path": current_state.final_report_path,
            "sources": len(current_state.verified_sources),
            "insights": len(current_state.insights),
        })

    except Exception as e:
        logger.exception(f"[Resume] Error: {e}")
        session.status = "error"
        session.push_event("error", {"message": str(e)})


# ──────────────────────────────────────────────
# API Endpoints
# ──────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/research/start", status_code=202)
def start_research(req: StartRequest):
    """
    Start a new research session.
    Returns session_id immediately; pipeline runs in background.
    """
    session_id = str(uuid.uuid4())
    thread_id = f"thread_{session_id}"

    session = ResearchSession(session_id=session_id, query=req.query)
    SESSIONS[session_id] = session
    session.status = "running"

    initial_state = ResearchState(
        original_query=req.query,
        max_iterations=req.max_iterations,
    ).model_dump()

    # Launch in background thread
    t = threading.Thread(
        target=_run_graph,
        args=(session, initial_state, thread_id),
        daemon=True,
    )
    t.start()
    session.thread = t

    logger.info(f"[API] Started session {session_id} for query: '{req.query[:60]}'")
    return {
        "session_id": session_id,
        "status": "running",
        "message": "Research pipeline started. Stream events at /research/{session_id}/stream",
    }


@app.post("/research/{session_id}/clarify")
def submit_clarification(session_id: str, req: ClarifyRequest):
    """
    Submit the user's answer to clarification questions.
    Resumes the pipeline from where it paused.
    """
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    if session.status != "clarifying":
        raise HTTPException(400, f"Session is not waiting for clarification (status={session.status})")

    if session.state:
        session.state.user_clarification_input = req.answer

    thread_id = f"thread_{session_id}"
    t = threading.Thread(
        target=_resume_graph,
        args=(session, thread_id),
        daemon=True,
    )
    t.start()
    session.thread = t

    return {"message": "Clarification received. Pipeline resuming."}


@app.get("/research/{session_id}/stream")
async def stream_events(session_id: str):
    """
    SSE endpoint — streams agent progress events to the client.
    Events: agent_update | clarification_needed | pipeline_complete | error
    """
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    async def event_generator() -> AsyncGenerator[str, None]:
        sent_index = 0
        max_wait = 600  # 10 minutes timeout
        elapsed = 0

        while elapsed < max_wait:
            with session._lock:
                new_events = session.events[sent_index:]

            for event in new_events:
                payload = json.dumps(event)
                yield f"data: {payload}\n\n"
                sent_index += 1

            if session.status in ("done", "error", "clarifying"):
                # Send final heartbeat
                yield f"data: {json.dumps({'type': 'stream_end', 'status': session.status})}\n\n"
                break

            await asyncio.sleep(0.5)
            elapsed += 0.5

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/research/{session_id}/status", response_model=StatusResponse)
def get_status(session_id: str):
    """Get current status and summary stats for a session."""
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    state = session.state
    return StatusResponse(
        session_id=session_id,
        status=session.status,
        query=session.query,
        agent_logs=[log.model_dump() for log in (state.agent_logs if state else [])],
        clarification_questions=[
            q.model_dump() for q in (state.clarification_questions if state else [])
        ],
        sources_count=len(state.verified_sources) if state else 0,
        insights_count=len(state.insights) if state else 0,
        contradictions_count=len(state.contradictions) if state else 0,
        created_at=session.created_at,
        finished_at=session.finished_at,
    )


@app.get("/research/{session_id}/report")
def get_report(session_id: str, format: str = "json"):
    """
    Retrieve the final research report.
    format=json → returns structured JSON
    format=md   → returns raw Markdown
    format=file → returns Markdown file download
    """
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    if session.status not in ("done",):
        raise HTTPException(425, f"Report not ready yet (status={session.status})")

    state = session.state
    if not state or not state.final_report_md:
        raise HTTPException(500, "Report not found in state")

    if format == "md":
        return JSONResponse({"report": state.final_report_md})

    if format == "file" and state.final_report_path:
        return FileResponse(
            state.final_report_path,
            media_type="text/markdown",
            filename=f"report_{session_id[:8]}.md",
        )

    # Default: rich JSON
    return {
        "session_id": session_id,
        "query": session.query,
        "report_markdown": state.final_report_md,
        "report_path": state.final_report_path,
        "metadata": {
            "sources_count": len(state.verified_sources),
            "insights_count": len(state.insights),
            "contradictions_count": len(state.contradictions),
            "visualizations": state.visualization_paths,
            "key_themes": state.key_themes,
            "sub_queries": state.sub_queries,
            "agent_logs": [l.model_dump() for l in state.agent_logs],
        },
    }


@app.get("/research/{session_id}/sources")
def get_sources(session_id: str):
    """Return all verified sources with credibility scores and summaries."""
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    state = session.state
    if not state:
        return {"sources": []}

    return {
        "session_id": session_id,
        "sources": [
            {
                **s.model_dump(),
                "summary": state.summary_per_source.get(s.id, ""),
                "fact_check": state.fact_check_results.get(s.id, {}),
            }
            for s in state.verified_sources
        ],
    }


@app.get("/research/{session_id}/insights")
def get_insights(session_id: str):
    """Return all insights with reasoning chains."""
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    state = session.state
    if not state:
        return {"insights": []}

    return {
        "session_id": session_id,
        "insights": [i.model_dump() for i in state.insights],
        "contradictions": [c.model_dump() for c in state.contradictions],
        "key_themes": state.key_themes,
    }


@app.get("/sessions")
def list_sessions():
    """List all research sessions (admin view)."""
    return {
        "sessions": [
            {
                "session_id": sid,
                "query": s.query[:80],
                "status": s.status,
                "created_at": s.created_at,
            }
            for sid, s in SESSIONS.items()
        ]
    }


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
