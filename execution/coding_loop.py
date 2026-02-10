"""Per-issue coding loop: coder → parallel(QA, reviewer) → synthesizer.

This is the INNER loop in the three-nested-loop architecture:
  - INNER (this): coder → QA/review → synthesizer → fix/approve/block
  - MIDDLE: issue advisor diagnoses failures → adapt ACs/approach/scope
  - OUTER: replanner restructures DAG after unrecoverable failures
"""

from __future__ import annotations

import asyncio
import json
import os
import traceback
import uuid
from typing import Callable

from execution.schemas import (
    DAGState,
    ExecutionConfig,
    IssueOutcome,
    IssueResult,
)


async def _call_with_timeout(coro, timeout: int = 2700, label: str = ""):
    """Wrap a coroutine with asyncio.wait_for timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Agent call '{label}' timed out after {timeout}s")


# ---------------------------------------------------------------------------
# Iteration-level checkpoint helpers
# ---------------------------------------------------------------------------


def _iteration_state_path(artifacts_dir: str, issue_name: str) -> str:
    if not artifacts_dir:
        return ""
    return os.path.join(artifacts_dir, "execution", "iterations", f"{issue_name}.json")


def _save_iteration_state(artifacts_dir: str, issue_name: str, state: dict) -> None:
    path = _iteration_state_path(artifacts_dir, issue_name)
    if not path:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(state, f, indent=2, default=str)


def _load_iteration_state(artifacts_dir: str, issue_name: str) -> dict | None:
    path = _iteration_state_path(artifacts_dir, issue_name)
    if not path or not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


async def run_coding_loop(
    issue: dict,
    dag_state: DAGState,
    call_fn: Callable,
    node_id: str,
    config: ExecutionConfig,
    note_fn: Callable | None = None,
) -> IssueResult:
    """Run the coder → QA/review → synthesizer loop for a single issue.

    Each iteration:
      1. Coder writes code & commits
      2. QA and code reviewer run in parallel
      3. Synthesizer merges feedback and decides fix/approve/block

    Returns an IssueResult with the final outcome, including iteration_history.
    """
    issue_name = issue.get("name", "unknown")
    worktree_path = issue.get("worktree_path", dag_state.repo_path)
    branch_name = issue.get("branch_name", "")
    max_iterations = config.max_coding_iterations
    timeout = config.agent_timeout_seconds
    permission_mode = ""  # inherits from agent config

    # Project context from DAG state — gives agents the big picture
    project_context = {
        "prd_summary": dag_state.prd_summary,
        "architecture_summary": dag_state.architecture_summary,
        "prd_path": dag_state.prd_path,
        "architecture_path": dag_state.architecture_path,
        "artifacts_dir": dag_state.artifacts_dir,
        "issues_dir": dag_state.issues_dir,
        "repo_path": dag_state.repo_path,
    }

    if note_fn:
        note_fn(
            f"Coding loop starting: {issue_name} (max {max_iterations} iterations)",
            tags=["coding_loop", "start", issue_name],
        )

    feedback = ""  # merged feedback from synthesizer (empty on first pass)
    iteration_history: list[dict] = []  # summaries for stuck detection
    files_changed: list[str] = []
    start_iteration = 1

    # Resume from iteration checkpoint if available
    existing_state = _load_iteration_state(dag_state.artifacts_dir, issue_name)
    if existing_state:
        start_iteration = existing_state.get("iteration", 0) + 1
        feedback = existing_state.get("feedback", "")
        files_changed = existing_state.get("files_changed", [])
        iteration_history = existing_state.get("iteration_history", [])
        if note_fn:
            note_fn(
                f"Resuming {issue_name} from iteration {start_iteration}",
                tags=["coding_loop", "resume", issue_name],
            )

    for iteration in range(start_iteration, max_iterations + 1):
        iteration_id = str(uuid.uuid4())[:8]

        if note_fn:
            note_fn(
                f"Coding loop iteration {iteration}/{max_iterations}: {issue_name}",
                tags=["coding_loop", "iteration", issue_name],
            )

        # --- 1. CODER ---
        try:
            coder_result = await _call_with_timeout(
                call_fn(
                    f"{node_id}.run_coder",
                    issue=issue,
                    worktree_path=worktree_path,
                    feedback=feedback,
                    iteration=iteration,
                    iteration_id=iteration_id,
                    project_context=project_context,
                    model=config.coder_model,
                    permission_mode=permission_mode,
                    ai_provider=config.ai_provider,
                ),
                timeout=timeout,
                label=f"coder:{issue_name}:iter{iteration}",
            )
        except Exception as e:
            if note_fn:
                note_fn(
                    f"Coder agent failed: {issue_name} iter {iteration}: {e}",
                    tags=["coding_loop", "coder_error", issue_name],
                )
            return IssueResult(
                issue_name=issue_name,
                outcome=IssueOutcome.FAILED_UNRECOVERABLE,
                error_message=f"Coder agent failed on iteration {iteration}: {e}",
                error_context=traceback.format_exc(),
                files_changed=files_changed,
                branch_name=branch_name,
                attempts=iteration,
                iteration_history=iteration_history,
            )

        # Track files changed across iterations
        for f in coder_result.get("files_changed", []):
            if f not in files_changed:
                files_changed.append(f)

        # --- 2. QA + CODE REVIEWER (parallel with error handling) ---
        try:
            qa_coro = _call_with_timeout(
                call_fn(
                    f"{node_id}.run_qa",
                    worktree_path=worktree_path,
                    coder_result=coder_result,
                    issue=issue,
                    iteration_id=iteration_id,
                    project_context=project_context,
                    model=config.qa_model,
                    permission_mode=permission_mode,
                    ai_provider=config.ai_provider,
                ),
                timeout=timeout,
                label=f"qa:{issue_name}:iter{iteration}",
            )

            review_coro = _call_with_timeout(
                call_fn(
                    f"{node_id}.run_code_reviewer",
                    worktree_path=worktree_path,
                    coder_result=coder_result,
                    issue=issue,
                    iteration_id=iteration_id,
                    project_context=project_context,
                    model=config.code_reviewer_model,
                    permission_mode=permission_mode,
                    ai_provider=config.ai_provider,
                ),
                timeout=timeout,
                label=f"review:{issue_name}:iter{iteration}",
            )

            qa_result, review_result = await asyncio.gather(
                qa_coro, review_coro, return_exceptions=True,
            )

            # Handle individual failures
            if isinstance(qa_result, Exception):
                if note_fn:
                    note_fn(
                        f"QA agent failed: {issue_name}: {qa_result}",
                        tags=["coding_loop", "qa_error", issue_name],
                    )
                qa_result = {"passed": False, "summary": f"QA agent failed: {qa_result}"}
            if isinstance(review_result, Exception):
                if note_fn:
                    note_fn(
                        f"Review agent failed: {issue_name}: {review_result}",
                        tags=["coding_loop", "review_error", issue_name],
                    )
                review_result = {"approved": True, "blocking": False, "summary": f"Review unavailable: {review_result}"}
        except Exception as e:
            # Both failed — use safe defaults
            if note_fn:
                note_fn(
                    f"QA+Review both failed: {issue_name}: {e}",
                    tags=["coding_loop", "qa_review_error", issue_name],
                )
            qa_result = {"passed": False, "summary": f"QA unavailable: {e}"}
            review_result = {"approved": True, "blocking": False, "summary": "Review unavailable"}

        if note_fn:
            note_fn(
                f"QA: passed={qa_result.get('passed')}, "
                f"Review: approved={review_result.get('approved')}, "
                f"blocking={review_result.get('blocking')}",
                tags=["coding_loop", "feedback", issue_name],
            )

        # --- 3. SYNTHESIZER (with fallback) ---
        try:
            synthesis_result = await _call_with_timeout(
                call_fn(
                    f"{node_id}.run_qa_synthesizer",
                    qa_result=qa_result,
                    review_result=review_result,
                    iteration_history=iteration_history,
                    iteration_id=iteration_id,
                    worktree_path=worktree_path,
                    issue_summary={
                        "name": issue.get("name", ""),
                        "title": issue.get("title", ""),
                        "acceptance_criteria": issue.get("acceptance_criteria", []),
                    },
                    artifacts_dir=project_context.get("artifacts_dir", ""),
                    model=config.qa_synthesizer_model,
                    permission_mode=permission_mode,
                    ai_provider=config.ai_provider,
                ),
                timeout=timeout,
                label=f"synthesizer:{issue_name}:iter{iteration}",
            )
        except Exception as e:
            if note_fn:
                note_fn(
                    f"Synthesizer failed: {issue_name}: {e} — using fallback",
                    tags=["coding_loop", "synthesizer_error", issue_name],
                )
            # Smart fallback: derive action from raw QA/review results
            qa_passed = qa_result.get("passed", False)
            review_approved = review_result.get("approved", False)
            review_blocking = review_result.get("blocking", False)
            if qa_passed and review_approved and not review_blocking:
                synthesis_result = {"action": "approve", "summary": "Auto-approved (synthesizer unavailable)"}
            elif review_blocking:
                synthesis_result = {"action": "block", "summary": f"Blocked by review (synthesizer unavailable): {review_result.get('summary', '')}"}
            else:
                synthesis_result = {"action": "fix", "summary": f"Auto-fix (synthesizer unavailable): QA={qa_result.get('summary','')}, Review={review_result.get('summary','')}"}

        action = synthesis_result.get("action", "fix")
        summary = synthesis_result.get("summary", "")

        # Record iteration for history
        iteration_history.append({
            "iteration": iteration,
            "action": action,
            "summary": summary,
            "qa_passed": qa_result.get("passed", False),
            "review_approved": review_result.get("approved", False),
            "review_blocking": review_result.get("blocking", False),
        })

        if note_fn:
            note_fn(
                f"Synthesis decision: {action} — {summary[:100]}",
                tags=["coding_loop", "synthesis", issue_name],
            )

        # Save iteration-level checkpoint
        _save_iteration_state(dag_state.artifacts_dir, issue_name, {
            "iteration": iteration,
            "feedback": summary,
            "files_changed": files_changed,
            "iteration_history": iteration_history,
        })

        # --- 4. BRANCH ON ACTION ---
        if action == "approve":
            if note_fn:
                note_fn(
                    f"Coding loop APPROVED: {issue_name} after {iteration} iteration(s)",
                    tags=["coding_loop", "complete", issue_name],
                )
            return IssueResult(
                issue_name=issue_name,
                outcome=IssueOutcome.COMPLETED,
                result_summary=summary,
                files_changed=files_changed,
                branch_name=branch_name,
                attempts=iteration,
                iteration_history=iteration_history,
            )

        if action == "block":
            if note_fn:
                note_fn(
                    f"Coding loop BLOCKED: {issue_name} — {summary}",
                    tags=["coding_loop", "blocked", issue_name],
                )
            return IssueResult(
                issue_name=issue_name,
                outcome=IssueOutcome.FAILED_UNRECOVERABLE,
                error_message=summary,
                files_changed=files_changed,
                branch_name=branch_name,
                attempts=iteration,
                iteration_history=iteration_history,
            )

        # action == "fix" — read feedback file and continue
        feedback = summary

        # Stuck detection from synthesizer
        if synthesis_result.get("stuck", False):
            if note_fn:
                note_fn(
                    f"Coding loop STUCK: {issue_name} — breaking after {iteration} iterations",
                    tags=["coding_loop", "stuck", issue_name],
                )
            return IssueResult(
                issue_name=issue_name,
                outcome=IssueOutcome.FAILED_UNRECOVERABLE,
                error_message=f"Stuck loop detected: {summary}",
                files_changed=files_changed,
                branch_name=branch_name,
                attempts=iteration,
                iteration_history=iteration_history,
            )

    # Loop exhausted without approval
    if note_fn:
        note_fn(
            f"Coding loop exhausted: {issue_name} after {max_iterations} iterations",
            tags=["coding_loop", "exhausted", issue_name],
        )

    return IssueResult(
        issue_name=issue_name,
        outcome=IssueOutcome.FAILED_UNRECOVERABLE,
        error_message=f"Coding loop exhausted after {max_iterations} iterations without approval",
        files_changed=files_changed,
        branch_name=branch_name,
        attempts=max_iterations,
        iteration_history=iteration_history,
    )
