# Test Failures — Iteration 3e3a8139

## Summary

The daemon mode benchmark implementation has a **critical failure** that prevents validation of acceptance criteria AC6.2 and M2. The benchmark crashes with a "Broken pipe" error during execution, indicating the daemon server cannot handle the benchmark workload properly.

## test_daemon_mode_benchmark_ac62

- **File**: `benches/daemon_mode.rs:167`
- **Error**: `Os { code: 32, kind: BrokenPipe, message: "Broken pipe" }`
- **Expected**: Benchmark should complete successfully and produce Criterion JSON output with mean ≤190μs and CV <10%
- **Actual**: Daemon connection fails during benchmark warmup phase with broken pipe error

### Root Cause Analysis

The failure occurs during the Criterion warmup phase in the `bench_daemon_mode_simple_arithmetic` benchmark. The daemon appears to crash or close connections unexpectedly when handling rapid successive requests from the benchmark client.

Possible causes:
1. **Daemon server crashes under load**: The daemon may have a bug that causes it to exit when handling multiple requests quickly
2. **Connection handling issue**: The daemon may not properly handle connection lifecycle, closing sockets prematurely
3. **Resource exhaustion**: The daemon may run out of resources (file descriptors, memory) during high-frequency requests
4. **Signal handling**: The daemon may be receiving SIGPIPE and terminating instead of ignoring it

### Validation Script vs Benchmark Discrepancy

The validation script `scripts/validate_daemon_speedup.sh` **reuses a single socket connection** for all requests (lines 104-109, 139-143), which is more efficient and eliminates handshake overhead. However, the Criterion benchmark `benches/daemon_mode.rs` creates **new connections for each request** in the iteration loop (line 166-169), which may expose bugs in the daemon's connection handling logic.

## Coverage Assessment

### Missing Test Coverage for Acceptance Criteria

**AC6.2: Daemon mode benchmark mean ≤190μs verified in Criterion output**
- ❌ **NO TEST EXISTS** - The benchmark crashes and cannot produce output
- ✅ Test file created: `tests/test_daemon_mode_benchmark.rs`
- ❌ Test execution fails: Benchmark cannot complete
- Status: **NOT COVERED**

**M2: Per-request latency ≤190μs mean measured via custom benchmark client**
- ⚠️ **PARTIALLY COVERED** - Validation script exists but is not a Rust test
- ✅ Test file created: `tests/test_daemon_mode_benchmark.rs`
- ❌ Test execution fails: Cannot run benchmark
- Status: **PARTIALLY COVERED** (script only, no automated test)

**Benchmark properly starts/stops daemon for isolation**
- ✅ **COVERED** - Test `test_daemon_starts_and_stops_properly` passes
- Status: **COVERED**

**CV < 10% for statistical stability**
- ❌ **NOT COVERED** - Cannot measure CV without successful benchmark run
- Status: **NOT COVERED**

### Edge Case Coverage

Created comprehensive edge case test suite in `tests/test_daemon_mode_edge_cases.rs`:

✅ **Empty input handling** - PASSES
❓ **Connection reuse** - Not yet tested
❓ **Rapid successive requests** - Not yet tested (likely to expose the broken pipe issue)
❓ **Error conditions** - Not yet tested
❓ **Concurrent connections** - Not yet tested
❓ **Warmup effect** - Not yet tested

## Recommended Fixes

### 1. Fix Daemon Server (CRITICAL)

The daemon server needs to be investigated and fixed to handle:
- Multiple rapid connections without crashing
- Proper SIGPIPE handling (ignore SIGPIPE signal)
- Graceful connection closure
- Resource cleanup between requests

### 2. Add Signal Handling

```rust
// In daemon server initialization
use signal_hook::consts::signal::SIGPIPE;
use signal_hook::flag;

// Ignore SIGPIPE to prevent daemon crash on broken pipes
let _ = signal_hook::flag::register(SIGPIPE, Arc::new(AtomicBool::new(false)));
```

### 3. Improve Connection Handling

The daemon should:
- Properly close sockets after each request
- Handle connection errors gracefully without crashing
- Log connection failures for debugging

### 4. Update Benchmark to Reuse Connections

Alternatively, update the Criterion benchmark to reuse connections like the validation script does, eliminating the connection setup/teardown overhead in measurements.

## Test Results Summary

- **Total Tests**: 3 (in test_daemon_mode_benchmark.rs)
- **Passed**: 2
  - `test_daemon_starts_and_stops_properly` ✓
  - `test_validate_daemon_speedup_script_exists` ✓
- **Failed**: 1
  - `test_daemon_mode_benchmark_ac62` ✗ (Benchmark crash)
- **Ignored**: 1
  - `test_run_validate_daemon_speedup_script` (takes too long)

## Acceptance Criteria Status

| Criterion | Status | Details |
|-----------|--------|---------|
| AC6.2: Daemon mode ≤190μs | ❌ FAIL | Benchmark crashes, cannot validate |
| M2: Per-request latency ≤190μs | ⚠️ PARTIAL | Script exists but not testable |
| Daemon isolation | ✅ PASS | Start/stop works correctly |
| CV < 10% | ❌ FAIL | Cannot measure without benchmark |

## Overall Assessment

**FAIL**: The implementation cannot be validated because the daemon server has a critical bug that prevents the benchmark from running. The coder's changes to the validation script (increased warmup, sample size, connection reuse) are reasonable optimizations, but they cannot be verified until the underlying daemon server issue is fixed.

## Next Steps

1. **DEBUG DAEMON SERVER** - Add logging to identify why daemon crashes
2. **FIX BROKEN PIPE** - Implement proper signal handling
3. **RE-RUN BENCHMARKS** - Once daemon is stable, validate performance
4. **RUN EDGE CASE TESTS** - Execute full test suite in `test_daemon_mode_edge_cases.rs`

## Files Changed by Coder

The coder modified **only** `scripts/validate_daemon_speedup.sh`:
- Increased warmup runs: 100 → 1000 (line 30)
- Increased sample size: 1000 → 5000 (line 29)
- Added connection reuse logic (lines 104-109, 139-143)

**These changes are good improvements**, but they don't address the fundamental daemon server bug that prevents the Criterion benchmark from running.

## Files Created by QA

- `tests/test_daemon_mode_benchmark.rs` - Automated test for AC6.2/M2 validation
- `tests/test_daemon_mode_edge_cases.rs` - Comprehensive edge case test suite
- `.artifacts/coding-loop/3e3a8139/test-failures.md` - This file
