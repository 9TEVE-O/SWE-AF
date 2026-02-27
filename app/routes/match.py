"""POST /v1/match — find top-3 embeddings by cosine similarity."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.repositories.embedding import EmbeddingRepository
from app.routes.upload import get_embedding_repo

router = APIRouter()

_EMBEDDING_DIM = 512


class MatchRequest(BaseModel):
    embedding: list[float] = Field(..., min_length=_EMBEDDING_DIM, max_length=_EMBEDDING_DIM)


class MatchResult(BaseModel):
    rank: int
    request_id: str
    embedding_id: str
    confidence: float


class MatchResponse(BaseModel):
    matches: list[MatchResult]


@router.post("/match", response_model=MatchResponse)
def match_embedding(
    req: MatchRequest,
    repo: EmbeddingRepository = Depends(get_embedding_repo),
) -> MatchResponse:
    results = repo.search(req.embedding, top_k=3)
    matches = [
        MatchResult(
            rank=rank + 1,
            request_id=record.request_id,
            embedding_id=record.embedding_id,
            confidence=round(max(0.0, min(1.0, score)), 6),
        )
        for rank, (record, score) in enumerate(results)
    ]
    return MatchResponse(matches=matches)
