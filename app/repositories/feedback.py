"""In-memory repository for user feedback records."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass


@dataclass
class FeedbackRecord:
    feedback_id: str
    request_id: str
    judgment: str
    ground_truth: str | None
    created_at: int


class FeedbackRepository:
    """Thread-unsafe in-memory store; sufficient for single-process MVP."""

    def __init__(self) -> None:
        self._records: list[FeedbackRecord] = []

    def save(self, record: FeedbackRecord) -> FeedbackRecord:
        self._records.append(record)
        return record

    def create(
        self,
        *,
        request_id: str,
        judgment: str,
        ground_truth: str | None = None,
    ) -> FeedbackRecord:
        record = FeedbackRecord(
            feedback_id=str(uuid.uuid4()),
            request_id=request_id,
            judgment=judgment,
            ground_truth=ground_truth,
            created_at=int(time.time()),
        )
        return self.save(record)

    def count(self) -> int:
        return len(self._records)
