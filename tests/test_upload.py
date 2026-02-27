"""Tests for POST /v1/upload endpoint."""
from __future__ import annotations

import struct
import zlib

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.embedding import EmbeddingRepository
from app.routes.upload import get_embedding_repo


def _make_png(width: int = 10, height: int = 10, color: tuple = (100, 150, 200)) -> bytes:
    """Generate a minimal valid PNG image without Pillow."""
    sig = b"\x89PNG\r\n\x1a\n"

    def chunk(ctype: bytes, data: bytes) -> bytes:
        c = ctype + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    scanline = b"\x00" + bytes(color) * width
    idat = chunk(b"IDAT", zlib.compress(scanline * height))
    iend = chunk(b"IEND", b"")
    return sig + ihdr + idat + iend


def _make_jpeg_stub() -> bytes:
    """Return the JPEG SOI + APP0 magic bytes (enough to pass format detection)."""
    return b"\xff\xd8\xff\xe0" + b"\x00" * 20


@pytest.fixture()
def client():
    """TestClient with a fresh EmbeddingRepository per test."""
    fresh_repo = EmbeddingRepository()
    app.dependency_overrides[get_embedding_repo] = lambda: fresh_repo
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestUploadSuccess:
    def test_upload_png_returns_200(self, client):
        resp = client.post(
            "/v1/upload",
            files={"file": ("test.png", _make_png(), "image/png")},
        )
        assert resp.status_code == 200

    def test_upload_returns_request_id(self, client):
        resp = client.post(
            "/v1/upload",
            files={"file": ("test.png", _make_png(), "image/png")},
        )
        data = resp.json()
        assert "request_id" in data
        assert len(data["request_id"]) > 0

    def test_upload_returns_embedding_id(self, client):
        resp = client.post(
            "/v1/upload",
            files={"file": ("img.png", _make_png(), "image/png")},
        )
        data = resp.json()
        assert "embedding_id" in data

    def test_upload_returns_512_dim_embedding(self, client):
        resp = client.post(
            "/v1/upload",
            files={"file": ("img.png", _make_png(), "image/png")},
        )
        data = resp.json()
        assert data["embedding_dim"] == 512

    def test_upload_reports_png_content_type(self, client):
        resp = client.post(
            "/v1/upload",
            files={"file": ("img.png", _make_png(), "image/png")},
        )
        assert resp.json()["content_type"] == "png"

    def test_upload_jpeg_accepted(self, client):
        resp = client.post(
            "/v1/upload",
            files={"file": ("img.jpg", _make_jpeg_stub(), "image/jpeg")},
        )
        assert resp.status_code == 200
        assert resp.json()["content_type"] == "jpeg"

    def test_multiple_uploads_have_unique_request_ids(self, client):
        ids = set()
        for i in range(3):
            resp = client.post(
                "/v1/upload",
                files={"file": (f"img{i}.png", _make_png(color=(i * 40, i * 50, i * 60)), "image/png")},
            )
            assert resp.status_code == 200
            ids.add(resp.json()["request_id"])
        assert len(ids) == 3


class TestUploadErrors:
    def test_empty_file_returns_400(self, client):
        resp = client.post(
            "/v1/upload",
            files={"file": ("empty.png", b"", "image/png")},
        )
        assert resp.status_code == 400

    def test_text_file_returns_400(self, client):
        resp = client.post(
            "/v1/upload",
            files={"file": ("doc.txt", b"Hello world", "text/plain")},
        )
        assert resp.status_code == 400

    def test_invalid_binary_returns_400(self, client):
        resp = client.post(
            "/v1/upload",
            files={"file": ("bad.png", b"\x00\x01\x02\x03" * 10, "image/png")},
        )
        assert resp.status_code == 400
