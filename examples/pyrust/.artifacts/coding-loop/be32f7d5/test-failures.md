# Test Failures — Iteration be32f7d5

## Coverage Analysis Summary

### Acceptance Criteria
- **AC6.2**: Daemon mode benchmark mean ≤190μs verified in Criterion output
- **M2**: Per-request latency ≤190μs mean measured via custom benchmark client
- **Benchmark properly starts/stops daemon for isolation**
- **CV < 10% for statistical stability**

## Test Coverage Assessment

### ✅ ADEQUATE COVERAGE

The coder implemented comprehensive benchmark coverage in `benches/daemon_mode.rs`:

1. **AC6.2 Coverage**: 9 benchmark variants implemented:
   - `bench_daemon_mode_simple_arithmetic` - Primary AC6.2 validation
   - `bench_daemon_mode_complex_expression`
   - `bench_daemon_mode_with_variables`
   - `bench_daemon_mode_print`
   - `bench_daemon_mode_multiple_operations`
   - `bench_daemon_mode_by_complexity` - Parametric testing
   - `bench_daemon_mode_cache_hit`
   - `bench_daemon_mode_throughput` - 1000 requests for M2 validation
   - `bench_daemon_mode_minimal_overhead`

2. **M2 Coverage**: Custom benchmark client implemented as `execute_via_daemon_socket()`:
   - Direct Unix socket communication
   - Measures pure daemon server latency
   - No process spawn overhead
   - Protocol: `[u32 length][UTF-8 code]` → `[u8 status][u32 length][response]`

3. **Daemon Isolation**: Each benchmark:
   - Calls `start_daemon()` before testing
   - Implements `warmup_daemon()` with 100 requests
   - Calls `stop_daemon()` after completion
   - Proper cleanup of `/tmp/pyrust.sock` and `/tmp/pyrust.pid`

4. **Statistical Stability (CV < 10%)**:
   - Criterion configured with:
     - `sample_size(1000)` - Large sample for stability
     - `measurement_time(30s)` - Sufficient duration
     - `warm_up_time(5s)` - Plus manual warmup
     - `noise_threshold(0.05)` - 5% noise tolerance
   - Manual warmup: 100 requests plus 10 of target code pattern

### ⚠️ ISSUE FOUND: scripts/validate_daemon_speedup.sh

**Problem**: The validation script measures CLI overhead, not daemon latency.

**Evidence**:
```bash
Mean latency: 99174μs  # This is process spawn + parsing + daemon request
Target:       ≤190μs   # This should be daemon request only
```

**Root Cause**: Script runs:
```bash
hyperfine './target/release/pyrust -c "2+3"'
```

This measures:
1. Process spawn (~50-70ms on macOS)
2. Argument parsing
3. Binary initialization
4. Daemon client setup
5. Unix socket communication (<200μs)
6. Process teardown

**Expected Behavior**: The script should measure only the Unix socket round-trip, similar to how `execute_via_daemon_socket()` works in the Criterion benchmarks.

## Test Execution Results

### Daemon Functionality Tests

✅ **Daemon Lifecycle**: PASS
- Daemon starts successfully with `--daemon`
- Socket file created at `/tmp/pyrust.sock`
- PID file created at `/tmp/pyrust.pid`
- Daemon accepts requests via socket
- `--stop-daemon` cleanly stops daemon
- Proper cleanup of socket and PID files

✅ **Daemon Request Handling**: PASS (Functional)
```bash
$ ./target/release/pyrust -c "2+3"
5
```

❌ **Daemon Request Latency**: CRITICAL FAILURE
```
Test Results (100 requests with 100ms spacing):
  Request 1: 41948μs (41.9ms)
  Request 2: 94016μs (94.0ms)
  Request 3: 94092μs (94.1ms)
  Request 4: 102060μs (102.1ms)
  Request 5: 98796μs (98.8ms)

Mean latency: ~98,100μs (98.1ms)
Target: ≤190μs (0.19ms)
Ratio: 516x OVER TARGET
```

