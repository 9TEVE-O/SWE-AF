from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, File, Query, UploadFile
from fastapi.responses import JSONResponse

from able_to_answer.context.service import ContextAssembler
from able_to_answer.core.config import settings
from able_to_answer.core.logging import logger
from able_to_answer.core.neon_client import NeonAPIError, NeonClient
from able_to_answer.core.storage import SqliteStore
from able_to_answer.ingestion.service import ingest_text
from able_to_answer.retrieval.service import retrieve_top_chunks
from able_to_answer.audit.service import build_audit_pack
from able_to_answer.api.models import (
    AskRequest,
    AskResponse,
    GetContextRequest,
    GetContextResponse,
    IngestResponse,
    IngestTextRequest,
    NeonCreateProjectRequest,
)

app = FastAPI(
    title="Able to Answer",
    description="Governance-grade AI document intelligence: ingest → retrieve → answer → audit",
    version="0.1.0",
)

store = SqliteStore(settings.db_path)

# Singleton Context Assembler; tests may swap this out directly.
_context_assembler = ContextAssembler()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest/text", response_model=IngestResponse)
def ingest_text_route(req: IngestTextRequest):
    res = ingest_text(store, source_name=req.source_name, text=req.text)
    return IngestResponse(
        document_id=res.document_id,
        chunk_count=res.chunk_count,
        document_sha256=res.document_sha256,
    )


@app.post("/ingest/file", response_model=IngestResponse)
async def ingest_file_route(file: UploadFile = File(...)):
    # MVP: treat uploaded file as text if it decodes cleanly.
    # PDF parsing is intentionally not implemented here (keeps MVP dependency-free).
    raw = await file.read()
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Unsupported file format in MVP",
                "detail": "Upload UTF-8 text. PDF extraction will be added next.",
            },
        )

    res = ingest_text(store, source_name=file.filename, text=text)
    return IngestResponse(
        document_id=res.document_id,
        chunk_count=res.chunk_count,
        document_sha256=res.document_sha256,
    )


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    doc = store.get_document(document_id=req.document_id)
    if not doc:
        return JSONResponse(status_code=404, content={"error": "document_not_found"})

    citations = retrieve_top_chunks(
        store, document_id=req.document_id, question=req.question
    )

    # MVP "answer builder": return the highest-scoring chunk(s) as an extractive answer.
    # This proves the end-to-end contract + citations + audit trail without model integration.
    if not citations:
        answer = (
            "No relevant evidence was found in the indexed chunks for this question. "
            "Try rephrasing the question or ingesting a more complete document."
        )
        cited_dicts = []
    else:
        chunk_rows = {r["id"]: r for r in store.get_chunks(document_id=req.document_id)}
        evidence = []
        for c in citations:
            row = chunk_rows.get(c.chunk_id)
            txt = row["text"] if row else None
            if txt:
                evidence.append(txt.strip())

        combined = "\n\n---\n\n".join(evidence)
        answer = combined[: settings.max_answer_chars]
        cited_dicts = [asdict(c) for c in citations]

    pack = build_audit_pack(
        document_id=req.document_id,
        question=req.question,
        answer=answer,
        citations=citations,
        retrieval_mode="lexical_overlap_v1",
    )
    audit_id = store.insert_audit(
        document_id=req.document_id,
        question=req.question,
        answer=answer,
        citations=citations,
        pack=pack,
    )

    logger.info(
        "ask: doc=%s audit=%s citations=%d", req.document_id, audit_id, len(citations)
    )

    return AskResponse(
        document_id=req.document_id,
        question=req.question,
        answer=answer,
        citations=cited_dicts,
        audit_id=audit_id,
        audit_pack=pack,
    )


