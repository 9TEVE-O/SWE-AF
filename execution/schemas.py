"""Pydantic schemas for DAG execution state and replanning."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel

# Global default for all agent max_turns. Change this one value to adjust everywhere.
DEFAULT_AGENT_MAX_TURNS: int = 150


class AdvisorAction(str, Enum):
    """What the Issue Advisor decided to do after a coding loop failure."""

    RETRY_MODIFIED = "retry_modified"          # Relax ACs, retry coding loop
    RETRY_APPROACH = "retry_approach"          # Keep ACs, different strategy
    SPLIT = "split"                            # Break into sub-issues
    ACCEPT_WITH_DEBT = "accept_with_debt"      # Close enough, record gaps
    ESCALATE_TO_REPLAN = "escalate_to_replan"  # Flag for outer loop


class IssueOutcome(str, Enum):
    """Outcome of executing a single issue."""

    COMPLETED = "completed"
    COMPLETED_WITH_DEBT = "completed_with_debt"   # Accepted via ACCEPT_WITH_DEBT
    FAILED_RETRYABLE = "failed_retryable"
    FAILED_UNRECOVERABLE = "failed_unrecoverable"
    FAILED_NEEDS_SPLIT = "failed_needs_split"     # Advisor wants to split
    FAILED_ESCALATED = "failed_escalated"         # Advisor escalated to replanner
    SKIPPED = "skipped"


class IssueAdaptation(BaseModel):
    """Records one AC/scope modification. Accumulated as technical debt."""

    adaptation_type: AdvisorAction
    original_acceptance_criteria: list[str] = []
    modified_acceptance_criteria: list[str] = []
    dropped_criteria: list[str] = []
    failure_diagnosis: str = ""
    rationale: str = ""
    new_approach: str = ""
    missing_functionality: list[str] = []
    downstream_impact: str = ""
    severity: str = "medium"


class SplitIssueSpec(BaseModel):
    """Sub-issue spec when advisor decides to SPLIT."""

    name: str
    title: str
    description: str
    acceptance_criteria: list[str]
    depends_on: list[str] = []
    provides: list[str] = []
    files_to_create: list[str] = []
    files_to_modify: list[str] = []
    parent_issue_name: str = ""


class IssueAdvisorDecision(BaseModel):
    """Structured output from the Issue Advisor agent."""

    action: AdvisorAction
    failure_diagnosis: str
    failure_category: str = ""   # environment|logic|dependency|approach|scope
    rationale: str
    confidence: float = 0.5
    # RETRY_MODIFIED
    modified_acceptance_criteria: list[str] = []
    dropped_criteria: list[str] = []
    modification_justification: str = ""
    # RETRY_APPROACH
    new_approach: str = ""
    approach_changes: list[str] = []
    # SPLIT
    sub_issues: list[SplitIssueSpec] = []
    split_rationale: str = ""
    # ACCEPT_WITH_DEBT
    missing_functionality: list[str] = []
    debt_severity: str = "medium"
    # ESCALATE_TO_REPLAN
    escalation_reason: str = ""
    dag_impact: str = ""
    suggested_restructuring: str = ""
    # Always
    downstream_impact: str = ""
    summary: str = ""


class IssueResult(BaseModel):
    """Result of executing a single issue."""

    issue_name: str
    outcome: IssueOutcome
    result_summary: str = ""
    error_message: str = ""
    error_context: str = ""  # traceback/logs for replanner
    attempts: int = 1
    files_changed: list[str] = []
    branch_name: str = ""
    # Advisor fields
    advisor_invocations: int = 0
    adaptations: list[IssueAdaptation] = []
    debt_items: list[dict] = []
    split_request: list[SplitIssueSpec] | None = None
    escalation_context: str = ""
    final_acceptance_criteria: list[str] = []
    iteration_history: list[dict] = []


class LevelResult(BaseModel):
    """Aggregated result of executing all issues in a single level."""

    level_index: int
    completed: list[IssueResult] = []
    failed: list[IssueResult] = []
    skipped: list[IssueResult] = []


class ReplanAction(str, Enum):
    """What the replanner decided to do."""

    CONTINUE = "continue"  # proceed unchanged
    MODIFY_DAG = "modify_dag"  # restructured
    REDUCE_SCOPE = "reduce_scope"  # dropped non-essential issues
    ABORT = "abort"  # cannot recover


class ReplanDecision(BaseModel):
    """Structured output from the replanner agent."""

    action: ReplanAction
    rationale: str
    updated_issues: list[dict] = []  # modified remaining issues
    removed_issue_names: list[str] = []
    skipped_issue_names: list[str] = []
    new_issues: list[dict] = []
    summary: str = ""


class DAGState(BaseModel):
    """Full execution state of the DAG — passed to replanner for context."""

    # --- Artifact paths (so any agent can read the full context) ---
    repo_path: str = ""
    artifacts_dir: str = ""
    prd_path: str = ""
    architecture_path: str = ""
    issues_dir: str = ""

    # --- Plan context (summaries for quick reference by replanner) ---
    original_plan_summary: str = ""
    prd_summary: str = ""
    architecture_summary: str = ""

    # --- Issue tracking ---
    all_issues: list[dict] = []  # full PlannedIssue dicts
    levels: list[list[str]] = []  # parallel execution levels

    # --- Execution progress ---
    completed_issues: list[IssueResult] = []
    failed_issues: list[IssueResult] = []
    skipped_issues: list[str] = []
    in_flight_issues: list[str] = []  # names of issues currently executing
    current_level: int = 0

    # --- Replan tracking ---
    replan_count: int = 0
    replan_history: list[ReplanDecision] = []
    max_replans: int = 2

    # --- Git branch tracking ---
    git_integration_branch: str = ""
    git_original_branch: str = ""
    git_initial_commit: str = ""
    git_mode: str = ""  # "fresh" or "existing"
    pending_merge_branches: list[str] = []
    merged_branches: list[str] = []
    unmerged_branches: list[str] = []  # branches that failed to merge
    worktrees_dir: str = ""  # e.g. repo_path/.worktrees

    # --- Merge/test history ---
    merge_results: list[dict] = []
    integration_test_results: list[dict] = []

    # --- Debt tracking ---
    accumulated_debt: list[dict] = []
    adaptation_history: list[dict] = []


class GitInitResult(BaseModel):
    """Result of git initialization."""

    mode: str  # "fresh" or "existing"
    original_branch: str  # "" for fresh, e.g. "main" for existing
    integration_branch: str  # branch where merged work accumulates
    initial_commit_sha: str  # commit SHA before any work
    success: bool
    error_message: str = ""


class WorkspaceInfo(BaseModel):
    """Info about a worktree created for an issue."""

    issue_name: str
    branch_name: str
    worktree_path: str


class MergeResult(BaseModel):
    """Structured output from the merger agent."""

    success: bool
    merged_branches: list[str]
    failed_branches: list[str]
    conflict_resolutions: list[dict] = []  # [{file, branches, resolution_strategy}]
    merge_commit_sha: str = ""
    pre_merge_sha: str = ""  # for potential rollback
    needs_integration_test: bool
    integration_test_rationale: str = ""
    summary: str


class IntegrationTestResult(BaseModel):
    """Result of integration testing after a merge."""

    passed: bool
    tests_written: list[str] = []  # test file paths
    tests_run: int
    tests_passed: int
    tests_failed: int
    failure_details: list[dict] = []  # [{test_name, error, file}]
    summary: str


class RetryAdvice(BaseModel):
    """Structured output from the retry advisor agent."""

    should_retry: bool
    diagnosis: str  # Root cause analysis
    strategy: str  # What to do differently
    modified_context: str  # Additional guidance to inject into retry
    confidence: float = 0.5  # 0.0-1.0


class CriterionResult(BaseModel):
    """Verification result for a single acceptance criterion."""

    criterion: str
    passed: bool
    evidence: str  # What the verifier found
    issue_name: str = ""  # Which issue was responsible


class VerificationResult(BaseModel):
    """Structured output from the verifier agent."""

    passed: bool
    criteria_results: list[CriterionResult]
    summary: str
    suggested_fixes: list[str] = []


# ---------------------------------------------------------------------------
# Phase 4: Coding loop schemas
# ---------------------------------------------------------------------------


class CoderResult(BaseModel):
    """Output from the coder agent."""

    files_changed: list[str] = []
    summary: str = ""
    complete: bool = True
    iteration_id: str = ""


class QAResult(BaseModel):
    """Output from the QA/tester agent."""

    passed: bool
    summary: str = ""
    failures_file: str = ""  # path to detailed failures (in .artifacts/)
    iteration_id: str = ""


class CodeReviewResult(BaseModel):
    """Output from the code reviewer agent."""

    approved: bool
    summary: str = ""
    issues_file: str = ""  # path to detailed issues (in .artifacts/)
    blocking: bool = False  # True ONLY for security/crash/data-loss
    debt_items: list[dict[str, Any]] = []  # [{severity, title, file_path, description}]
    iteration_id: str = ""


class QASynthesisAction(str, Enum):
    """Decision from the feedback synthesizer."""

    FIX = "fix"
    APPROVE = "approve"
    BLOCK = "block"


class QASynthesisResult(BaseModel):
    """Output from the feedback synthesizer agent."""

    action: QASynthesisAction
    summary: str = ""
    feedback_file: str = ""  # path to merged feedback for coder
    stuck: bool = False
    iteration_id: str = ""


class CodingLoopConfig(BaseModel):
    """Configuration for the per-issue coding loop."""

    max_coding_iterations: int = 5
    coder_model: str = "sonnet"
    qa_model: str = "sonnet"
    reviewer_model: str = "sonnet"
    synthesizer_model: str = "haiku"  # lightweight decision agent


class BuildConfig(BaseModel):
    """Configuration for the end-to-end build pipeline."""

    # Planning
    pm_model: str = "sonnet"
    architect_model: str = "sonnet"
    tech_lead_model: str = "sonnet"
    sprint_planner_model: str = "sonnet"
    max_review_iterations: int = 2
    # Execution
    max_retries_per_issue: int = 2
    max_replans: int = 2
    enable_replanning: bool = True
    replan_model: str = "sonnet"
    retry_advisor_model: str = "sonnet"
    issue_writer_model: str = "sonnet"
    # Verification
    verifier_model: str = "sonnet"
    max_verify_fix_cycles: int = 1
    # Git / Merge
    git_model: str = "sonnet"
    merger_model: str = "sonnet"
    integration_tester_model: str = "sonnet"
    max_integration_test_retries: int = 1
    enable_integration_testing: bool = True
    # Coding loop
    max_coding_iterations: int = 5
    coder_model: str = "sonnet"
    qa_model: str = "sonnet"
    code_reviewer_model: str = "sonnet"
    qa_synthesizer_model: str = "haiku"
    # Agent limits
    agent_max_turns: int = DEFAULT_AGENT_MAX_TURNS
    # Target
    execute_fn_target: str = ""
    ai_provider: Literal["claude", "codex"] = "claude"
    permission_mode: str = ""
    # Issue Advisor
    agent_timeout_seconds: int = 2700
    issue_advisor_model: str = "sonnet"
    max_advisor_invocations: int = 2
    enable_issue_advisor: bool = True


class BuildResult(BaseModel):
    """Final output of the end-to-end build pipeline."""

    plan_result: dict
    dag_state: dict
    verification: dict | None = None
    success: bool
    summary: str


class ExecutionConfig(BaseModel):
    """Configuration for the DAG executor."""

    max_retries_per_issue: int = 1
    max_replans: int = 2
    replan_model: str = "sonnet"
    enable_replanning: bool = True
    retry_advisor_model: str = "sonnet"
    issue_writer_model: str = "sonnet"
    merger_model: str = "sonnet"
    integration_tester_model: str = "sonnet"
    max_integration_test_retries: int = 1
    enable_integration_testing: bool = True
    # Coding loop
    max_coding_iterations: int = 5
    coder_model: str = "sonnet"
    qa_model: str = "sonnet"
    code_reviewer_model: str = "sonnet"
    qa_synthesizer_model: str = "haiku"
    # Agent limits
    agent_max_turns: int = DEFAULT_AGENT_MAX_TURNS
    ai_provider: Literal["claude", "codex"] = "claude"
    # Issue Advisor
    agent_timeout_seconds: int = 2700       # 45 min
    issue_advisor_model: str = "sonnet"
    max_advisor_invocations: int = 2
    enable_issue_advisor: bool = True
