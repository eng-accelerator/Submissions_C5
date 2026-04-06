from __future__ import annotations

from langgraph.graph import END, StateGraph

from financial_coach.agents import BudgetOptimizationAgent, DebtAnalyzerAgent, FinancialCoachOrchestrator, SavingsStrategyAgent
from financial_coach.market import fetch_market_context
from financial_coach.rag import TabularRagAgent
from financial_coach.types import CoachState


def build_financial_graph(tabular_rag: TabularRagAgent):
    debt_agent = DebtAnalyzerAgent()
    savings_agent = SavingsStrategyAgent()
    budget_agent = BudgetOptimizationAgent()
    orchestrator = FinancialCoachOrchestrator()

    def _authorize_for_action(state: CoachState, action: str) -> None:
        authorized = {}
        for table_name, frame in state["authorized_tables"].items():
            table_frame = tabular_rag.fga_client.authorize_table(state["user_id"], table_name, frame, action)
            row_frame = tabular_rag.fga_client.authorize_rows(state["user_id"], table_name, table_frame, action)
            authorized[table_name] = row_frame
        state["authorized_tables"] = authorized

    def retrieve_data(state: CoachState) -> CoachState:
        bundle = tabular_rag.retrieve(
            state["user_id"],
            state["query"],
            state["authorized_tables"],
            raw_text=state.get("raw_text", ""),
        )
        state["authorized_tables"] = bundle.tables
        state["retrieval_summary"] = bundle.summaries
        state["document_hits"] = [
            {
                "chunk_id": hit.chunk_id,
                "score": hit.score,
                "retrieval_mode": hit.retrieval_mode,
                "text": hit.text,
            }
            for hit in bundle.document_hits
        ]
        state["audit_log"] = state.get("audit_log", []) + [
            {"step": "tabular_rag", "summary": bundle.summaries}
        ]
        return state

    def collect_market_context(state: CoachState) -> CoachState:
        state["market_context"] = fetch_market_context()
        state["audit_log"] = state.get("audit_log", []) + [
            {"step": "market_context", "summary": state["market_context"]}
        ]
        return state

    def debt_analysis(state: CoachState) -> CoachState:
        _authorize_for_action(state, "calculate")
        income_df = state["authorized_tables"]["income"]
        expense_df = state["authorized_tables"]["expenses"]
        debt_df = state["authorized_tables"]["debts"]
        cash_flow = state.get("savings_plan", {}).get("cash_flow")
        if not cash_flow:
            cash_flow = savings_agent.analyze(
                income_df,
                expense_df,
                debt_df,
                state["authorized_tables"]["assets"],
            )["cash_flow"]
        state["debt_plan"] = debt_agent.analyze(debt_df, cash_flow)
        state["audit_log"] = state.get("audit_log", []) + [
            {"step": "debt_analysis", "summary": state["debt_plan"]}
        ]
        return state

    def savings_analysis(state: CoachState) -> CoachState:
        _authorize_for_action(state, "calculate")
        state["savings_plan"] = savings_agent.analyze(
            state["authorized_tables"]["income"],
            state["authorized_tables"]["expenses"],
            state["authorized_tables"]["debts"],
            state["authorized_tables"]["assets"],
        )
        state["audit_log"] = state.get("audit_log", []) + [
            {"step": "savings_analysis", "summary": state["savings_plan"]}
        ]
        return state

    def budget_analysis(state: CoachState) -> CoachState:
        _authorize_for_action(state, "calculate")
        state["budget_plan"] = budget_agent.analyze(state["authorized_tables"]["expenses"])
        state["audit_log"] = state.get("audit_log", []) + [
            {"step": "budget_analysis", "summary": state["budget_plan"]}
        ]
        return state

    def orchestrate(state: CoachState) -> CoachState:
        _authorize_for_action(state, "explain")
        result = orchestrator.assemble(
            user_id=state["user_id"],
            query=state["query"],
            cash_flow=state["savings_plan"]["cash_flow"],
            debt_plan=state["debt_plan"],
            savings_plan=state["savings_plan"],
            budget_plan=state["budget_plan"],
            market_context=state["market_context"],
            currency_code=state.get("currency_code", "INR"),
        )
        state["action_plan"] = {"action_items": result["action_items"]}
        state["direct_answer"] = result["direct_answer"]
        state["explanation"] = result["explanation"]
        state["moderation"] = result["moderation"]
        state["audit_log"] = state.get("audit_log", []) + [
            {"step": "orchestrate", "summary": state["action_plan"]},
            {"step": "moderation", "summary": state["moderation"]},
        ]
        return state

    graph = StateGraph(CoachState)
    graph.add_node("retrieve_data", retrieve_data)
    graph.add_node("collect_market_context", collect_market_context)
    graph.add_node("savings_analysis", savings_analysis)
    graph.add_node("debt_analysis", debt_analysis)
    graph.add_node("budget_analysis", budget_analysis)
    graph.add_node("orchestrate", orchestrate)

    graph.set_entry_point("retrieve_data")
    graph.add_edge("retrieve_data", "collect_market_context")
    graph.add_edge("collect_market_context", "savings_analysis")
    graph.add_edge("savings_analysis", "debt_analysis")
    graph.add_edge("debt_analysis", "budget_analysis")
    graph.add_edge("budget_analysis", "orchestrate")
    graph.add_edge("orchestrate", END)

    return graph.compile()
