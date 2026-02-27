"""POST /v1/feedback — store user judgment for a previous upload request."""
from __future__ import annotations

from enum import Enum

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.repositories.embedding import EmbeddingRepository
from app.repositories.feedback import FeedbackRepository
from app.routes.upload import get_embedding_repo

router = APIRouter()

# Module-level singleton; tests may replace via app.dependency_overrides.
_feedback_repo: FeedbackRepository = FeedbackRepository()


def get_feedback_repo() -> FeedbackRepository:
    return _feedback_repo


class Judgment(str, Enum):
    correct = "correct"
    wrong = "wrong"
    none = "none"


class FeedbackRequest(BaseModel):
    request_id: str
    judgment: Judgment
    ground_truth: str | None = None


class FeedbackResponse(BaseModel):
    feedback_id: str
    created_at: int


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(
    req: FeedbackRequest,
    embedding_repo: EmbeddingRepository = Depends(get_embedding_repo),
    fb_repo: FeedbackRepository = Depends(get_feedback_repo),
) -> FeedbackResponse:
    # Verify the request_id exists in the embedding store
    if embedding_repo.find_by_request_id(req.request_id) is None:
        raise HTTPException(status_code=404, detail="request_id not found")

    record = fb_repo.create(
        request_id=req.request_id,
        judgment=req.judgment.value,
        ground_truth=req.ground_truth,
    )
    return FeedbackResponse(feedback_id=record.feedback_id, created_at=record.created_at)
