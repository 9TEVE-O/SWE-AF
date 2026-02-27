"""BandLens FastAPI application factory."""
from __future__ import annotations

from fastapi import FastAPI

from app.routes import feedback, match, upload

app = FastAPI(
    title="BandLens",
    description="Image embedding upload, similarity search, and feedback API",
    version="0.1.0",
)

v1 = app
v1.include_router(upload.router, prefix="/v1")
v1.include_router(match.router, prefix="/v1")
v1.include_router(feedback.router, prefix="/v1")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
