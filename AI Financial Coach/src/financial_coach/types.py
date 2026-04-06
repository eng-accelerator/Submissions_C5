from __future__ import annotations

from typing import Dict, List, TypedDict

import pandas as pd


class CoachState(TypedDict, total=False):
    user_id: str
    query: str
    run_id: str
    currency_code: str
    raw_text: str
    authorized_tables: Dict[str, pd.DataFrame]
    retrieval_summary: Dict[str, List[str]]
    document_hits: List[Dict[str, object]]
    debt_plan: Dict[str, object]
    savings_plan: Dict[str, object]
    budget_plan: Dict[str, object]
    market_context: Dict[str, object]
    action_plan: Dict[str, object]
    direct_answer: str
    explanation: str
    moderation: Dict[str, object]
    notification_status: Dict[str, object]
    audit_log: List[Dict[str, object]]
