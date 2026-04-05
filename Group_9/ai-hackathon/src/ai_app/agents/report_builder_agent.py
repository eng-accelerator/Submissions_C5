from __future__ import annotations

from collections import defaultdict

from ai_app.agents.base import AgentBase
from ai_app.retrieval.citation_builder import format_inline_citations, format_reference_entry, order_sources_for_citation
from ai_app.retrieval.time_filters import describe_date_window
from ai_app.domain.enums import SourceChannel
from ai_app.schemas.research import Claim, Contradiction, ReportSection, ResearchSession


def _credibility_winner_phrase(ctr: Contradiction) -> str:
    if ctr.more_credible_side == "a":
        return f"**{ctr.source_a_label}** (heuristic lean)"
    if ctr.more_credible_side == "b":
        return f"**{ctr.source_b_label}** (heuristic lean)"
    return "**No clear lean (credibility tie)**"


class ReportBuilderAgent(AgentBase):
    name = "report_builder_agent"

    async def run(self, session: ResearchSession) -> ResearchSession:
        ordered_sources = order_sources_for_citation(session.sources)
        source_map = {source.id: source for source in ordered_sources}
        rag_sources = [source for source in ordered_sources if source.provider == "local_rag"]
        web_sources = [source for source in ordered_sources if source.provider == "tavily" and source.source_type.value == "web"]
        news_sources = [source for source in ordered_sources if source.provider == "tavily" and source.source_type.value == "news"]
        arxiv_sources = [source for source in ordered_sources if source.provider == "arxiv"]
        enabled_sources = ", ".join(source.value for source in session.enabled_sources)
        date_window = describe_date_window(session.start_date, session.end_date)

        summary = (
            session.claims[0].statement if session.claims else "Research session completed with limited evidence."
        )
        methodology = "\n".join(
            [
                f"- Query: {session.query}",
                f"- Run mode: {session.run_mode.value}",
                f"- Depth: {session.depth.value}",
                f"- Enabled sources: {enabled_sources}",
                f"- Date window applied to external sources: {date_window}",
                f"- Sub-questions investigated: {len(session.sub_questions)}",
                f"- Sources collected: {len(ordered_sources)}",
                f"- Findings collected: {len(session.findings)}",
                f"- Claims generated: {len(session.claims)}",
                "- Retrieval policy: local corpus first, then public enrichment when local evidence is incomplete.",
                "- Local RAG note: uploaded and indexed local documents remain eligible even when external date filters are narrow, because local files may not carry reliable publication metadata.",
            ]
        )
        source_strategy = "\n".join(
            [
                f"- Local RAG enabled: {'yes' if SourceChannel.LOCAL_RAG in session.enabled_sources else 'no'}",
                f"- Web/Tavily enabled: {'yes' if SourceChannel.WEB in session.enabled_sources else 'no'}",
                f"- arXiv enabled: {'yes' if SourceChannel.ARXIV in session.enabled_sources else 'no'}",
                "- Local evidence is prioritized in both ranking and inline citation order.",
                "- External sources are ranked by relevance, credibility, metadata completeness, date-window fit, and corroboration.",
            ]
        )

        findings_by_question: dict[str, list[str]] = defaultdict(list)
        for finding in session.findings:
            linked_sources = [source_map[source_id] for source_id in finding.source_ids if source_id in source_map]
            citation = format_inline_citations(linked_sources[:4]) if linked_sources else "No citation available"
            snippet_line = f"  Snippet: {finding.quote_excerpt or finding.snippet}" if (finding.quote_excerpt or finding.snippet) else ""
            findings_by_question[finding.sub_question].append(
                f"- {finding.content}\n{snippet_line}\n  Citations: {citation}"
            )
        evidence_synthesis = "\n\n".join(
            f"### {question}\n" + "\n".join(entries[:5])
            for question, entries in findings_by_question.items()
        ) or "No evidence synthesis available."

        ctr_by_claim: dict[str, list[Contradiction]] = defaultdict(list)
        seen_pair: set[tuple[str, str]] = set()
        for item in session.contradictions:
            for cid in (item.claim_a_id, item.claim_b_id):
                if not cid:
                    continue
                key = (cid, item.id)
                if key in seen_pair:
                    continue
                seen_pair.add(key)
                ctr_by_claim[cid].append(item)

        finding_blocks: list[str] = []
        for claim in session.claims[:12]:
            cites = format_inline_citations(
                [source_map[source_id] for source_id in claim.supporting_source_ids if source_id in source_map][:4]
            ) or "No citation available"
            block = (
                f"- {claim.statement}\n"
                f"  Confidence: {claim.confidence.value} ({claim.confidence_pct}%), Trust: {claim.trust_score}%, "
                f"Consensus across sources: {claim.consensus_pct}%\n"
                f"  Credibility: {claim.credibility_summary}\n"
                f"  Evidence: {claim.evidence_summary}\n"
                f"  Citations: {cites}"
            )
            for ctr in ctr_by_claim.get(claim.id, [])[:2]:
                block += (
                    f"\n  **Where sources disagree:** **{ctr.source_a_label}** says: {ctr.position_a}\n"
                    f"  **{ctr.source_b_label}** says: {ctr.position_b}\n"
                    f"  **Credibility read:** {_credibility_winner_phrase(ctr)} — {ctr.credibility_reasoning}"
                )
            finding_blocks.append(block)
        detailed_findings = "\n".join(finding_blocks) if finding_blocks else "- No claims generated."

        if session.contradictions:
            disagreement_parts: list[str] = []
            for item in session.contradictions[:12]:
                disagreement_parts.append(
                    "\n".join(
                        [
                            f"### {item.source_a_label} vs {item.source_b_label}",
                            f"- **{item.source_a_label}** says: {item.position_a}",
                            f"- **{item.source_b_label}** says: {item.position_b}",
                            f"- **Why this tension matters:** {item.analysis}",
                            f"- **Heuristic lean:** {_credibility_winner_phrase(item)}",
                            f"- **Reasoning:** {item.credibility_reasoning}",
                        ]
                    )
                )
            disagreements_md = "\n\n".join(disagreement_parts)
        else:
            disagreements_md = (
                "- No strong pairwise contradictions were detected among generated claims. "
                "Still verify conclusions when evidence is sparse, undated, or drawn from a single channel."
            )

        def _contested_for_section(claim: Claim) -> bool:
            return claim.consensus_pct < 60 or (claim.contested and claim.consensus_pct < 72)

        contested_pool = [c for c in session.claims if _contested_for_section(c)]
        contested_pool = sorted(contested_pool, key=lambda c: (c.consensus_pct, c.trust_score))[:15]
        if contested_pool:
            contested_lines: list[str] = [
                "These claims show **low consensus** (conflicting sources, weak corroboration, or explicit tension). "
                "Use them as review anchors—not as settled facts."
            ]
            for claim in contested_pool:
                contested_cites = format_inline_citations(
                    [source_map[sid] for sid in claim.supporting_source_ids if sid in source_map][:4]
                ) or "No citation available"
                tension_cites = format_inline_citations(
                    [source_map[sid] for sid in claim.contradicting_source_ids if sid in source_map][:4]
                ) or "n/a"
                contested_lines.append(
                    "\n".join(
                        [
                            f"### Consensus {claim.consensus_pct}% — contested claim",
                            f"- **Statement:** {claim.statement}",
                            f"- **Signals:** contested={claim.contested}, weak_evidence={claim.weak_evidence}, "
                            f"supporting_sources={len(claim.supporting_source_ids)}, tension_sources={len(claim.contradicting_source_ids)}",
                            f"- **Interpretation:** {claim.reasoning}",
                            f"- **Evidence summary:** {claim.evidence_summary}",
                            f"- **Supporting citations:** {contested_cites}",
                            f"- **Sources in tension (if any):** {tension_cites}",
                        ]
                    )
                )
            contested_claims_md = "\n\n".join(contested_lines)
        else:
            contested_claims_md = (
                "- No claims fell below the consensus threshold for this run. "
                "If you narrow sources or add uploads, re-check this section after a new pass."
            )

        credibility_methodology = "\n".join(
            [
                "- Source credibility score is a weighted heuristic:",
                "  source-type weight (35%), provider trust (20%), metadata completeness (15%), date-window fit (15%), and cross-source agreement (15%).",
                "- Scores do not claim absolute truth; they communicate how strongly the retrieved evidence should be trusted relative to other collected material.",
                "",
                *[
                    f"- {(source.filename or source.title)} [{source.provider}] -> {source.credibility_score:.2f}. {source.credibility_explanation}"
                    for source in ordered_sources[:12]
                ],
            ]
        ) or "- No credibility data available."

        insights = "\n".join(
            f"- {insight.label}: {insight.content}\n  Evidence: {format_inline_citations([source_map[source_id] for source_id in insight.evidence_chain if source_id in source_map][:5]) or 'No citation available'}"
            for insight in session.insights[:10]
        ) or "- No insights generated."

        follow_ups = "\n".join(
            f"- {question.question}\n  Why it matters: {question.rationale}"
            for question in session.follow_up_questions[:8]
        ) or "- No follow-up questions."

        limitations = "\n".join(
            [
                "- Local documents may not always have reliable publication metadata, so date filtering is strongest for external web and arXiv sources.",
                "- Some web results may not expose publication dates; these are included with lower time-window certainty when otherwise relevant.",
                "- Findings without corroborating sources are retained but marked as lower-confidence evidence.",
            ]
        )

        rag_references = "\n".join(
            f"- {source.filename or source.title} | pages={','.join(str(page) for page in source.page_refs) if source.page_refs else 'n/a'} | snippet={source.snippet} | credibility={source.credibility_score:.2f}"
            for source in rag_sources[:30]
        ) or "- No local RAG references collected."

        reference_list = "\n".join(
            f"- {format_reference_entry(source)}"
            for source in ordered_sources[:50]
        ) or "- No sources collected."

        web_and_papers = "\n".join(
            f"- [{source.title}]({source.url}) | provider={source.provider} | type={source.source_type.value} | published={source.published_date or 'unknown'} | snippet={source.snippet}"
            for source in ordered_sources
            if source.url
        ) or "- No external links collected."

        session.report_sections = [
            ReportSection(section_type="summary", title="Executive Summary", content=f"{summary}\n\nPrimary citations: {format_inline_citations(ordered_sources[:8])}", order=1),
            ReportSection(section_type="methodology", title="Research Scope and Methodology", content=methodology, order=2),
            ReportSection(section_type="strategy", title="Source Strategy", content=source_strategy, order=3),
            ReportSection(section_type="evidence_synthesis", title="Evidence Synthesis by Sub-question", content=evidence_synthesis, order=4),
            ReportSection(section_type="findings", title="Detailed Findings", content=detailed_findings, order=5),
            ReportSection(section_type="disagreements", title="Where Sources Disagree", content=disagreements_md, order=6),
            ReportSection(section_type="contested_claims", title="Contested Claims (Low Consensus)", content=contested_claims_md, order=7),
            ReportSection(section_type="credibility", title="Credibility and Trust Evaluation", content=credibility_methodology, order=8),
            ReportSection(section_type="insights", title="Insights and Interpretive Analysis", content=insights, order=9),
            ReportSection(section_type="limitations", title="Limitations and Open Questions", content=f"{limitations}\n\n{follow_ups}", order=10),
            ReportSection(section_type="links", title="Web and arXiv Links", content=web_and_papers, order=11),
            ReportSection(section_type="rag_refs", title="RAG Document References", content=rag_references, order=12),
            ReportSection(section_type="appendix", title="Comprehensive Bibliography / References", content=reference_list, order=13),
        ]
        return session
