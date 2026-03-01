"""Tests for the Context Assembler API — /get-context endpoint (Ticket 4)."""
from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient

from able_to_answer.api.main import app, _context_assembler
from able_to_answer.context.models import SecurityLevel
from able_to_answer.context.service import ContextAssembler
from able_to_answer.permissions.models import AccessLevel
from able_to_answer.permissions.repository import PermissionsRepository


@pytest.fixture()
def fresh_assembler() -> ContextAssembler:
    """Provide a fresh ContextAssembler and wire it into the FastAPI app."""
    assembler = ContextAssembler()
    import able_to_answer.api.main as api_module
    original = api_module._context_assembler
    api_module._context_assembler = assembler
    yield assembler
    api_module._context_assembler = original


@pytest.fixture()
def client(fresh_assembler) -> TestClient:
    return TestClient(app)


class TestGetContextEndpoint:
    def test_returns_200(self, client):
        resp = client.post("/get-context", json={"agent_id": "agent-1"})
        assert resp.status_code == 200

    def test_response_has_required_fields(self, client):
        resp = client.post("/get-context", json={"agent_id": "agent-1"})
        data = resp.json()
        assert "agent_id" in data
        assert "retrieved_at" in data
        assert "documents" in data
        assert "adrs" in data

    def test_agent_id_echoed_in_response(self, client):
        resp = client.post("/get-context", json={"agent_id": "my-agent"})
        assert resp.json()["agent_id"] == "my-agent"

    def test_retrieved_at_is_recent_timestamp(self, client):
        before = int(time.time()) - 1
        resp = client.post("/get-context", json={"agent_id": "agent-1"})
        after = int(time.time()) + 1
        ts = resp.json()["retrieved_at"]
        assert before <= ts <= after

    def test_empty_assembler_returns_empty_lists(self, client):
        resp = client.post("/get-context", json={"agent_id": "agent-1"})
        data = resp.json()
        assert data["documents"] == []
        assert data["adrs"] == []

    def test_missing_agent_id_returns_422(self, client):
        resp = client.post("/get-context", json={})
        assert resp.status_code == 422


class TestGetContextWithDocuments:
    def test_public_document_returned_without_user(self, client, fresh_assembler):
        fresh_assembler.add_document(
            source="Architecture Docs",
            summary="System overview.",
            security_level=SecurityLevel.public,
        )
        resp = client.post("/get-context", json={"agent_id": "agent-1"})
        data = resp.json()
        assert len(data["documents"]) == 1
        doc = data["documents"][0]
        assert doc["source"] == "Architecture Docs"
        assert doc["summary"] == "System overview."
        assert "security_level" in doc
        assert "date" in doc
        assert "document_id" in doc

    def test_document_metadata_includes_source_date_security_level(self, client, fresh_assembler):
        fixed_date = 1_700_000_000
        fresh_assembler.add_document(
            source="ADR-001",
            summary="Decision record.",
            security_level=SecurityLevel.public,
            date=fixed_date,
        )
        resp = client.post("/get-context", json={"agent_id": "agent-1"})
        doc = resp.json()["documents"][0]
        assert doc["source"] == "ADR-001"
        assert doc["date"] == fixed_date
        assert doc["security_level"] == SecurityLevel.public.value

    def test_private_document_not_returned_for_other_user(self, client, fresh_assembler):
        """Acceptance criterion: User A cannot see User B's private docs."""
        fresh_assembler.add_document(
            source="Alice's private notes",
            summary="Sensitive content.",
            security_level=SecurityLevel.confidential,
            owner_id="alice",
        )
        # Bob requests context — must not receive Alice's doc
        resp = client.post("/get-context", json={"agent_id": "agent-1", "user_id": "bob"})
        assert resp.json()["documents"] == []

    def test_private_document_returned_for_owner(self, client, fresh_assembler):
        fresh_assembler.add_document(
            source="Alice's notes",
            summary="Private.",
            security_level=SecurityLevel.confidential,
            owner_id="alice",
        )
        resp = client.post("/get-context", json={"agent_id": "agent-1", "user_id": "alice"})
        assert len(resp.json()["documents"]) == 1


class TestGetContextWithADRs:
    def test_public_adr_included_in_bundle(self, client, fresh_assembler):
        fresh_assembler.add_adr(
            title="Use pgvector for vector storage",
            source="ADR-002",
            body="We chose pgvector over Qdrant because…",
            security_level=SecurityLevel.public,
        )
        resp = client.post("/get-context", json={"agent_id": "agent-1"})
        adrs = resp.json()["adrs"]
        assert len(adrs) == 1
        adr = adrs[0]
        assert adr["title"] == "Use pgvector for vector storage"
        assert adr["source"] == "ADR-002"
        assert "body" in adr
        assert "security_level" in adr
        assert "date" in adr
        assert "adr_id" in adr

    def test_private_adr_not_returned_for_other_user(self, client, fresh_assembler):
        fresh_assembler.add_adr(
            title="Internal decision",
            source="ADR-003",
            body="Confidential body.",
            security_level=SecurityLevel.confidential,
            owner_id="alice",
        )
        resp = client.post("/get-context", json={"agent_id": "agent-1", "user_id": "bob"})
        assert resp.json()["adrs"] == []


class TestContextAssemblerService:
    def test_get_context_returns_context_bundle(self):
        assembler = ContextAssembler()
        bundle = assembler.get_context(agent_id="agent-x")
        assert bundle.agent_id == "agent-x"
        assert isinstance(bundle.retrieved_at, int)
        assert isinstance(bundle.documents, list)
        assert isinstance(bundle.adrs, list)

    def test_system_resource_visible_to_all(self):
        assembler = ContextAssembler()
        assembler.add_document(
            source="Shared",
            summary="Public doc",
            security_level=SecurityLevel.public,
        )
        for user in ("alice", "bob", "charlie"):
            bundle = assembler.get_context(agent_id="a", user_id=user)
            assert len(bundle.documents) == 1

    def test_user_resource_only_visible_to_owner(self):
        assembler = ContextAssembler()
        assembler.add_document(
            source="Private",
            summary="Alice only",
            security_level=SecurityLevel.confidential,
            owner_id="alice",
        )
        alice_bundle = assembler.get_context(agent_id="a", user_id="alice")
        bob_bundle = assembler.get_context(agent_id="a", user_id="bob")
        assert len(alice_bundle.documents) == 1
        assert len(bob_bundle.documents) == 0