@app.post("/get-context", response_model=GetContextResponse)
def get_context(req: GetContextRequest) -> GetContextResponse:
    """Assemble a Context Bundle for an agent.

    Returns documents and ADRs the requesting user is authorised to see,
    each decorated with Source, Date, and Security Level metadata.
    """
    bundle = _context_assembler.get_context(
        agent_id=req.agent_id,
        user_id=req.user_id,
    )
    return GetContextResponse(
        agent_id=bundle.agent_id,
        retrieved_at=bundle.retrieved_at,
        documents=[
            {
                "document_id": d.document_id,
                "source": d.source,
                "date": d.date,
                "security_level": d.security_level,
                "summary": d.summary,
            }
            for d in bundle.documents
        ],
        adrs=[
            {
                "adr_id": a.adr_id,
                "title": a.title,
                "source": a.source,
                "date": a.date,
                "security_level": a.security_level,
                "body": a.body,
            }
            for a in bundle.adrs
        ],
    )


# ---------------------------------------------------------------------------
# Neon Management API v2 proxy routes
# ---------------------------------------------------------------------------


def _neon_client() -> NeonClient:
    """Return a NeonClient configured from application settings."""
    return NeonClient(
        api_key=settings.neon_api_key,
        base_url=settings.neon_api_base_url,
    )


def _neon_error(exc: NeonAPIError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message},
    )


@app.get("/neon/projects")
def neon_list_projects(
    limit: int | None = Query(
        default=None, description="Maximum number of projects to return"
    ),
    cursor: str | None = Query(default=None, description="Pagination cursor"),
):
    """List all Neon projects for the configured API key.

    Requires ``NEON_API_KEY`` to be set in the environment.
    """
    try:
        return _neon_client().list_projects(limit=limit, cursor=cursor)
    except NeonAPIError as exc:
        return _neon_error(exc)


@app.post("/neon/projects", status_code=201)
def neon_create_project(req: NeonCreateProjectRequest):
    """Create a new Neon project.

    Requires ``NEON_API_KEY`` to be set in the environment.
    """
    try:
        return _neon_client().create_project(
            name=req.name,
            region_id=req.region_id,
            pg_version=req.pg_version,
        )
    except NeonAPIError as exc:
        return _neon_error(exc)


@app.get("/neon/projects/{project_id}")
def neon_get_project(project_id: str):
    """Get details for a single Neon project.

    Requires ``NEON_API_KEY`` to be set in the environment.
    """
    try:
        return _neon_client().get_project(project_id)
    except NeonAPIError as exc:
        return _neon_error(exc)


@app.delete("/neon/projects/{project_id}")
def neon_delete_project(project_id: str):
    """Delete a Neon project.

    Requires ``NEON_API_KEY`` to be set in the environment.
    """
    try:
        return _neon_client().delete_project(project_id)
    except NeonAPIError as exc:
        return _neon_error(exc)


@app.get("/neon/projects/{project_id}/branches")
def neon_list_branches(project_id: str):
    """List all branches for a Neon project.

    Requires ``NEON_API_KEY`` to be set in the environment.
    """
    try:
        return _neon_client().list_branches(project_id)
    except NeonAPIError as exc:
        return _neon_error(exc)


@app.get("/neon/projects/{project_id}/branches/{branch_id}/databases")
def neon_list_databases(project_id: str, branch_id: str):
    """List all databases for a Neon project branch.

    Requires ``NEON_API_KEY`` to be set in the environment.
    """
    try:
        return _neon_client().list_databases(project_id, branch_id)
    except NeonAPIError as exc:
        return _neon_error(exc)


@app.get("/neon/projects/{project_id}/connection_uri")
def neon_get_connection_uri(
    project_id: str,
    branch_id: str | None = Query(default=None),
    endpoint_id: str | None = Query(default=None),
    database_name: str | None = Query(default=None),
    role_name: str | None = Query(default=None),
    pooled: bool = Query(default=False),
):
    """Get a PostgreSQL connection URI for a Neon project.

    Requires ``NEON_API_KEY`` to be set in the environment.
    """
    try:
        return _neon_client().get_connection_uri(
            project_id,
            branch_id=branch_id,
            endpoint_id=endpoint_id,
            database_name=database_name,
            role_name=role_name,
            pooled=pooled,
        )
    except NeonAPIError as exc:
        return _neon_error(exc)
