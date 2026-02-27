"""Tests for POST /v1/match endpoint."""
from __future__ import annotations

import struct
import zlib

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.embedding import EmbeddingRepository
from app.routes.upload import get_embedding_repo

_EMBEDDING_DIM = 512


def _make_png(color: tuple = (100, 150, 200)) -> bytes:
    sig = b"\x89PNG\r\n\x1a\n"

    def chunk(ctype: bytes, data: bytes) -> bytes:
        c = ctype + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", 10, 10, 8, 2, 0, 0, 0))
    idat = chunk(b"IDAT", zlib.compress((b"\x00" + bytes(color) * 10) * 10))
    iend = chunk(b"IEND", b"")
    return sig + ihdr + idat + iend


def _unit_vec(dim: int = _EMBEDDING_DIM) -> list[float]:
    """Return a unit vector with 1.0 at index 0."""
    v = [0.0] * dim
    v[0] = 1.0
    return v


@pytest.fixture()
def client():
    fresh_repo = EmbeddingRepository()
    app.dependency_overrides[get_embedding_repo] = lambda: fresh_repo
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def client_with_uploads(client):
    """Client that has 3 images pre-uploaded."""
    request_ids = []
    for i in range(3):
        resp = client.post(
            "/v1/upload",
            files={"file": (f"img{i}.png", _make_png(color=(i * 60, i * 70, i * 80)), "image/png")},
        )
        assert resp.status_code == 200
        request_ids.append(resp.json()["request_id"])
    return client, request_ids


class TestMatchSuccess:
    def test_match_empty_store_returns_empty_list(self, client):
        resp = client.post("/v1/match", json={"embedding": _unit_vec()})
        assert resp.status_code == 200
        assert resp.json()["matches"] == []

    def test_match_returns_up_to_three_results(self, client_with_uploads):
        client, _ = client_with_uploads
        resp = client.post("/v1/match", json={"embedding": _unit_vec()})
        assert resp.status_code == 200
        assert len(resp.json()["matches"]) <= 3

    def test_match_results_have_required_fields(self, client_with_uploads):
        client, _ = client_with_uploads
        resp = client.post("/v1/match", json={"embedding": _unit_vec()})
        for m in resp.json()["matches"]:
            assert "rank" in m
            assert "request_id" in m
            assert "embedding_id" in m
            assert "confidence" in m

    def test_match_confidence_between_zero_and_one(self, client_with_uploads):
        client, _ = client_with_uploads
        resp = client.post("/v1/match", json={"embedding": _unit_vec()})
        for m in resp.json()["matches"]:
            assert 0.0 <= m["confidence"] <= 1.0

    def test_match_ranks_are_ascending(self, client_with_uploads):
        client, _ = client_with_uploads
        resp = client.post("/v1/match", json={"embedding": _unit_vec()})
        ranks = [m["rank"] for m in resp.json()["matches"]]
        assert ranks == sorted(ranks)

    def test_match_confidence_descending(self, client_with_uploads):
        client, _ = client_with_uploads
        resp = client.post("/v1/match", json={"embedding": _unit_vec()})
        scores = [m["confidence"] for m in resp.json()["matches"]]
        assert scores == sorted(scores, reverse=True)

    def test_exact_match_gives_confidence_one(self, client):
        """Uploading an image then querying with its own embedding yields confidence ~1."""
        # Upload
        png = _make_png(color=(123, 45, 67))
        up = client.post("/v1/upload", files={"file": ("x.png", png, "image/png")})
        assert up.status_code == 200

        # Retrieve the stored embedding via the repository
        from app.routes.upload import _compute_embedding
        emb = _compute_embedding(png)

        resp = client.post("/v1/match", json={"embedding": emb})
        assert resp.status_code == 200
        top = resp.json()["matches"][0]
        assert top["confidence"] > 0.99


class TestMatchErrors:
    def test_wrong_dimension_returns_422(self, client):
        resp = client.post("/v1/match", json={"embedding": [0.1] * 10})
        assert resp.status_code == 422

    def test_missing_embedding_returns_422(self, client):
        resp = client.post("/v1/match", json={})
        assert resp.status_code == 422
