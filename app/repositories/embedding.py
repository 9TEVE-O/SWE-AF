"""In-memory repository for image embeddings with cosine similarity search."""
from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class EmbeddingRecord:
    embedding_id: str
    request_id: str
    embedding: list[float]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class EmbeddingRepository:
    """Thread-unsafe in-memory store; sufficient for single-process MVP."""

    def __init__(self) -> None:
        self._records: list[EmbeddingRecord] = []

    def save(self, record: EmbeddingRecord) -> None:
        self._records.append(record)

    def find_by_request_id(self, request_id: str) -> EmbeddingRecord | None:
        for r in self._records:
            if r.request_id == request_id:
                return r
        return None

    def search(self, query: list[float], top_k: int = 3) -> list[tuple[EmbeddingRecord, float]]:
        """Return up to *top_k* records ranked by cosine similarity descending."""
        scored = [
            (r, _cosine_similarity(query, r.embedding))
            for r in self._records
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def count(self) -> int:
        return len(self._records)
