# Feedback: compiler-benchmarks Issue

## Decision: BLOCK

This issue cannot be completed as specified due to a fundamental mismatch between acceptance criteria and physical measurement constraints.

## Root Cause Analysis

**AC4 Requirement**: CV < 5% for all benchmarks
**Actual Performance**:
- compiler_simple: 8.12% CV (203ns operation)
- compiler_complex: 5.12% CV (330ns operation)
- compiler_variables: 6.86% CV (381ns operation)

**Why This Cannot Be Fixed**: All three benchmarks operate at nanosecond timescales (<500ns). At this scale, system noise (CPU scheduler jitter, cache effects, thermal noise) dominates measurement variance. Your codebase's own architecture document acknowledges this limitation, predicting 42% CV for compiler_simple due to inherent measurement noise.

## What's Working

✅ **AC1-AC3 Fully Satisfied**:
- benches/compiler_benchmarks.rs created with all 3 required benchmarks
- AST correctly pre-parsed outside measurement loop (lexer::lex() + parser::parse())
- Criterion generates estimates.json for each benchmark

✅ **Code Quality**: Implementation is architecturally sound with proper black_box usage, no regressions (344 library tests pass), and code reviewer approved it with no blocking issues.

## Recommended Resolution

This is a **specification problem**, not an implementation defect. You have two options:

1. **Relax AC4**: Change requirement to CV < 10% or CV < 15% for sub-500ns benchmarks, which aligns with measurement theory
2. **Accept Documented Variance**: Keep current implementation and document the expected 5-10% CV as expected behavior for compiler-only benchmarks

The code reviewer explicitly recommended this path. Further iterations will not improve CV below 5% without fundamentally changing what's being measured (e.g., making operations take microseconds instead of nanoseconds).

## No Action Required

Do not attempt additional iterations. Escalate the acceptance criteria to stakeholders for alignment with physical measurement constraints.
