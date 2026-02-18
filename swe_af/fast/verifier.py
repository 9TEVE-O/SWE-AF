"""swe_af.fast.verifier — FastBuild single-pass verification reasoner.

Registers ``fast_verify`` on the shared ``fast_router``.  The function
performs exactly one verification pass — there are no fix cycles.
"""

from __future__ import annotations

import logging
from typing import Any

from swe_af.fast import fast_router
from swe_af.fast.schemas import FastVerificationResult

logger = logging.getLogger(__name__)


@fast_router.reasoner()
async def fast_verify(
    *,
    prd: str,
    repo_path: str,
    task_results: list[dict[str, Any]],
    verifier_model: str,
    permission_mode: str,
    ai_provider: str,
    artifacts_dir: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Run a single verification pass against the built repository.

    Calls ``run_verifier`` via a lazy import of ``swe_af.fast.app`` to
    avoid circular imports at module load time.  No fix cycles are
    attempted — this is a single-pass reasoner.

    Args:
        prd: The product requirements document text.
        repo_path: Absolute path to the repository to verify.
        task_results: List of task result dicts from the execution phase.
        verifier_model: Model name string for the verifier agent.
        permission_mode: Permission mode string passed to the agent runtime.
        ai_provider: AI provider identifier string.
        artifacts_dir: Path to the artifacts directory.
        **kwargs: Additional keyword arguments forwarded to the agent call.

    Returns:
        A :class:`~swe_af.fast.schemas.FastVerificationResult` serialised
        as a plain dict.
    """
    try:
        import swe_af.fast.app as _app  # noqa: PLC0415

        result: dict[str, Any] = await _app.app.call(
            "run_verifier",
            prd=prd,
            repo_path=repo_path,
            task_results=task_results,
            verifier_model=verifier_model,
            permission_mode=permission_mode,
            ai_provider=ai_provider,
            artifacts_dir=artifacts_dir,
            **kwargs,
        )
        # Ensure the result conforms to FastVerificationResult
        verification = FastVerificationResult(
            passed=result.get("passed", False),
            summary=result.get("summary", ""),
            criteria_results=result.get("criteria_results", []),
            suggested_fixes=result.get("suggested_fixes", []),
        )
        return verification.model_dump()
    except Exception as exc:  # noqa: BLE001
        logger.exception("fast_verify: verification agent raised an exception")
        fallback = FastVerificationResult(
            passed=False,
            summary=f"Verification agent failed: {exc}",
        )
        return fallback.model_dump()


__all__ = ["fast_verify"]
