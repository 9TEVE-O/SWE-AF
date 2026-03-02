# SWE-AF Repository

This is a Python-based repository providing an autonomous engineering team runtime built on [AgentField](https://github.com/Agent-Field/agentfield). It is primarily responsible for orchestrating multi-agent software engineering pipelines — planning, coding, review, testing, and merging — across one or more repositories. Please follow these guidelines when contributing:

## Code Standards

### Required Before Each Commit
- Run `ruff check .` and `ruff format .` before committing any changes to ensure proper code formatting and style

### Development Flow
- Install: `python -m pip install -e ".[dev]"`
- Test: `make test` (runs `pytest tests/ -x -q`)
- Full CI check: `make check` (includes tests + compile checks for both packages)

## Repository Structure
- `swe_af/` — Core agent runtime: execution engine, agent AI providers, prompts, and reasoners
  - `swe_af/execution/` — Build orchestration, DAG executor, workspace management, and schemas
  - `swe_af/agent_ai/` — Agent AI provider integrations (Claude, OpenCode, etc.)
  - `swe_af/prompts/` — Prompt templates for each agent role
  - `swe_af/reasoners/` — Planning and reasoning logic
  - `swe_af/fast/` — Fast execution path
- `src/able_to_answer/` — FastAPI service layer for the HTTP API
  - `src/able_to_answer/api/` — API endpoints and routing
  - `src/able_to_answer/core/` — Core business logic
  - `src/able_to_answer/ingestion/` — Data ingestion
  - `src/able_to_answer/retrieval/` — Retrieval logic
  - `src/able_to_answer/permissions/` — Permission handling
  - `src/able_to_answer/audit/` — Audit logging
  - `src/able_to_answer/context/` — Context assembly
- `tests/` — Test suite (pytest)
- `docs/` — Architecture, contributing guidelines, and skill documentation
- `examples/` — Example builds and benchmark artifacts
- `assets/` — Images and static assets

## Key Guidelines
1. Follow Python best practices and idiomatic patterns for Python 3.12+
2. Maintain existing code structure and organization
3. Use Pydantic v2 models for all data schemas (see `swe_af/execution/schemas.py`)
4. Write unit tests for new functionality using pytest; use parametrize for table-driven tests where possible
5. Use `pytest-asyncio` (configured with `asyncio_mode = "auto"`) for async tests
6. Document public APIs and complex logic; suggest changes to `docs/` when appropriate
7. When modifying agent prompts, update the corresponding files in `swe_af/prompts/`
8. All configuration options are defined in `swe_af/execution/schemas.py` — update that file when adding new config keys
