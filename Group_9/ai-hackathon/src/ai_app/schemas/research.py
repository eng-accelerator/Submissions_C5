from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator

from ai_app.domain.enums import ConfidenceLabel, DatePreset, Depth, InsightType, ResearchStatus, RunMode, SourceChannel, SourceType


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Source(BaseModel):
    id: str = Field(default_factory=lambda: f"src_{uuid4().hex}")
    url: str | None = None
    title: str
    source_type: SourceType
    provider: str
    author: str | None = None
    published_date: str | None = None
    credibility_score: float = 0.0
    relevance_score: float = 0.0
    rank: int = 0
    duplicate_of_source_id: str | None = None
    snippet: str
    filename: str | None = None
    collection_id: str | None = None
    page_refs: list[int] = Field(default_factory=list)
    credibility_explanation: str = ""
    retrieval_reason: str = ""
    matched_time_window: bool | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Finding(BaseModel):
    id: str = Field(default_factory=lambda: f"fnd_{uuid4().hex}")
    sub_question: str
    content: str
    snippet: str = ""
    quote_excerpt: str = ""
    filename: str | None = None
    page_refs: list[int] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    agent: str
    raw: dict[str, Any] = Field(default_factory=dict)


class Claim(BaseModel):
    id: str = Field(default_factory=lambda: f"clm_{uuid4().hex}")
    statement: str
    supporting_source_ids: list[str] = Field(default_factory=list)
    contradicting_source_ids: list[str] = Field(default_factory=list)
    confidence: ConfidenceLabel = ConfidenceLabel.LOW
    confidence_pct: int = 0
    reasoning: str
    credibility_summary: str = ""
    evidence_summary: str = ""
    contested: bool = False
    weak_evidence: bool = False
    trust_score: int = 0
    # 100 = broad agreement among cited sources; lower when paired with conflicting claims/sources.
    consensus_pct: int = 100


class Contradiction(BaseModel):
    id: str = Field(default_factory=lambda: f"ctr_{uuid4().hex}")
    claim_a_id: str = ""
    claim_b_id: str = ""
    claim_a: str
    source_a_id: str
    claim_b: str
    source_b_id: str
    source_a_label: str = ""
    source_b_label: str = ""
    position_a: str = ""
    position_b: str = ""
    analysis: str
    resolution: str | None = None
    # Which side the system weights more: "a", "b", or "tie".
    more_credible_side: str = "tie"
    credibility_reasoning: str = ""
    # 0 = strong disagreement; 1 = mild tension (heuristic).
    consensus_score: float | None = None


class Insight(BaseModel):
    id: str = Field(default_factory=lambda: f"ins_{uuid4().hex}")
    content: str
    evidence_chain: list[str] = Field(default_factory=list)
    insight_type: InsightType = InsightType.TREND
    label: str


class Entity(BaseModel):
    id: str = Field(default_factory=lambda: f"ent_{uuid4().hex}")
    name: str
    entity_type: str
    description: str | None = None
    source_ids: list[str] = Field(default_factory=list)


class Relationship(BaseModel):
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    description: str | None = None


class ReportSection(BaseModel):
    section_type: str
    title: str
    content: str
    order: int


class FollowUpQuestion(BaseModel):
    question: str
    rationale: str


class ResearchEvent(BaseModel):
    event_type: str
    timestamp: datetime = Field(default_factory=utc_now)
    agent: str | None = None
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class AgentTraceEntry(BaseModel):
    id: str = Field(default_factory=lambda: f"trc_{uuid4().hex}")
    agent: str
    step: str
    input_summary: str | None = None
    output_summary: str | None = None
    timestamp: datetime = Field(default_factory=utc_now)
    token_estimate: int | None = None


class KnowledgeDocument(BaseModel):
    id: str = Field(default_factory=lambda: f"doc_{uuid4().hex}")
    collection_id: str
    filename: str
    document_type: str
    checksum: str
    upload_timestamp: datetime = Field(default_factory=utc_now)
    status: str = "uploaded"
    page_count: int | None = None
    tags: list[str] = Field(default_factory=list)
    summary: str = ""


