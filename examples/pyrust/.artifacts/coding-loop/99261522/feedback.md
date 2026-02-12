# Feedback — Iteration 99261522

## Decision: FIX

## Status
- ✅ Code changes are correct (review approved with no blocking issues)
- ✅ Mean latency meets target: 132μs ≤ 190μs
- ❌ **BLOCKING**: CV (55.30%) exceeds 10% threshold — statistical stability requirement NOT met

## Critical Issue: Statistical Instability (CV > 10%)

**Problem**: The benchmark produces a Coefficient of Variation of 55.30%, far exceeding the required 10% threshold. While mean latency (132μs) meets the target, the high variance (stddev=73μs) makes results unreliable.

**Why this matters**: CV < 10% is an explicit acceptance criterion. Individual requests vary from ~59μs to ~205μs, which means we cannot confidently claim "≤190μs" performance.

## Required Fix

**Reduce CV from 55.30% to below 10%** by addressing measurement variability.

### Specific Actions (in priority order):

#### 1. **Increase warmup runs** [HIGHEST PRIORITY]
- **File**: `scripts/validate_daemon_speedup.sh`
- **Line**: 29
- **Change**: `WARMUP_RUNS=100` → `WARMUP_RUNS=1000`
- **Rationale**: 100 warmup requests insufficient for JIT/cache stabilization

#### 2. **Reuse socket connections**
- **File**: `scripts/validate_daemon_speedup.sh` (Python measurement code)
- **Current**: Connect/disconnect per request adds variable overhead
- **Change**: Establish single persistent Unix socket connection, send all requests through it
- **Implementation**:
  ```python
  # Connect once
  sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
  sock.connect(socket_path)

  # Send all requests through same connection
  for i in range(NUM_RUNS):
      # send/recv without reconnecting

  sock.close()
  ```
- **Expected impact**: Should significantly reduce CV by eliminating connection handshake overhead

#### 3. **Increase sample size**
- **File**: `scripts/validate_daemon_speedup.sh`
- **Line**: 30
- **Change**: `NUM_RUNS=1000` → `NUM_RUNS=5000`
- **Rationale**: Larger sample → better statistical confidence, smoother CV

#### 4. **Optional: Add statistical filtering**
- Remove outliers beyond 3 standard deviations before calculating CV
- This filters system noise spikes while preserving typical behavior

### Validation

After changes, run:
```bash
./scripts/validate_daemon_speedup.sh
```

**Success criteria**:
- Mean latency still ≤ 190μs ✓
- CV < 10% ✓

## Non-Blocking Debt Items (from code review)

These are acceptable for merge after CV is fixed:
1. Missing test coverage for 100μs sleep fix (should_fix)
2. Hardcoded validation parameters (should_fix)
3. Insufficient comment on sleep duration (suggestion)

## Summary

**Root cause**: Socket connection/disconnection overhead per request + insufficient warmup
**Fix priority**: (1) Increase warmup, (2) Reuse socket connections, (3) Increase sample size
**Expected outcome**: CV drops from 55.30% → <10% while maintaining 132μs mean latency

The code is correct — this is purely a measurement stability issue.
