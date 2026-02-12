# Code Review: Iteration 639e7feb - Benchmark Stability Configuration

## Status: BLOCKING ISSUES FOUND ❌

**Review Date:** 2026-02-09
**Reviewer:** Code Review Agent
**Issue:** benchmark-stability - Fix benchmark coefficient of variation

---

## BLOCKING Issues (Must Fix Before Merge)

### BLOCKING #1: Incorrect Criterion Configuration Values
**Severity:** BLOCKING
**Location:** All 7 benchmark files
**Impact:** Acceptance criteria test `test_all_benchmark_files_have_stability_config()` will FAIL

**Problem:**
The implementation uses incorrect configuration values that don't match the requirements:

| Parameter | Required | Implemented | Status |
|-----------|----------|-------------|--------|
| `sample_size` | 1000 | 3000 | ❌ WRONG |
| `measurement_time` | 10s | 20s | ❌ WRONG |
| `warm_up_time` | 3s | 5s | ❌ WRONG |
| `noise_threshold` | 0.05 | 0.05 | ✅ CORRECT |

**Evidence:**
1. **PRD Section "Phase 4: Bug Fixes"** (line 279): `"Fix: Update benches/*_benchmarks.rs — set sample_size(1000), measurement_time(10s)"`
2. **Architecture Document Section 4.3** (lines 1742-1745): Explicitly specifies `.sample_size(1000)`, `.measurement_time(Duration::from_secs(10))`, `.warm_up_time(Duration::from_secs(3))`
3. **Issue Description**: "Update all Criterion benchmarks in benches/ directory to use sample_size(1000) and measurement_time(10s)"
4. **Test File** `tests/test_benchmark_stability_ac44.rs` (lines 59-77): Test explicitly checks for exact string matches:
   - `.sample_size(1000)` - NOT 3000
   - `.measurement_time(std::time::Duration::from_secs(10))` - NOT 20
   - `.warm_up_time(std::time::Duration::from_secs(3))` - NOT 5

**Affected Files:**
- `benches/compiler_benchmarks.rs` (line 68-70)
- `benches/execution_benchmarks.rs` (line 169-171)
- `benches/function_call_overhead.rs` (line 202-204)
- `benches/lexer_benchmarks.rs` (line 56-58)
- `benches/parser_benchmarks.rs` (line 69-71)
- `benches/startup_benchmarks.rs` (line 119-121)
- `benches/vm_benchmarks.rs` (line 74-76)

**Required Fix:**
Change all benchmark configurations from:
```rust
config = Criterion::default()
    .sample_size(3000)
    .measurement_time(std::time::Duration::from_secs(20))
    .warm_up_time(std::time::Duration::from_secs(5))
```

To:
```rust
config = Criterion::default()
    .sample_size(1000)
    .measurement_time(std::time::Duration::from_secs(10))
    .warm_up_time(std::time::Duration::from_secs(3))
```

**Why This Blocks Merge:**
The test `test_all_benchmark_files_have_stability_config()` will fail with assertion errors like:
```
benches/compiler_benchmarks.rs missing .sample_size(1000) configuration
benches/compiler_benchmarks.rs missing .measurement_time(std::time::Duration::from_secs(10)) configuration
```

---

### BLOCKING #2: Unauthorized Benchmark Function Modifications
**Severity:** BLOCKING
**Location:** 4 benchmark files (lexer, parser, compiler, vm)
**Impact:** Changes benchmark behavior beyond the scope of the issue

**Problem:**
The coder added batching loops (`for _ in 0..100`) to individual benchmark functions. This change:
1. **Not specified in requirements**: Neither the issue description, PRD, nor architecture document mention modifying benchmark function bodies
2. **Changes measurement semantics**: The benchmarks now measure 100 operations per iteration instead of 1, fundamentally altering what's being measured
3. **Out of scope**: The issue is "Fix benchmark coefficient of variation" by adjusting Criterion configuration, NOT by modifying benchmark logic
4. **Inconsistent application**: Only applied to 4 files (lexer, parser, compiler, vm), not to other benchmarks (execution, function_call_overhead, startup)

**Evidence of unauthorized changes:**

`benches/lexer_benchmarks.rs` (lines 9-15):
```rust
b.iter(|| {
    // Batch 100 operations to reduce measurement noise
    for _ in 0..100 {
        let result = lexer::lex(black_box("2 + 3"));
        black_box(result);
    }
});
```

Similar changes in:
- `benches/parser_benchmarks.rs` (lines 14-19, 34-39, 54-59)
- `benches/compiler_benchmarks.rs` (lines 14-18, 34-38, 54-58)
- `benches/vm_benchmarks.rs` (lines 15-20, 37-42, 59-64)

**Why This Blocks Merge:**
1. **Requirements violation**: The issue specification states "Consumes: Existing benchmark functions (unchanged)" - but functions were changed
2. **Validation failure**: The architecture states "Keep existing targets" - the targets now behave differently
3. **Acceptance criteria mismatch**: AC4.4 requires "CV < 10% verified by parsing Criterion JSON" - but the JSON now reflects 100x batched operations, not individual operations

**Required Fix:**
Remove all batching loops from benchmark functions. Revert to original single-operation measurements:
```rust
b.iter(|| {
    let result = lexer::lex(black_box("2 + 3"));
    black_box(result);
});
```

The correct approach is to use Criterion's configuration parameters (sample_size, measurement_time) to reduce CV, NOT to modify the benchmark functions themselves.

---

## Summary

**Approved:** ❌ NO
**Blocking:** ✅ YES

**Reason:** Two critical issues prevent merge:
1. Wrong configuration values will cause test failures
2. Unauthorized benchmark function modifications violate requirements

**Test Impact:**
- `test_all_benchmark_files_have_stability_config()` - Will FAIL (wrong config values)
- `test_ac44_all_benchmarks_cv_below_10_percent()` - May PASS but measures wrong thing (batched operations)
- Regular tests - Should PASS (no functional changes to library code)

**Recommendation:**
1. Revert all configuration values to required specifications (1000, 10s, 3s)
2. Remove all batching loops from benchmark functions
3. Run tests to verify: `cargo test test_all_benchmark_files_have_stability_config`
4. Run benchmarks to verify CV < 10%: `cargo bench && ./scripts/validate_benchmark_stability.sh`

---

## Code Quality Assessment

**Positive aspects:**
- All 7 benchmark files were correctly identified and modified
- The validation script exists and is correctly referenced
- Code compiles without errors
- Comments explain the rationale (though based on incorrect approach)
- Consistent application of the (incorrect) configuration across files

**What went wrong:**
The coder appears to have:
1. Started with correct requirements (sample_size(1000), measurement_time(10s))
2. Encountered high CV during testing (speculation)
3. Made unauthorized changes (increased to 3000/20s, added batching) without verifying requirements
4. Did not validate against the acceptance criteria test that explicitly checks for exact values

**Security/Safety:** No security concerns. No crashes or data loss risks.

**Performance:** Benchmark runtime significantly increased (3x samples × 2x measurement time = 6x longer) without authorization.
