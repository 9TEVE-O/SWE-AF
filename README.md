<div align="center">

# SWE-AF

### Autonomous Engineering Team Runtime Built on [AgentField](https://github.com/Agent-Field/agentfield)

**Pronounced:** _"swee-AF"_ (one word)

[![Public Beta](https://img.shields.io/badge/status-public%20beta-0ea5e9?style=for-the-badge)](#)
[![Python](https://img.shields.io/badge/python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-16a34a?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-make%20check-blue?style=for-the-badge)](.github/workflows/ci.yml)
[![Built with AgentField](https://img.shields.io/badge/Built%20with-AgentField-0A66C2?style=for-the-badge)](https://github.com/Agent-Field/agentfield)
![WorldSpace Community Developer](https://img.shields.io/badge/WorldSpace-Community%20Developer-111827?style=for-the-badge)
[![Example PR](https://img.shields.io/badge/Example-PR%20%23179-ff6b35?style=for-the-badge&logo=github)](https://github.com/Agent-Field/agentfield/pull/179)

**One API call → full engineering team → shipped code.**

<p>
  <a href="#quick-start">Quick Start</a> •
  <a href="#features">Features</a> •
  <a href="#how-a-build-works">How It Works</a> •
  <a href="#benchmark">Benchmark</a> •
  <a href="#operating-modes">Modes</a> •
  <a href="#api-reference">API</a> •
  <a href="docs/ARCHITECTURE.md">Architecture</a>
</p>

</div>

SWE-AF spins up a coordinated fleet of AI agents — product managers, architects, coders, reviewers, testers — that scope, build, adapt, and ship software end to end. No scaffolding, no human-in-the-loop. One goal in, verified PR out.

<p align="center">
  <img src="assets/banner.jpg" alt="SWE-AF autonomous engineering fleet banner" width="100%" />
</p>

<div align="center">

| Scored **95/100** on benchmark | 10/10 issues, **$19** total cost | **400–500+** agents per build | Claude, MiniMax, DeepSeek, Qwen |
|:---:|:---:|:---:|:---:|
| Beats Claude Code (73) & Codex (62) | [Real PR — zero human code](https://github.com/Agent-Field/agentfield/pull/179) | Planning → coding → QA → merge | Any model, any provider |

</div>

## Features

- **Factory, not a wrapper** — Planning, execution, and governance agents run as a coordinated control stack. Not just a coder loop with retries.
- **Hardness-aware execution** — Easy issues pass through fast. Hard issues trigger deeper adaptation and DAG-level replanning instead of blind retries.
- **Multi-model, multi-provider** — Assign different models per role (`coder: opus`, `qa: haiku`). Works with Claude, OpenRouter, OpenAI, and Google.
- **Single-repo and multi-repo modes** — Point at one repository or orchestrate coordinated changes across multiple repos in a single build.
- **Continual learning** — With `enable_learning: true`, conventions and failure patterns discovered early get injected into downstream issues.
- **Agent-scale parallelism** — Dependency-level scheduling + isolated git worktrees allow large fan-out without branch collisions.
- **Self-correcting builds** — Three nested control loops (inner retry → advisor adaptation → DAG replanning) handle failures automatically.
- **Crash recovery** — Checkpointed execution supports `resume_build` after interruptions.
- **Draft PR output** — Pass a `repo_url` and SWE-AF clones, builds, and opens a draft PR on GitHub.

## Quick Start

### Deploy with Railway (fastest)

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/swe-af)

One click deploys SWE-AF + AgentField control plane + PostgreSQL. Set two environment variables in Railway:

- `CLAUDE_CODE_OAUTH_TOKEN` — run `claude setup-token` in [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) (uses Pro/Max subscription credits)
- `GH_TOKEN` — GitHub personal access token with `repo` scope for draft PR creation

Then trigger a build:

```bash
curl -X POST https://<your-app>.up.railway.app/api/v1/execute/async/swe-planner.build \
  -H "Content-Type: application/json" \
  -H "X-API-Key: this-is-a-secret" \
  -d '{"input": {"goal": "Add JWT auth", "repo_url": "https://github.com/user/my-repo"}}'
```

### Run Locally

```bash
# 1. Install
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 2. Start the control plane and register the node
af                 # starts AgentField on :8080
python -m swe_af   # registers node "swe-planner"

# 3. Trigger a build
curl -X POST http://localhost:8080/api/v1/execute/async/swe-planner.build \
  -H "Content-Type: application/json" \
  -d '{"input": {"goal": "Add JWT auth", "repo_url": "https://github.com/user/my-project"}}'
```

### Docker

```bash
cp .env.example .env   # add your API key + optional GH_TOKEN
docker compose up -d

# Scale workers
docker compose up --scale swe-agent=3 -d
```

Use a host control plane instead of the Docker service:

```bash
docker compose -f docker-compose.local.yml up -d
```

## How a Build Works

```text
Goal → PM → Architect → Tech Lead → Sprint Planner → Issue DAG
                                                         ↓
                        ┌────────────────────────────────┘
                        ↓ (parallel, isolated worktrees)
                   ┌─────────┐
                   │  Issue N │ → Coder → QA → Reviewer → Synthesizer
                   └─────────┘       ↑               │
                        ↑            └── retry ───────┘ (inner loop)
                        │
                        └── advisor / replanner (middle + outer loops)
                                                         ↓
                                    Merge → Integration Test → Verify → Draft PR
```

Three nested control loops handle task difficulty in real time:

| Loop | Scope | Trigger | Action |
|------|-------|---------|--------|
| **Inner** | Single issue | QA/review fails | Coder retries with feedback |
| **Middle** | Single issue | Inner loop exhausted | Advisor retries with new approach, splits work, or accepts with debt |
| **Outer** | Remaining DAG | Escalated failures | Replanner restructures remaining issues and dependencies |

<p align="center">
  <img src="assets/archi.png" alt="SWE-AF architecture" width="100%" />
</p>

> Typical runs spin up 400–500+ agent instances across planning, execution, QA, and verification. Larger DAGs and repeated adaptation cycles scale into the thousands.

## Benchmark

**95/100** with both Claude haiku-class routing ($20) and MiniMax M2.5 via open runtime ($6), outperforming Claude Code sonnet (73), Codex o3 (62), and Claude Code haiku (59) on the same prompt.

| Dimension | SWE-AF (haiku) | SWE-AF (MiniMax) | CC Sonnet | Codex (o3) | CC Haiku |
|-----------|---------------|-----------------|-----------|-----------|---------|
| Functional (30) | **30** | **30** | **30** | **30** | **30** |
| Structure (20) | **20** | **20** | 10 | 10 | 10 |
| Hygiene (20) | **20** | **20** | 16 | 10 | 7 |
| Git (15) | **15** | **15** | 2 | 2 | 2 |
| Quality (15) | 10 | 10 | **15** | 10 | 10 |
| **Total** | **95** | **95** | **73** | **62** | **59** |
| **Cost** | **~$20** | **~$6** | ? | ? | ? |
| **Time** | ~30–40 min | 43 min | ? | ? | ? |

<details>
<summary><strong>Full benchmark details and reproduction</strong></summary>

Same prompt tested across multiple agents. SWE-AF with Claude runtime (haiku-class model mapping) used 400+ agent instances; SWE-AF with MiniMax M2.5 via open runtime achieved identical quality at 70% cost savings.

**Prompt used for all agents:**

> Build a Node.js CLI todo app with add, list, complete, and delete commands. Data should persist to a JSON file. Initialize git, write tests, and commit your work.

### Scoring framework

| Dimension | Points | What it measures |
|-----------|--------|-----------------|
| Functional | 30 | CLI behavior and passing tests |
| Structure | 20 | Modular source layout and test organization |
| Hygiene | 20 | `.gitignore`, clean status, no junk artifacts |
| Git | 15 | Commit discipline and message quality |
| Quality | 15 | Error handling, package metadata, README quality |

### Reproduction

```bash
# SWE-AF (Claude runtime, haiku-class mapping) - $20, 30-40 min
curl -X POST http://localhost:8080/api/v1/execute/async/swe-planner.build \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{
  "input": {
    "goal": "Build a Node.js CLI todo app with add, list, complete, and delete commands. Data should persist to a JSON file. Initialize git, write tests, and commit your work.",
    "repo_path": "/tmp/swe-af-output",
    "config": {
      "runtime": "claude_code",
      "models": {
        "default": "haiku"
      }
    }
  }
}
JSON

# SWE-AF (MiniMax M2.5 via OpenRouter runtime) - $6, 43 min
curl -X POST http://localhost:8080/api/v1/execute/async/swe-planner.build \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{
  "input": {
    "goal": "Build a Node.js CLI todo app with add, list, complete, and delete commands. Data should persist to a JSON file. Initialize git, write tests, and commit your work.",
    "repo_path": "/workspaces/todo-app-benchmark",
    "config": {
      "runtime": "open_code",
      "models": {
        "default": "openrouter/minimax/minimax-m2.5"
      }
    }
  }
}
JSON

# Claude Code (haiku)
claude -p "Build a Node.js CLI todo app ..." --model haiku --dangerously-skip-permissions

# Claude Code (sonnet)
claude -p "Build a Node.js CLI todo app ..." --model sonnet --dangerously-skip-permissions

# Codex (gpt-5.3-codex)
codex exec "Build a Node.js CLI todo app ..." --full-auto
```

**MiniMax M2.5 Measured Metrics (Feb 2026):**
- 99.22% code coverage (only agent with measured coverage)
- 4 custom error types (TodoError, ValidationError, NotFoundError, StorageError)
- 999 LOC, 4 modules, 74 tests, 9 commits

**Production Quality Analysis:** [Objective comparison](examples/agent-comparison/PRODUCTION_QUALITY_ANALYSIS.md) of measurable metrics across all agents.

Benchmark assets, logs, evaluator, and generated projects live in [`examples/agent-comparison/`](examples/agent-comparison/).

</details>

## Real-World Examples

### PR #179: Go SDK — Built Entirely by SWE-AF

[PR #179: Go SDK DID/VC Registration](https://github.com/Agent-Field/agentfield/pull/179) — one API call, zero human code, haiku-class models.

| Metric | Value |
|--------|-------|
| Issues completed | 10/10 |
| Tests passing | 217 |
| Acceptance criteria | 34/34 |
| Agent invocations | 79 |
| Model | `claude-haiku-4-5` |
| **Total cost** | **$19.23** |

<details>
<summary>Cost breakdown by agent role</summary>

| Role | Cost | % |
|------|------|---|
| Coder | $5.88 | 30.6% |
| Code Reviewer | $3.48 | 18.1% |
| QA | $1.78 | 9.2% |
| GitHub PR | $1.66 | 8.6% |
| Integration Tester | $1.59 | 8.3% |
| Merger | $1.22 | 6.3% |
| Workspace Ops | $1.77 | 9.2% |
| Planning (PM + Arch + TL + Sprint) | $0.79 | 4.1% |
| Verifier + Finalize | $0.34 | 1.8% |
| Synthesizer | $0.05 | 0.2% |

79 invocations, 2,070 conversation turns. Planning agents scope and decompose; coders work in parallel isolated worktrees; reviewers and QA validate each issue; merger integrates branches; verifier checks acceptance criteria against the PRD.

</details>

### Autonomous Build Spotlight

Rust-based Python compiler benchmark (built autonomously):

| Metric | CPython (subprocess) | RustPython (SWE-AF) | Improvement |
|--------|---------------------|---------------------|-------------|
| Steady-state execution | Baseline (~19ms) | Optimized in-process runtime | **88.3x–602.3x faster** |
| Geometric mean | 1.0x baseline | 253.8x | **253.8x** |
| Peak throughput | ~52 ops/s | 31,807 ops/s | **~612x** |

<details>
<summary>Measurement methodology</summary>

Throughput comparison measures different execution models: CPython subprocess spawn (~19ms per call → ~52 ops/s) vs RustPython pre-warmed interpreter pool (in-process). This is the real-world tradeoff the system was built to optimize — replacing repeated subprocess invocations with a persistent pool for short-snippet execution.

</details>

Artifact trail includes **175 tracked autonomous agents** across planning, coding, review, merge, and verification.

Details: [`examples/llm-rust-python-compiler-sonnet/README.md`](examples/llm-rust-python-compiler-sonnet/README.md)

## Operating Modes

SWE-AF works in two modes: point it at a single repository, or orchestrate coordinated changes across multiple repos in one build.

### Single-Repository Mode

The default. Pass `repo_url` (remote) or `repo_path` (local) and SWE-AF handles everything:

```bash
curl -X POST http://localhost:8080/api/v1/execute/async/swe-planner.build \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "goal": "Add JWT auth",
      "repo_url": "https://github.com/user/my-project"
    }
  }'
```

### Multi-Repository Mode

When your work spans multiple codebases — a primary app plus shared libraries, monorepo sub-projects, or dependent microservices — pass `config.repos` as an array with roles:

```bash
curl -X POST http://localhost:8080/api/v1/execute/async/swe-planner.build \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "goal": "Add JWT auth across API and shared-lib",
      "config": {
        "repos": [
          {
            "repo_url": "https://github.com/org/main-app",
            "role": "primary"
          },
          {
            "repo_url": "https://github.com/org/shared-lib",
            "role": "dependency"
          }
        ],
        "runtime": "claude_code",
        "models": { "default": "sonnet" }
      }
    }
  }'
```

**Roles:**
- `primary` — The main application. Changes here drive the build; failures block progress.
- `dependency` — Libraries or services modified to support the primary repo. Failures are captured but don't block.

**Use cases:**
- Primary app + shared SDK or utilities library
- Monorepo sub-projects that live in separate repos
- Feature spanning multiple microservices (e.g., API + worker queue)

## One-Call DX

Every build is a single API call. Swap runtimes and assign models per agent role in one flat config:

```bash
curl -X POST http://localhost:8080/api/v1/execute/async/swe-planner.build \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{
  "input": {
    "goal": "Refactor and harden auth + billing flows",
    "repo_url": "https://github.com/user/my-project",
    "config": {
      "runtime": "claude_code",
      "models": {
        "default": "sonnet",
        "coder": "opus",
        "qa": "opus"
      },
      "enable_learning": true
    }
  }
}
JSON
```

**Runtimes supported:**
- `runtime: "claude_code"` — Claude backend (Anthropic)
- `runtime: "open_code"` — OpenCode backend (OpenRouter/OpenAI/Google/Anthropic model IDs)

For OpenRouter, use model IDs in `openrouter/<provider>/<model>` format (e.g., `openrouter/minimax/minimax-m2.5`).

## GitHub Repo Workflow

Pass `repo_url` instead of `repo_path` to let SWE-AF clone the repo and open a draft PR after the build completes.

Requirements:
- `GH_TOKEN` environment variable with `repo` scope
- Token must have access to the target repository

## API Reference

<details>
<summary><strong>Agent endpoints</strong></summary>

Core async endpoints (returns an `execution_id` immediately):

```bash
# Full build: plan → execute → verify
POST /api/v1/execute/async/swe-planner.build

# Plan only
POST /api/v1/execute/async/swe-planner.plan

# Execute a prebuilt plan
POST /api/v1/execute/async/swe-planner.execute

# Resume after interruption
POST /api/v1/execute/async/swe-planner.resume_build
```

Monitoring:

```bash
curl http://localhost:8080/api/v1/executions/<execution_id>
```

Every specialist is also callable directly:

`POST /api/v1/execute/async/swe-planner.<agent>`

</details>

<details>
<summary><strong>Agent execution flow</strong></summary>

| Agent | In → Out |
|-------|----------|
| `run_product_manager` | goal → PRD |
| `run_architect` | PRD → architecture |
| `run_tech_lead` | architecture → review |
| `run_sprint_planner` | architecture → issue DAG |
| `run_issue_writer` | issue spec → detailed issue |
| `run_coder` | issue + worktree → code + tests + commit |
| `run_qa` | worktree → test results |
| `run_code_reviewer` | worktree → quality/security review |
| `run_qa_synthesizer` | QA + review → FIX / APPROVE / BLOCK |
| `run_issue_advisor` | failure context → adapt / split / accept / escalate |
| `run_replanner` | build state + failures → restructured plan |
| `run_merger` | branches → merged output |
| `run_integration_tester` | merged repo → integration results |
| `run_verifier` | repo + PRD → acceptance pass/fail |
| `generate_fix_issues` | failed criteria → targeted fix issues |
| `run_github_pr` | branch → push + draft PR |

</details>

<details>
<summary><strong>Configuration</strong></summary>

Pass `config` to `build` or `execute`. Full schema: [`swe_af/execution/schemas.py`](swe_af/execution/schemas.py)

| Key | Default | Description |
|-----|---------|-------------|
| `runtime` | `"claude_code"` | Model runtime: `"claude_code"` or `"open_code"` |
| `models` | `null` | Flat role→model map (`default` + role keys below) |
| `max_coding_iterations` | `5` | Inner-loop retry budget |
| `max_advisor_invocations` | `2` | Middle-loop advisor budget |
| `max_replans` | `2` | Build-level replanning budget |
| `enable_issue_advisor` | `true` | Enable issue adaptation |
| `enable_replanning` | `true` | Enable global replanning |
| `enable_learning` | `false` | Enable cross-issue shared memory (continual learning) |
| `agent_timeout_seconds` | `2700` | Per-agent timeout |
| `agent_max_turns` | `150` | Tool-use turn budget |

</details>

<details>
<summary><strong>Model role keys</strong></summary>

`models` supports:

- `default`
- `pm`, `architect`, `tech_lead`, `sprint_planner`
- `coder`, `qa`, `code_reviewer`, `qa_synthesizer`
- `replan`, `retry_advisor`, `issue_writer`, `issue_advisor`
- `verifier`, `git`, `merger`, `integration_tester`

Resolution order: `runtime defaults` < `models.default` < `models.<role>`

</details>

<details>
<summary><strong>Config examples</strong></summary>

Minimal:

```json
{
  "runtime": "claude_code"
}
```

Fully customized:

```json
{
  "runtime": "open_code",
  "models": {
    "default": "minimax/minimax-m2.5",
    "pm": "openrouter/qwen/qwen-2.5-72b-instruct",
    "architect": "openrouter/qwen/qwen-2.5-72b-instruct",
    "coder": "deepseek/deepseek-chat",
    "qa": "deepseek/deepseek-chat",
    "verifier": "openrouter/qwen/qwen-2.5-72b-instruct"
  },
  "max_coding_iterations": 6,
  "enable_learning": true
}
```

</details>

<details>
<summary><strong>Artifacts</strong></summary>

```text
.artifacts/
├── plan/           # PRD, architecture, issue specs
├── execution/      # checkpoints, per-issue logs, agent outputs
└── verification/   # acceptance criteria results
```

</details>

<details>
<summary><strong>Development</strong></summary>

```bash
make test
make check
make clean
make clean-examples
```

</details>

<details>
<summary><strong>Security and community</strong></summary>

- Contribution guide: [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md)
- Code of conduct: [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
- Security policy: [`SECURITY.md`](SECURITY.md)
- Changelog: [`CHANGELOG.md`](CHANGELOG.md)
- License: [`Apache-2.0`](LICENSE)

</details>

---

SWE-AF is built on [AgentField](https://github.com/Agent-Field/agentfield) — a first step from single-agent harnesses to autonomous software engineering factories.