class DocumentChunk(BaseModel):
    id: str = Field(default_factory=lambda: f"chk_{uuid4().hex}")
    document_id: str
    chunk_index: int
    text: str
    token_count: int
    page_span: list[int] = Field(default_factory=list)
    embedding_id: str | None = None
    keywords: list[str] = Field(default_factory=list)
    embedding: list[float] = Field(default_factory=list)


class LocalCollection(BaseModel):
    id: str = Field(default_factory=lambda: f"col_{uuid4().hex}")
    name: str
    description: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    document_ids: list[str] = Field(default_factory=list)
    shared_scope: str = "workspace"


class ResearchSession(BaseModel):
    session_id: str = Field(default_factory=lambda: f"ses_{uuid4().hex}")
    query: str
    run_mode: RunMode = RunMode.SINGLE
    batch_topics: list[str] = Field(default_factory=list)
    enabled_sources: list[SourceChannel] = Field(default_factory=lambda: [SourceChannel.LOCAL_RAG, SourceChannel.WEB, SourceChannel.ARXIV])
    start_date: date | None = None
    end_date: date | None = None
    date_preset: DatePreset = DatePreset.ALL_TIME
    depth: Depth = Depth.STANDARD
    status: ResearchStatus = ResearchStatus.PENDING
    sub_questions: list[str] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    contradictions: list[Contradiction] = Field(default_factory=list)
    insights: list[Insight] = Field(default_factory=list)
    entities: list[Entity] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    follow_up_questions: list[FollowUpQuestion] = Field(default_factory=list)
    report_sections: list[ReportSection] = Field(default_factory=list)
    events: list[ResearchEvent] = Field(default_factory=list)
    agent_trace: list[AgentTraceEntry] = Field(default_factory=list)
    uploaded_documents: list[KnowledgeDocument] = Field(default_factory=list)
    selected_collection_ids: list[str] = Field(default_factory=list)
    retrieved_chunks: list[DocumentChunk] = Field(default_factory=list)
    pdf_texts: list[str] = Field(default_factory=list)
    debate_mode: bool = False
    position_a: str | None = None
    position_b: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ResearchRequest(BaseModel):
    query: str = ""
    depth: Depth = Depth.STANDARD
    collection_ids: list[str] = Field(default_factory=list)
    use_local_corpus: bool = True
    enabled_sources: list[SourceChannel] = Field(default_factory=lambda: [SourceChannel.LOCAL_RAG, SourceChannel.WEB, SourceChannel.ARXIV])
    start_date: date | None = None
    end_date: date | None = None
    date_preset: DatePreset = DatePreset.ALL_TIME
    batch_topics: list[str] = Field(default_factory=list)
    run_mode: RunMode = RunMode.SINGLE

    @model_validator(mode="after")
    def validate_request(self) -> "ResearchRequest":
        if not self.enabled_sources:
            raise ValueError("At least one source must be enabled.")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date must be on or before end_date.")
        cleaned_topics = [topic.strip() for topic in self.batch_topics if topic and topic.strip()]
        self.batch_topics = cleaned_topics
        if self.run_mode == RunMode.BATCH and not cleaned_topics:
            raise ValueError("batch_topics are required when run_mode=batch.")
        if self.run_mode == RunMode.SINGLE and not self.query.strip():
            raise ValueError("query is required when run_mode=single.")
        if self.run_mode == RunMode.BATCH and not self.query.strip():
            self.query = cleaned_topics[0]
        return self


class KnowledgeUploadResponse(BaseModel):
    collection_id: str
    document_ids: list[str]
    status: str


class GraphResponse(BaseModel):
    nodes: list[Entity]
    edges: list[Relationship]


class TraceResponse(BaseModel):
    trace: list[AgentTraceEntry]
