"""Context Assembler service: builds ContextBundles for AI agents."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from able_to_answer.context.models import (
    ADRRecord,
    ContextBundle,
    DocumentMetadata,
    SecurityLevel,
)
from able_to_answer.permissions.repository import PermissionsRepository


@dataclass
class _DocumentEntry:
    document_id: str
    source: str
    date: int
    security_level: SecurityLevel
    summary: str


@dataclass
class _ADREntry:
    adr_id: str
    title: str
    source: str
    date: int
    security_level: SecurityLevel
    body: str


class ContextAssembler:
    """Assembles context bundles by combining documents and ADRs.

    Calls ``PermissionsRepository.check_access`` for every resource so that
    agents only receive items they are authorised to read.
    """

    def __init__(self, permissions: PermissionsRepository | None = None) -> None:
        self._permissions = permissions or PermissionsRepository()
        self._documents: list[_DocumentEntry] = []
        self._adrs: list[_ADREntry] = []

    # ------------------------------------------------------------------
    # Population helpers
    # ------------------------------------------------------------------

    def add_document(
        self,
        *,
        source: str,
        summary: str,
        security_level: SecurityLevel = SecurityLevel.internal,
        date: int | None = None,
        document_id: str | None = None,
        owner_id: str | None = None,
    ) -> str:
        """Register a document and return its document_id."""
        from able_to_answer.permissions.models import AccessLevel

        doc_id = document_id or str(uuid.uuid4())
        entry = _DocumentEntry(
            document_id=doc_id,
            source=source,
            date=date or int(time.time()),
            security_level=security_level,
            summary=summary,
        )
        self._documents.append(entry)

        # Grant permission based on security level
        if security_level == SecurityLevel.public:
            self._permissions.grant(
                resource_id=doc_id,
                owner_id=owner_id or "system",
                access_level=AccessLevel.system,
            )
        elif owner_id:
            self._permissions.grant(
                resource_id=doc_id,
                owner_id=owner_id,
                access_level=AccessLevel.user,
            )
        return doc_id

    def add_adr(
        self,
        *,
        title: str,
        source: str,
        body: str,
        security_level: SecurityLevel = SecurityLevel.internal,
        date: int | None = None,
        adr_id: str | None = None,
        owner_id: str | None = None,
    ) -> str:
        """Register an ADR and return its adr_id."""
        from able_to_answer.permissions.models import AccessLevel

        a_id = adr_id or str(uuid.uuid4())
        entry = _ADREntry(
            adr_id=a_id,
            title=title,
            source=source,
            date=date or int(time.time()),
            security_level=security_level,
            body=body,
        )
        self._adrs.append(entry)

        if security_level == SecurityLevel.public:
            self._permissions.grant(
                resource_id=a_id,
                owner_id=owner_id or "system",
                access_level=AccessLevel.system,
            )
        elif owner_id:
            self._permissions.grant(
                resource_id=a_id,
                owner_id=owner_id,
                access_level=AccessLevel.user,
            )
        return a_id

    # ------------------------------------------------------------------
    # Core assembly
    # ------------------------------------------------------------------

    def get_context(self, agent_id: str, user_id: str | None = None) -> ContextBundle:
        """Build a ContextBundle for *agent_id*.

        If *user_id* is provided, only resources accessible to that user
        (as determined by ``check_access``) are included.  When *user_id*
        is ``None``, only ``system``-level (public) resources are returned.
        """
        effective_user = user_id or "__anonymous__"

        docs = [
            DocumentMetadata(
                document_id=d.document_id,
                source=d.source,
                date=d.date,
                security_level=d.security_level,
                summary=d.summary,
            )
            for d in self._documents
            if self._permissions.check_access(effective_user, d.document_id)
        ]

        adrs = [
            ADRRecord(
                adr_id=a.adr_id,
                title=a.title,
                source=a.source,
                date=a.date,
                security_level=a.security_level,
                body=a.body,
            )
            for a in self._adrs
            if self._permissions.check_access(effective_user, a.adr_id)
        ]

        return ContextBundle(
            agent_id=agent_id,
            retrieved_at=int(time.time()),
            documents=docs,
            adrs=adrs,
        )
