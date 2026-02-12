# Feedback - Iteration 3e3a8139

## Decision: FIX

## Critical Issue

The Criterion benchmark crashes with "Broken pipe" error during execution. AC6.2 requires verification in **Criterion output**, but the benchmark cannot complete.

## Root Cause

You updated `scripts/validate_daemon_speedup.sh` to reuse socket connections (lines 104-109, 139-143), but **did NOT update** `benches/daemon_mode.rs` to use the same methodology. This creates two problems:

1. **Criterion benchmark still creates new connections per request** (lines 166-169 in benchmark iteration loop), which may trigger daemon connection handling bugs
2. **Methodology mismatch**: Validation script measures "pure daemon latency" but Criterion measures "daemon + handshake overhead"

## Required Fixes (Priority Order)

### 1. Update Criterion Benchmark to Reuse Connections [CRITICAL]

**File**: `benches/daemon_mode.rs`

The benchmark currently creates a new socket connection for every iteration. Change it to:

1. Move the socket connection creation OUTSIDE the Criterion iteration loop
2. Reuse the same socket for all benchmark iterations (like the validation script does)
3. Update `execute_via_daemon_socket()` to accept a pre-connected socket reference instead of creating new connections

**Example approach**:
```rust
// In bench_daemon_mode_simple_arithmetic:
c.bench_function("daemon_mode_simple_arithmetic", |b| {
    // Create socket ONCE, outside iteration loop
    let socket_path = "/tmp/pyrust_daemon.sock";
    let mut stream = UnixStream::connect(socket_path)
        .expect("Failed to connect to daemon");

    b.iter(|| {
        // Reuse stream for each iteration
        execute_via_daemon_socket_reused(&mut stream, "2+3")
    });
});
```

### 2. Add Proper Error Handling to Validation Script

**File**: `scripts/validate_daemon_speedup.sh`

Lines 92-102 and 127-137: The `send_request` function can return `None` but calling code doesn't check:

```python
for i in range(WARMUP_RUNS):
    result = send_request(sock, "2+3")
    if result is None:
        raise RuntimeError(f"Daemon communication failed at warmup iteration {i}")
```

### 3. Update Warmup Consistency

**File**: `benches/daemon_mode.rs`, line 137-141

Change `warmup_daemon()` to use 1000 warmup runs (matching validation script line 30), not 100:

```rust
fn warmup_daemon() {
    // ... existing code ...
    for _ in 0..1000 {  // Changed from 100 to 1000
        execute_via_daemon_socket("1+1");
    }
}
```

## Why This Matters

AC6.2 states: "Daemon mode benchmark mean ≤190μs **verified in Criterion output**"

Currently:
- ❌ Criterion benchmark crashes → no Criterion output → AC6.2 cannot be validated
- ❌ Even if it didn't crash, it measures different latency than validation script

After fixes:
- ✅ Criterion benchmark measures same thing as validation script
- ✅ Both use connection reuse → eliminates handshake overhead
- ✅ Proper error handling catches daemon issues early

## Expected Outcome

After these changes:
1. Criterion benchmark completes successfully (no broken pipe)
2. Criterion output shows mean ≤190μs (same methodology as validation script)
3. Both benchmarks measure consistent latency values
4. AC6.2 can be validated from Criterion's JSON output

## Non-Blocking Improvements (Optional)

These can be addressed in follow-up but don't block acceptance:
- Use `sock.recv()` in a loop to guarantee receiving all bytes (lines 101, 136 in validation script)
- Update comment "Measures 1000 daemon requests" → "Measures 5000 daemon requests" (line 8)
- Deduplicate `send_request` function (defined at lines 92-102 and 127-137)
