from __future__ import annotations

from pydantic import BaseModel, Field

from able_to_answer.context.models import SecurityLevel


class IngestTextRequest(BaseModel):
    source_name: str | None = Field(default=None, description="Optional label for the document source")
    text: str = Field(..., description="Raw text to ingest")


class IngestResponse(BaseModel):
    document_id: str
    chunk_count: int
    document_sha256: str


class AskRequest(BaseModel):
    document_id: str
    question: str
    max_context_chunks: int | None = None  # future override hook


class AskResponse(BaseModel):
    document_id: str
    question: str
    answer: str
    citations: list[dict]
    audit_id: str
    audit_pack: dict


class GetContextRequest(BaseModel):
    agent_id: str = Field(..., description="Identifier of the requesting agent")
    user_id: str | None = Field(default=None, description="User on behalf of whom context is assembled")


class DocumentMetadataResponse(BaseModel):
    document_id: str
    source: str
    date: int
    security_level: SecurityLevel
    summary: str


class ADRRecordResponse(BaseModel):
    adr_id: str
    title: str
    source: str
    date: int
    security_level: SecurityLevel
    body: str


class GetContextResponse(BaseModel):
    agent_id: str
    retrieved_at: int
    documents: list[DocumentMetadataResponse]
    adrs: list[ADRRecordResponse]
