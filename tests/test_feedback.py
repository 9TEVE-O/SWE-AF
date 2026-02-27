"""Tests for POST /v1/feedback endpoint."""
from __future__ import annotations

import struct
import zlib

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.embedding import EmbeddingRepository
from app.repositories.feedback import FeedbackRepository
from app.routes.feedback import get_feedback_repo
from app.routes.upload import get_embedding_repo


def _make_png() -> bytes:
    sig = b"\x89PNG\r\n\x1a\n"

    def chunk(ctype: bytes, data: bytes) -> bytes:
        c = ctype + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", 8, 8, 8, 2, 0, 0, 0))
    idat = chunk(b"IDAT", zlib.compress((b"\x00" + bytes([200, 100, 50]) * 8) * 8))
    iend = chunk(b"IEND", b"")
    return sig + ihdr + idat + iend


@pytest.fixture()
def client():
    fresh_emb_repo = EmbeddingRepository()
    fresh_fb_repo = FeedbackRepository()
    app.dependency_overrides[get_embedding_repo] = lambda: fresh_emb_repo
    app.dependency_overrides[get_feedback_repo] = lambda: fresh_fb_repo
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def uploaded_request_id(client):
    resp = client.post(
        "/v1/upload",
        files={"file": ("img.png", _make_png(), "image/png")},
    )
    assert resp.status_code == 200
    return resp.json()["request_id"]


class TestFeedbackSuccess:
    def test_feedback_correct_returns_200(self, client, uploaded_request_id):
        resp = client.post(
            "/v1/feedback",
            json={"request_id": uploaded_request_id, "judgment": "correct"},
        )
        assert resp.status_code == 200

    def test_feedback_wrong_returns_200(self, client, uploaded_request_id):
        resp = client.post(
            "/v1/feedback",
            json={"request_id": uploaded_request_id, "judgment": "wrong"},
        )
        assert resp.status_code == 200

    def test_feedback_none_returns_200(self, client, uploaded_request_id):
        resp = client.post(
            "/v1/feedback",
            json={"request_id": uploaded_request_id, "judgment": "none"},
        )
        assert resp.status_code == 200

    def test_feedback_returns_feedback_id(self, client, uploaded_request_id):
        resp = client.post(
            "/v1/feedback",
            json={"request_id": uploaded_request_id, "judgment": "correct"},
        )
        data = resp.json()
        assert "feedback_id" in data
        assert len(data["feedback_id"]) > 0

    def test_feedback_returns_created_at(self, client, uploaded_request_id):
        resp = client.post(
            "/v1/feedback",
            json={"request_id": uploaded_request_id, "judgment": "correct"},
        )
        data = resp.json()
        assert "created_at" in data
        assert isinstance(data["created_at"], int)
        assert data["created_at"] > 0

    def test_feedback_with_ground_truth(self, client, uploaded_request_id):
        resp = client.post(
            "/v1/feedback",
            json={
                "request_id": uploaded_request_id,
                "judgment": "wrong",
                "ground_truth": "The correct band is X",
            },
        )
        assert resp.status_code == 200

    def test_multiple_feedbacks_have_unique_ids(self, client, uploaded_request_id):
        ids = set()
        for judgment in ("correct", "wrong", "none"):
            resp = client.post(
                "/v1/feedback",
                json={"request_id": uploaded_request_id, "judgment": judgment},
            )
            assert resp.status_code == 200
            ids.add(resp.json()["feedback_id"])
        assert len(ids) == 3


class TestFeedbackErrors:
    def test_unknown_request_id_returns_404(self, client):
        resp = client.post(
            "/v1/feedback",
            json={"request_id": "nonexistent-id", "judgment": "correct"},
        )
        assert resp.status_code == 404

    def test_invalid_judgment_returns_422(self, client, uploaded_request_id):
        resp = client.post(
            "/v1/feedback",
            json={"request_id": uploaded_request_id, "judgment": "maybe"},
        )
        assert resp.status_code == 422

    def test_missing_judgment_returns_422(self, client, uploaded_request_id):
        resp = client.post(
            "/v1/feedback",
            json={"request_id": uploaded_request_id},
        )
        assert resp.status_code == 422

    def test_missing_request_id_returns_422(self, client):
        resp = client.post(
            "/v1/feedback",
            json={"judgment": "correct"},
        )
        assert resp.status_code == 422
