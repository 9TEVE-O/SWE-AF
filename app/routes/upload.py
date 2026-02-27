"""POST /v1/upload — accept an image file and store its embedding."""
from __future__ import annotations

import hashlib
import struct
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.repositories.embedding import EmbeddingRecord, EmbeddingRepository

router = APIRouter()

# Module-level singleton; tests may replace via app.dependency_overrides.
_embedding_repo: EmbeddingRepository = EmbeddingRepository()


def get_embedding_repo() -> EmbeddingRepository:
    return _embedding_repo

# Limits
_MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB
_EMBEDDING_DIM = 512

# Accepted image magic bytes
_MAGIC = {
    b"\x89PNG\r\n\x1a\n": "png",
    b"\xff\xd8\xff": "jpeg",
    b"GIF87a": "gif",
    b"GIF89a": "gif",
    b"RIFF": "webp",  # RIFF....WEBP
}


class UploadResponse(BaseModel):
    request_id: str
    embedding_id: str
    embedding_dim: int
    content_type: str


def _detect_format(data: bytes) -> str | None:
    for magic, fmt in _MAGIC.items():
        if data[: len(magic)] == magic:
            if fmt == "webp":
                # RIFF????WEBP
                if len(data) >= 12 and data[8:12] == b"WEBP":
                    return "webp"
                return None
            return fmt
    return None


def _compute_embedding(data: bytes) -> list[float]:
    """Produce a deterministic 512-dim unit-normalised embedding from raw bytes.

    The approach: generate 512 floats by hashing successive 64-byte windows
    of the data (using SHA-256), then L2-normalise the vector.
    """
    floats: list[float] = []
    seed = data
    while len(floats) < _EMBEDDING_DIM:
        digest = hashlib.sha256(seed).digest()
        # Interpret each 4-byte group as a signed int32, normalise to [-1, 1]
        for i in range(0, len(digest), 4):
            val = struct.unpack_from(">i", digest, i)[0]
            floats.append(val / 2_147_483_648.0)
        seed = digest  # chain hashes

    floats = floats[:_EMBEDDING_DIM]

    # L2 normalise
    norm = sum(x * x for x in floats) ** 0.5
    if norm > 0:
        floats = [x / norm for x in floats]

    return floats


@router.post("/upload", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    repo: EmbeddingRepository = Depends(get_embedding_repo),
) -> UploadResponse:
    data = await file.read()

    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    if len(data) > _MAX_FILE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: max {_MAX_FILE_BYTES // (1024 * 1024)} MB",
        )

    fmt = _detect_format(data)
    if fmt is None:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Upload a PNG, JPEG, GIF, or WebP image.",
        )

    request_id = str(uuid.uuid4())
    embedding_id = str(uuid.uuid4())
    embedding = _compute_embedding(data)

    record = EmbeddingRecord(
        embedding_id=embedding_id,
        request_id=request_id,
        embedding=embedding,
    )
    repo.save(record)

    return UploadResponse(
        request_id=request_id,
        embedding_id=embedding_id,
        embedding_dim=len(embedding),
        content_type=fmt,
    )
