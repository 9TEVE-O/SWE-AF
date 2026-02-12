# Feedback: Iteration 7bb1ce39

## Decision: FIX

## Summary
Implementation approach is correct - Criterion configuration applied to all benchmark files and validation script created. However, **31 out of 56 benchmarks (55.4%) still exceed CV=10% threshold**. AC4.4 and M5 NOT MET. Critical failure: `cold_start_simple` has CV=112.57% (11x over threshold).

Root cause: Very fast operations (<1μs) are dominated by system noise despite current config (sample_size=1000, measurement_time=10s). Need more aggressive configuration for fast benchmarks.

## Required Fixes (Priority Order)

### 1. **CRITICAL: Fix Fast Benchmark Configuration**

**Problem:** 31 benchmarks exceed CV=10%, especially fast operations like `cold_start_simple` (CV=112.57%).

**Action:**
- For benchmarks with inner loops (lexer: 1000 iterations, parser: 12000 iterations), use `iter_batched` instead of manual loops:
  ```rust
  // In benches/lexer_benchmarks.rs
  c.bench_function("lexer_simple", |b| {
      b.iter_batched(
          || input.clone(),
          |input| black_box(tokenize(&input)),
          criterion::BatchSize::SmallInput,
      )
  });
  ```
- Remove manual inner loops (the 1000/12000 iteration loops) - Criterion handles iteration internally
- For extremely fast operations (<100ns), increase `sample_size` to 5000 and `measurement_time` to 20s in their specific benchmark groups

**Files to modify:**
- `benches/lexer_benchmarks.rs` - remove 1000-iteration loop, use iter_batched
- `benches/parser_benchmarks.rs` - remove 12000-iteration loop, use iter_batched
- `benches/vm_benchmarks.rs` - increase config for cold_start benchmarks specifically

### 2. **REQUIRED: Document AC4.2 Test Regression Check**

**Problem:** Reviewer noted no evidence for "All 664 currently passing tests still pass" claim.

**Action:**
- Run `cargo test --release` and capture output showing all tests pass
- Add output to `.artifacts/coding-loop/<iteration_id>/test-output.txt`
- Update validation script or create companion script that verifies test count

### 3. **RECOMMENDED: Add Dependency Checks to Validation Script**

**Action in `scripts/validate_benchmark_stability.sh`:**
```bash
# Add at top of script after shebang
command -v jq >/dev/null 2>&1 || { echo "Error: jq required. Install with: brew install jq"; exit 1; }
command -v bc >/dev/null 2>&1 || { echo "Error: bc required (should be pre-installed)"; exit 1; }
```

## Verification Steps
After fixes:
1. Run `cargo bench` to generate fresh Criterion JSON
2. Run `scripts/validate_benchmark_stability.sh` - should show 0 benchmarks exceeding 10% CV
3. Run `cargo test --release` - verify 377 tests pass (or current passing count)
4. All 3 acceptance criteria (AC4.4, AC4.2, M5) must pass

## Notes
- 25 benchmarks already achieve CV < 10% - keep their configuration
- The `iter_batched` approach is the Criterion-recommended pattern for benchmarks with setup/teardown
- Inner loops change what's being measured (N operations vs 1 operation) - removing them gives true per-operation timing
