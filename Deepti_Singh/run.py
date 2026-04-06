"""
run.py — CLI runner for testing the research pipeline directly

Usage:
  python run.py "What are the latest breakthroughs in Alzheimer's treatment?"
  python run.py "How is quantum computing affecting cryptography?" --iterations 2
  python run.py "Impact of LLMs on drug discovery" --no-visualize
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

load_dotenv()

console = Console()


def print_header():
    console.print(Panel.fit(
        "[bold blue]🔬 Multi-Agent AI Deep Researcher[/bold blue]\n"
        "[dim]Orchestrator → Clarifier → Retriever → Analyzer → "
        "FactChecker → Insight → Visualizer → Report[/dim]",
        border_style="blue",
    ))


def print_agent_log_table(agent_logs):
    table = Table(title="Agent Execution Summary", show_header=True, header_style="bold cyan")
    table.add_column("Agent", style="bold")
    table.add_column("Status")
    table.add_column("Notes")
    table.add_column("Duration")

    for log in agent_logs:
        status_color = {
            "done":    "green",
            "failed":  "red",
            "running": "yellow",
            "skipped": "dim",
        }.get(log.status, "white")

        duration = ""
        if log.started_at and log.finished_at:
            try:
                s = datetime.fromisoformat(log.started_at)
                e = datetime.fromisoformat(log.finished_at)
                duration = f"{(e - s).total_seconds():.1f}s"
            except Exception:
                pass

        table.add_row(
            log.agent_name,
            f"[{status_color}]{log.status}[/{status_color}]",
            log.notes[:60] if log.notes else log.error or "",
            duration,
        )
    console.print(table)


def run_research(
    query: str,
    max_iterations: int = 2,
    clarification_answer: Optional[str] = None,
):
    from graph import build_graph
    from state import ResearchState

    print_header()
    console.print(f"\n[bold]Query:[/bold] {query}\n")

    graph_app = build_graph(checkpointing=False)

    initial_state = ResearchState(
        original_query=query,
        max_iterations=max_iterations,
        user_clarification_input=clarification_answer,
    ).dict()

    final_state = None
    agent_updates = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        task = progress.add_task("Starting pipeline...", total=None)

        prev_log_count = 0

        for chunk in graph_app.stream(initial_state, stream_mode="values"):
            from state import ResearchState as RS
            current = RS(**chunk)
            final_state = current

            # Show agent updates
            if len(current.agent_logs) > prev_log_count:
                for log in current.agent_logs[prev_log_count:]:
                    icon = {"done": "✓", "running": "▶", "failed": "✗"}.get(log.status, "•")
                    color = {"done": "green", "running": "cyan", "failed": "red"}.get(log.status, "white")
                    progress.update(
                        task,
                        description=f"[{color}]{icon} {log.agent_name}[/{color}] — {log.notes[:50] or ''}",
                    )
                    agent_updates.append(log)
                prev_log_count = len(current.agent_logs)

            # Handle clarification
            if (
                current.clarification_needed
                and not current.clarification_complete
                and current.clarification_questions
            ):
                progress.stop()
                console.print("\n[yellow]⚠ Clarification needed:[/yellow]")
                for q in current.clarification_questions:
                    console.print(f"  • {q.question}")
                answer = console.input("\n[bold]Your answer:[/bold] ").strip()
                # Restart with clarification
                new_state = current.dict()
                new_state["user_clarification_input"] = answer
                new_state["clarification_needed"] = False
                for chunk2 in graph_app.stream(new_state, stream_mode="values"):
                    final_state = RS(**chunk2)
                break

    if not final_state:
        console.print("[red]Pipeline produced no output.[/red]")
        return

    # ── Print results ──────────────────────────
    console.print("\n")
    print_agent_log_table(final_state.agent_logs)

    # Sources
    console.print(f"\n[bold]📚 Sources Retrieved:[/bold] {len(final_state.verified_sources)}")
    for s in final_state.verified_sources[:5]:
        console.print(
            f"  • [{s.credibility_score:.0%}] [link={s.url}]{s.title[:70]}[/link] "
            f"({s.source_type})"
        )

    # Insights
    if final_state.insights:
        console.print(f"\n[bold]💡 Insights Generated:[/bold] {len(final_state.insights)}")
        for ins in final_state.insights:
            console.print(f"  • [{ins.category}] {ins.hypothesis[:100]}")

    # Contradictions
    if final_state.contradictions:
        console.print(f"\n[bold]⚡ Contradictions Found:[/bold] {len(final_state.contradictions)}")
        for c in final_state.contradictions[:3]:
            console.print(f"  • [{c.severity}] {c.explanation[:100]}")

    # Visualizations
    if final_state.visualization_paths:
        console.print(f"\n[bold]📊 Charts Generated:[/bold]")
        for p in final_state.visualization_paths:
            console.print(f"  • {p}")

    # Report
    if final_state.final_report_md:
        console.print(f"\n[bold]📄 Report saved to:[/bold] {final_state.final_report_path}\n")
        show_report = console.input("Show full report in terminal? [y/N]: ").strip().lower()
        if show_report == "y":
            console.print(Markdown(final_state.final_report_md))
    else:
        console.print("\n[red]No report was generated.[/red]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Agent AI Deep Researcher CLI")
    parser.add_argument("query", help="Research question to investigate")
    parser.add_argument(
        "--iterations", type=int, default=2,
        help="Max research loop iterations (default: 2)"
    )
    parser.add_argument(
        "--answer", type=str, default=None,
        help="Pre-supply clarification answer (skips interactive prompt)"
    )
    args = parser.parse_args()

    try:
        run_research(
            query=args.query,
            max_iterations=args.iterations,
            clarification_answer=args.answer,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
