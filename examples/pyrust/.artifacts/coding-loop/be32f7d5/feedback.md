# Feedback: FIX Required

## Critical Issue - Daemon Sleep Bug (MUST FIX)

**File**: `src/daemon.rs:199`
**Problem**: Daemon server has 100ms sleep causing 516x latency over target (98ms actual vs 190μs target)
**Fix**: Change `Duration::from_millis(100)` to `Duration::from_micros(100)`

This single-character bug is preventing all acceptance criteria from passing. The benchmark implementation is correct, but the underlying daemon is broken.

## Secondary Issue - Validation Script Measures Wrong Metric

**File**: `scripts/validate_daemon_performance.sh`
**Problem**: Script measures CLI overhead (subprocess spawn + socket communication) instead of pure socket latency
**Fix**: Update validation script to measure socket-only communication like the Criterion benchmarks do (direct Unix socket client)

## Action Required

1. **Fix daemon.rs:199**: Change milliseconds to microseconds
2. **Fix validation script**: Measure socket latency, not CLI overhead
3. **Re-run benchmarks**: After daemon fix, all benchmarks should pass AC6.2 (mean ≤190μs)

## Non-Blocking Debt Items (Track for Follow-up)

The code review identified 7 technical debt items that should be addressed in future work but are NOT blocking this issue:

- Missing test coverage for daemon startup/1000 requests
- Test isolation between benchmarks (cleanup on crash)
- Misleading benchmark name (throughput vs single request)
- Python dependency without fallback validation
- Magic numbers in daemon startup wait loop
- Configuration mismatch (30s vs 10s measurement_time)
- Hardcoded baseline in validation script (19ms)

These can be tracked separately and do not need to be fixed for this issue to be approved.

## Expected Outcome After Fix

After fixing the daemon sleep bug, benchmarks should show:
- Mean latency: ≤190μs (target met)
- CV: <10% (statistical stability)
- All 9 Criterion benchmarks passing
- Validation script confirming performance
