from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from financial_coach.config import CANONICAL_TABLES, EXPORT_DIR, UPLOAD_DIR
from financial_coach.config import load_env_file
from financial_coach.currency import format_money
from financial_coach.service import FinancialCoachService

load_env_file()


st.set_page_config(
    page_title="AI Financial Coach Agent",
    page_icon="💼",
    layout="wide",
)


st.markdown(
    """
    <style>
    .narrative-scrollbox {
        max-height: 320px;
        overflow-y: auto;
        padding: 0.75rem 0.9rem;
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 0.5rem;
        background-color: rgba(248, 249, 251, 0.85);
    }

    .narrative-scrollbox pre {
        margin: 0;
        white-space: pre-wrap;
        word-break: break-word;
        font-family: "Source Code Pro", monospace;
        font-size: 0.9rem;
        line-height: 1.45;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def save_uploaded_files(uploaded_files) -> list[Path]:
    saved_paths: list[Path] = []
    for uploaded in uploaded_files:
        target = UPLOAD_DIR / uploaded.name
        target.write_bytes(uploaded.getbuffer())
        saved_paths.append(target)
    return saved_paths


def render_metric_row(state: Dict[str, object]) -> None:
    cash_flow = state["savings_plan"]["cash_flow"]
    currency_code = str(state.get("currency_code", "INR"))
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Net Monthly Income", format_money(float(cash_flow["net_income"]), currency_code))
    col2.metric("Core Expenses", format_money(float(cash_flow["core_expenses"]), currency_code))
    col3.metric("Debt Minimums", format_money(float(cash_flow["debt_minimums"]), currency_code))
    col4.metric("Disposable Income", format_money(float(cash_flow["disposable_income"]), currency_code))


def render_expense_chart(expense_df: pd.DataFrame) -> None:
    if expense_df.empty:
        st.info("No expense data available.")
        return
    grouped = expense_df.groupby("category")["amount"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 4))
    grouped.plot(kind="bar", ax=ax, color="#1f77b4")
    ax.set_ylabel("Monthly spend")
    ax.set_xlabel("")
    ax.set_title("Expense distribution")
    st.pyplot(fig, clear_figure=True)


def render_debt_chart(state: Dict[str, object]) -> None:
    debt_plan = state["debt_plan"]["strategies"]
    chart_df = pd.DataFrame(
        [
            {"strategy": "Snowball", "months": debt_plan["snowball"]["months_to_payoff"], "interest": debt_plan["snowball"]["interest_paid"]},
            {"strategy": "Avalanche", "months": debt_plan["avalanche"]["months_to_payoff"], "interest": debt_plan["avalanche"]["interest_paid"]},
        ]
    )
    fig, ax = plt.subplots(figsize=(6, 4))
    chart_df.plot(kind="bar", x="strategy", y="months", ax=ax, color=["#00897b", "#f57c00"])
    ax.set_ylabel("Months to payoff")
    ax.set_xlabel("")
    ax.set_title("Debt strategy comparison")
    st.pyplot(fig, clear_figure=True)


def render_authorized_tables(tables: Dict[str, pd.DataFrame]) -> None:
    for table_name in CANONICAL_TABLES:
        with st.expander(f"{table_name.title()} table", expanded=False):
            st.dataframe(tables[table_name], use_container_width=True)


def render_chat_history(chat_history: list[dict[str, object]]) -> None:
    for item in chat_history:
        with st.chat_message("user"):
            st.markdown(str(item["question"]))
        with st.chat_message("assistant"):
            st.markdown(str(item["answer"]))


def render_document_hits(document_hits: list[dict[str, object]]) -> None:
    if not document_hits:
        st.info("No document-text hits were needed for this query.")
        return
    for hit in document_hits:
        with st.expander(
            f"Chunk {hit['chunk_id']} | score={hit['score']} | mode={hit['retrieval_mode']}",
            expanded=False,
        ):
            st.write(hit["text"])


def render_ai_technologies() -> None:
    st.markdown(
        """
        ✅ Hugging Face (`LLMs`, embeddings, safety facade)

        ✅ n8n (automation, ingestion, alerts, integrations)

        ✅ LangGraph (multi-agent orchestration)

        ✅ Tabular RAG and Hybrid RAG (data injection from structured files and messy PDFs/CSVs)

        ✅ Ozero FGA (secure fine-grained access control)

        ✅ Streamlit (frontend dashboards)

        ✅ Llama Guard (financial safety guardrails)

        ✅ PyPDF2 and pandas (file ingestion, normalization, analytics)

        ✅ yfinance (live market context with fallback defaults)

        ✅ LangSmith (optional tracing and observability)
        """
    )


@st.dialog("AI technologies", width="large")
def show_ai_technologies_dialog() -> None:
    st.caption("Technologies used across orchestration, ingestion, retrieval, safety, and the UI.")
    render_ai_technologies()


st.title("AI Financial Coach Agent")
st.caption("Secure multi-agent financial coaching with LangGraph, tabular RAG, deterministic math, and guardrailed advice.")

if "analysis_state" not in st.session_state:
    st.session_state.analysis_state = None
if "saved_paths" not in st.session_state:
    st.session_state.saved_paths = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
with st.sidebar:
    st.header("Session")
    user_id = st.text_input("User ID", value="demo-user-001")
    analysis_request = st.text_area(
        "Analysis request",
        value="Create a safe debt payoff, savings, and budget optimization plan for the next 12 months.",
        height=120,
    )
    uploaded_files = st.file_uploader(
        "Upload income, expenses, debts, or assets files",
        type=["csv", "pdf", "xlsx", "xls", "json"],
        accept_multiple_files=True,
    )
    run_analysis = st.button("Run secure analysis", type="primary", use_container_width=True)
    if st.button("AI technologies", use_container_width=True):
        show_ai_technologies_dialog()

service = FinancialCoachService(user_id=user_id.strip() or "demo-user-001")

if run_analysis:
    saved_paths = save_uploaded_files(uploaded_files) if uploaded_files else []
    with st.spinner("Running LangGraph workflow and generating action plan..."):
        state = service.run(query=analysis_request, uploaded_paths=saved_paths)
    st.session_state.analysis_state = state
    st.session_state.saved_paths = saved_paths
    st.session_state.chat_history = []

state = st.session_state.analysis_state
if state:
    render_metric_row(state)

    left, right = st.columns([1.1, 0.9])
    with left:
        st.subheader("Analysis Summary")
        st.info(state["direct_answer"])
        st.subheader("Action Plan")
        for index, item in enumerate(state["action_plan"]["action_items"], start=1):
            st.markdown(f"{index}. {item}")
        st.subheader("Narrative Explanation")
        st.markdown(
            f"""
            <div class="narrative-scrollbox">
                <pre>{state["explanation"]}</pre>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.subheader("Guardrail Status")
        moderation = state["moderation"]
        status = "Approved" if moderation["approved"] else "Blocked"
        st.metric("Llama Guard Decision", status)
        st.json(moderation)
        st.subheader("Market Context")
        st.json(state["market_context"])

    chart_left, chart_right = st.columns(2)
    with chart_left:
        render_expense_chart(state["authorized_tables"]["expenses"])
    with chart_right:
        render_debt_chart(state)

    st.subheader("Budget Opportunities")
    st.dataframe(pd.DataFrame(state["budget_plan"]["opportunities"]), use_container_width=True)

    st.subheader("Authorized Data")
    render_authorized_tables(state["authorized_tables"])

    st.subheader("Retrieval Summary")
    st.json(state["retrieval_summary"])

    st.subheader("Hybrid RAG Document Hits")
    render_document_hits(state.get("document_hits", []))

    st.subheader("Audit Trail")
    st.dataframe(pd.DataFrame(state["audit_log"]), use_container_width=True)

    st.subheader("Ask About This Analysis")
    question = st.chat_input("Ask a question about your savings, debt, budget, or cash flow")
    if question:
        response = service.answer_question(question, state)
        st.session_state.chat_history.append(response)
    if st.session_state.chat_history:
        render_chat_history(st.session_state.chat_history)

    export_path = EXPORT_DIR / f"{user_id}_action_plan.md"
    export_path.write_text(state["explanation"], encoding="utf-8")
    st.success(f"Action plan exported to {export_path}")
else:
    st.info("Run secure analysis first, then use the chat box to ask focused questions about the current results.")
