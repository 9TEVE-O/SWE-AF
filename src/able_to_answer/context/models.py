"""Data models for Context Bundles returned by the Context Assembler API."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SecurityLevel(str, Enum):
    """Security classification for a context item."""

    public = "public"
    internal = "internal"
    confidential = "confidential"


@dataclass
class DocumentMetadata:
    """Metadata envelope attached to every document in a context bundle."""

    document_id: str
    source: str
    date: int          # Unix timestamp of ingestion / last update
    security_level: SecurityLevel
    summary: str       # Short excerpt used as context


@dataclass
class ADRRecord:
    """An Architecture Decision Record entry inside a context bundle."""

    adr_id: str
    title: str
    source: str
    date: int
    security_level: SecurityLevel
    body: str


@dataclass
class ContextBundle:
    """Assembled context payload returned by the /get-context endpoint."""

    agent_id: str
    retrieved_at: int
    documents: list[DocumentMetadata] = field(default_factory=list)
    adrs: list[ADRRecord] = field(default_factory=list)