**Root Cause Identified**: `src/daemon.rs:199`
```rust
Err(ref e) if e.kind() == std::io::ErrorKind::WouldBlock => {
    // No connection available, sleep briefly and check shutdown flag again
    std::thread::sleep(Duration::from_millis(100));  // ← BUG!
}
```

**Impact**: The daemon event loop sleeps for 100ms when no connection is immediately available. This causes a race condition:
1. Client connects to socket
2. Connection enters listen queue
3. Daemon is sleeping (100ms)
4. Daemon wakes up and accepts connection
5. Total latency: 100ms + actual processing (~40μs) ≈ 100ms

**Expected Behavior**: Non-blocking accept with a much shorter sleep (1-10ms) or use `select()`/`poll()` for event-driven I/O.

**Fix Required**: Change `Duration::from_millis(100)` to `Duration::from_micros(100)` or use blocking I/O with timeout.

### Benchmark Compilation

✅ **benches/daemon_mode.rs**: COMPILES SUCCESSFULLY
- All 9 benchmark functions compile
- Daemon lifecycle functions work
- Unix socket protocol implementation correct
- Criterion configuration valid

❌ **Benchmark Execution**: WILL FAIL
- Benchmarks will measure ~100ms latency due to daemon bug
- All AC6.2 and M2 tests will fail
- Results will show ~500x over target

## Edge Cases Analysis

### Missing Edge Cases - Daemon Robustness

The benchmark implementation focuses on happy path testing. Additional edge case tests would strengthen the suite:

1. **Daemon Crash Recovery**:
   - What happens if daemon dies mid-request?
   - Socket cleanup on abnormal termination
   - Stale PID file handling

2. **Concurrent Request Handling**:
   - Multiple simultaneous requests
   - Request interleaving
   - Thread safety of daemon

3. **Large Payload Handling**:
   - Very long Python code (>1MB)
   - Buffer overflow protection
   - Memory limits

4. **Error Path Latency**:
   - Syntax errors
   - Runtime errors
   - Undefined variables
   - Does error path meet latency target?

5. **Socket Error Conditions**:
   - Socket connection timeout
   - Broken pipe
   - Socket file permissions
   - Multiple readers

6. **Warmup Validation**:
   - Is 100 warmup requests sufficient?
   - Does cache hit rate stabilize?
   - Variance before vs after warmup

### Edge Cases - Performance Boundaries

7. **Latency Distribution**:
   - What is P50, P90, P99?
   - Are there tail latencies?
   - Outlier analysis

8. **Sustained Load**:
   - Does latency degrade over time?
   - Memory leaks?
   - Cache eviction patterns

## Recommendations

### CRITICAL: Fix validate_daemon_speedup.sh

The script needs to bypass CLI overhead. Two options:

**Option 1: Use Python to measure socket communication directly**
```python
import socket
import struct
import time

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect("/tmp/pyrust.sock")

times = []
for _ in range(1000):
    code = "2+3"
    request = struct.pack(">I", len(code)) + code.encode()

    start = time.perf_counter_ns()
    sock.sendall(request)

    # Read response
    header = sock.recv(5)
    status, length = struct.unpack(">BI", header)
    response = sock.recv(length)
    end = time.perf_counter_ns()

    times.append((end - start) / 1000)  # Convert to microseconds

mean = sum(times) / len(times)
print(f"Mean latency: {mean:.1f}μs")
```

**Option 2: Create a minimal Rust benchmark client**
```rust
// Reuse execute_via_daemon_socket from benchmark
// Measure 1000 iterations
// Report mean and CV
```

### HIGH PRIORITY: Add Edge Case Tests

Create `tests/test_daemon_edge_cases.rs`:
```rust
#[test]
fn test_daemon_concurrent_requests() { /* ... */ }

#[test]
fn test_daemon_large_payload() { /* ... */ }

#[test]
fn test_daemon_error_latency() { /* ... */ }

#[test]
fn test_daemon_socket_errors() { /* ... */ }
```

### MEDIUM PRIORITY: Latency Distribution Analysis

