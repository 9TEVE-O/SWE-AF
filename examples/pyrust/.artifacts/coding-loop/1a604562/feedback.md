# Feedback: parser-benchmarks Issue

## Decision: BLOCK

This issue is stuck in an unproductive loop and cannot be completed with continued iterations.

## Analysis

### The Core Problem
You have correctly implemented the structural requirements (AC1-AC3):
- ✓ benches/parser_benchmarks.rs created with three benchmarks (parser_simple, parser_complex, parser_variables)
- ✓ Input pre-tokenized outside benchmark loops
- ✓ Criterion generates estimates.json files

However, **AC4 (CV < 5% for all benchmarks) fails across all three benchmarks**, and this failure pattern has persisted through 3 iterations.

### Why Further Iteration Won't Help
The root cause (identified in QA) is **architectural, not a parameter tuning issue**:
- Parser operations are extremely fast: 80-250ns per parse
- Current approach batches 12,000 iterations per sample → measurements of 1-4ms
- At this measurement duration, system noise, thermal throttling, and cache effects dominate
- Increasing Criterion parameters (sample_size, measurement_time, warm_up_time) in iteration 2 did NOT resolve the issue
- CV remains 6-39% across benchmarks, well above the 5% target

### The Stuck Pattern
- **Iteration 1**: CV failures (18.37%, 7.94%, 19.09%) → Recommendation: tune parameters
- **Iteration 2**: You increased sample_size to 1000, measurement_time to 30s, warm_up_time to 5s → CV failures persist (8.88%, 39.04%, 6.45%)
- **Iteration 3**: Same failures despite parameter tuning in iteration 2

This is a classic stuck loop: the approach taken in iteration 2 (the recommended fix from iteration 1) has proven insufficient after being fully implemented.

## Why This Cannot Be Completed Now

The benchmark architecture needs fundamental redesign:

**Option A: Remove the iteration loop entirely**
- Let Criterion automatically determine iteration count
- Criterion will adjust iterations to keep measurement time in the sweet spot for accurate measurements
- This allows Criterion to compensate for the fast operation timing

**Option B: Significantly reduce iteration count**
- Use 100-500 iterations per sample instead of 12,000
- Keeps individual measurements in the microsecond range where system noise is proportional
- Allows Criterion parameters to be effective

The current 12,000-iteration batching approach conflicts with the Criterion design philosophy for accurate measurement of fast operations. This is a fundamental mismatch, not a tuning problem.

## Recommendation

**Escalate to the issue stakeholder.** The benchmark design needs to be reconsidered:
1. Clarify if the CV < 5% target is realistic for measuring 80-250ns operations on a general-purpose machine
2. If CV < 5% is required, reconsider the benchmark architecture (Option A or B above)
3. If a higher CV tolerance is acceptable for parser_complex (currently 39%), update the acceptance criteria

The current implementation cannot satisfy AC4 through continued iterations.
