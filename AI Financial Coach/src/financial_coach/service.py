from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional
from uuid import uuid4

import pandas as pd

from financial_coach.auth import OzeroFgaClient, build_demo_policy_store
from financial_coach.audit import AuditEvent, AuditLogger
from financial_coach.agents import FinancialCoachOrchestrator
from financial_coach.currency import detect_currency_code
from financial_coach.demo_data import build_demo_raw_text, build_demo_tables
from financial_coach.graph import build_financial_graph
from financial_coach.ingestion import ingest_structured_files
from financial_coach.notifications import NotificationDispatcher
from financial_coach.rag import TabularRagAgent
from financial_coach.tracing import build_langgraph_config, langsmith_enabled, langsmith_project
from financial_coach.types import CoachState


class FinancialCoachService:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.fga_client = OzeroFgaClient(build_demo_policy_store(user_id))
        self.rag_agent = TabularRagAgent(self.fga_client)
        self.graph = build_financial_graph(self.rag_agent)
        self.orchestrator = FinancialCoachOrchestrator()
        self.audit_logger = AuditLogger()
        self.notifier = NotificationDispatcher()

    def load_data_bundle(self, uploaded_paths: Optional[Iterable[Path]] = None) -> Dict[str, object]:
        paths = [Path(path) for path in uploaded_paths or []]
        if paths:
            result = ingest_structured_files(paths, user_id=self.user_id)
            return {"tables": result.tables, "raw_text": result.raw_text}
        return {"tables": build_demo_tables(self.user_id), "raw_text": build_demo_raw_text(self.user_id)}

    def load_tables(self, uploaded_paths: Optional[Iterable[Path]] = None) -> Dict[str, pd.DataFrame]:
        bundle = self.load_data_bundle(uploaded_paths)
        return bundle["tables"]

    def run(
        self,
        query: str,
        uploaded_paths: Optional[List[Path]] = None,
        source: str = "streamlit",
        send_notifications: bool = False,
    ) -> CoachState:
        run_id = str(uuid4())
        data_bundle = self.load_data_bundle(uploaded_paths)
        tables = data_bundle["tables"]
        raw_text = str(data_bundle.get("raw_text", ""))
        self.audit_logger.log_event(
            AuditEvent(
                event_type="analysis_requested",
                user_id=self.user_id,
                source=source,
                run_id=run_id,
                payload={
                    "query": query,
                    "uploaded_paths": [str(path) for path in uploaded_paths or []],
                    "table_counts": {name: len(frame) for name, frame in tables.items()},
                },
            )
        )
        initial_state: CoachState = {
            "user_id": self.user_id,
            "query": query,
            "currency_code": detect_currency_code(tables),
            "raw_text": raw_text,
            "authorized_tables": tables,
            "audit_log": [],
        }
        invoke_config = build_langgraph_config(
            run_name="financial_coach_analysis",
            tags=["financial-coach", source, self.user_id],
            metadata={
                "user_id": self.user_id,
                "source": source,
                "run_id": run_id,
                "query": query,
                "langsmith_enabled": langsmith_enabled(),
                "langsmith_project": langsmith_project(),
            },
        )
        result = self.graph.invoke(initial_state, config=invoke_config)
        result["run_id"] = run_id
        self.audit_logger.log_event(
            AuditEvent(
                event_type="analysis_completed",
                user_id=self.user_id,
                source=source,
                run_id=run_id,
                payload={
                    "action_items": result.get("action_plan", {}).get("action_items", []),
                    "moderation": result.get("moderation", {}),
                    "graph_audit_steps": len(result.get("audit_log", [])),
                },
            )
        )
        if send_notifications:
            notification_result = self.notifier.dispatch(
                "analysis_completed",
                {
                    "user_id": self.user_id,
                    "run_id": run_id,
                    "action_items": result.get("action_plan", {}).get("action_items", []),
                    "moderation": result.get("moderation", {}),
                },
            )
            result["notification_status"] = notification_result
            self.audit_logger.log_event(
                AuditEvent(
                    event_type="notification_dispatched",
                    user_id=self.user_id,
                    source=source,
                    run_id=run_id,
                    payload=notification_result,
                )
            )
        return result

    def answer_question(self, question: str, state: CoachState) -> Dict[str, object]:
        answer = self.orchestrator.answer_chat_question(question, state)
        moderation = self.orchestrator.moderator.moderate(question, answer)
        return {
            "question": question,
            "answer": answer,
            "moderation": moderation,
            "tracing": {
                "langsmith_enabled": langsmith_enabled(),
                "langsmith_project": langsmith_project(),
            },
        }