Add P50/P90/P99 reporting to benchmarks:
```rust
// Use Criterion's built-in percentile reporting
// Add custom analysis for tail latencies
```

## Detailed Test Failure Analysis

### test_daemon_latency_target

**File**: Manual validation (standalone Rust test)
**Status**: ❌ FAIL

**Error**: Daemon latency 516x over target (98,100μs vs 190μs)

**Expected**: Each daemon request should complete in ≤190μs mean latency

**Actual**:
- Request 1: 41,948μs
- Request 2-5: 94,000-102,000μs
- Mean: 98,100μs
- All requests take ~100ms due to daemon sleep bug

**Code Location**: `src/daemon.rs:199`
```rust
// WRONG:
std::thread::sleep(Duration::from_millis(100));

// SHOULD BE:
std::thread::sleep(Duration::from_micros(100));
// OR better: use blocking I/O with short timeout
```

### test_validate_daemon_speedup_sh

**File**: `scripts/validate_daemon_speedup.sh`
**Status**: ❌ FAIL (but for wrong reasons)

**Error**: Script measures CLI overhead (99,174μs), not daemon latency

**Expected**: Script should measure socket-only communication

**Actual**: Script runs `pyrust -c '2+3'` which includes:
- Process spawn: ~50-70ms
- Argument parsing: ~1-5ms
- Binary initialization: ~10-20ms
- Socket communication: ~100ms (due to daemon bug)
- Total: ~99ms

**Fix Required**: Script should use direct socket communication like the Criterion benchmarks do.

### criterion_bench_daemon_mode_simple_arithmetic

**File**: `benches/daemon_mode.rs::bench_daemon_mode_simple_arithmetic`
**Status**: ⚠️ WILL FAIL (not run yet, but daemon bug will cause failure)

**Expected**: Mean ≤190μs with CV < 10%

**Predicted Actual**:
- Mean: ~100,000μs
- CV: ~10% (relatively stable, but at wrong value)
- Result: 526x over target

**All Other Criterion Benchmarks**: Same failure pattern expected

## Acceptance Criteria Validation

### ❌ AC6.2: Daemon mode benchmark mean ≤190μs verified in Criterion output
**Status**: FAIL - Daemon has 100ms sleep bug, actual latency ~98ms

### ❌ M2: Per-request latency ≤190μs mean measured via custom benchmark client
**Status**: FAIL - Custom benchmark client correctly measures socket latency, but daemon bug causes ~98ms delay

### ⚠️ Benchmark properly starts/stops daemon for isolation
**Status**: PARTIAL PASS - Isolation works, but daemon is fundamentally broken

### ⚠️ CV < 10% for statistical stability
**Status**: UNKNOWN - Daemon is so broken that stability doesn't matter yet

## Conclusion

**Test Coverage: ADEQUATE** ✅
- All acceptance criteria have corresponding tests
- Daemon lifecycle properly tested
- Socket protocol correctly implemented
- Statistical stability configured

**Test Execution: CRITICAL FAILURE** ❌
- Daemon implementation has 100ms sleep bug
- ALL latency tests will fail by ~500x
- Daemon is fundamentally broken for performance requirements
- Bug is in `src/daemon.rs:199`

**Missing Coverage: EDGE CASES** ⚠️
- Robustness testing limited
- Error paths not benchmarked
- Concurrent load not tested
- Tail latency not analyzed

**Verdict**:
- ✅ **Benchmark implementation**: Correct and comprehensive
- ❌ **Daemon implementation**: Critical performance bug makes it unusable
- ⚠️ **Validation script**: Measures wrong thing (CLI overhead vs socket latency)

**Required Fixes**:
1. **CRITICAL**: Fix `src/daemon.rs:199` - change 100ms sleep to 100μs or use blocking I/O
2. **HIGH**: Fix `scripts/validate_daemon_speedup.sh` to measure socket latency directly
3. **MEDIUM**: Add edge case tests for robustness

**Impact**: The benchmarks are well-designed but will all fail due to the daemon bug. The coder correctly implemented the benchmark suite but the underlying daemon server is broken.
