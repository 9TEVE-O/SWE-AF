# Feedback: compiler-benchmarks

## Status: FIX REQUIRED

**AC4 (CV < 5%) is not met.** This is a hard requirement per PRD. Only 1 of 3 benchmarks passes:
- compiler_simple: 2.71% ✓ PASS
- compiler_complex: 134.53% ✗ FAIL (extreme instability)
- compiler_variables: 14.09% ✗ FAIL

AC1-AC3 are complete (benchmarks created, pre-parsed, output files generated). Code structure and quality are good. The issue is measurement stability.

## Root Cause (from QA analysis)

The compiler_complex benchmark shows severe variance (>100% CV), likely caused by:
- Memory allocation variance from nested AST structures
- Cache effects from complex compiler operations
- System interference (background processes, CPU scaling)
- Outliers affecting 13.9% of samples

## Action Required

**Priority 1: Increase measurement duration and sample size**
- In `benches/compiler_benchmarks.rs`, increase Criterion's sample size and measurement time for compiler_complex and compiler_variables
- Example: modify `.sample_size(100)` (or higher) and `.measurement_time(std::time::Duration::from_secs(10))` for unstable benchmarks
- This reduces impact of measurement noise

**Priority 2: Stabilize system environment**
- Disable CPU frequency scaling during test execution
- Close background applications
- Consider running benchmarks with reduced system load

**Priority 3: Profile memory allocation variance**
- Use `perf` or profiling tools to check if AST construction variance is the culprit
- Consider simplifying the compiler_complex test case if possible without losing benchmark value

**Priority 4: Re-run benchmarks**
- After changes, verify CV < 5% for all three benchmarks
- Ensure estimates.json is regenerated with stable measurements

## Non-blocking

The missing automated test coverage (SHOULD_FIX debt item) can be addressed in a follow-up—it does not block this merge once AC4 is satisfied.

---

**Success Criteria for Next Iteration:**
- All 3 benchmarks have CV < 5%
- All estimates.json files are present and valid
- No regressions to unit tests (344 tests still pass)
