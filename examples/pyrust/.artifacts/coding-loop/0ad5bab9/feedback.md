# Feedback: parser-benchmarks

**Status**: FIX REQUIRED

## Summary
The benchmark structure is correct (AC1-AC3 PASS), but all benchmarks fail the CV < 5% requirement (AC4 FAIL). Parser operations are too fast (~80-250ns) for Criterion's default configuration to achieve statistical stability. This is iteration 2 with the same CV threshold failure.

## Blocking Issues

### AC4 Failure: Coefficient of Variation Exceeds Threshold
**Files affected**: `benches/parser_benchmarks.rs`

**Current status**:
- parser_simple: 45.38% CV (limit: <5%) — EXCEEDS by 40.38%
- parser_complex: 2.98% CV (limit: <5%) — PASSES
- parser_variables: 6.07% CV (limit: <5%) — EXCEEDS by 1.07%

**Root cause**: The 12,000-iteration batching approach fails for sub-100ns operations because system noise still dominates. Criterion's wall-clock time measurement is insufficient for this speed range.

**Action required**: Apply aggressive Criterion configuration changes to reduce variance:

1. **Increase sample collection**: In `benches/parser_benchmarks.rs`, modify the BenchmarkId for each group to add:
   ```rust
   .sample_size(1000)        // Increase from default 100
   .measurement_time(Duration::from_secs(30))  // Extend measurement window
   .warm_up_time(Duration::from_secs(5))       // Add proper warm-up
   ```

2. **Verify per-benchmark**: After running `cargo bench --bench parser_benchmarks`, check that `target/criterion/*/base/estimates.json` shows `coefficient_of_variation` < 0.05 for all three benchmarks.

3. **If still failing**: Consider CPU cycle counter instrumentation (e.g., `rdtsc` or `perf`-based measurement) instead of wall-clock time, as these sub-100ns operations may be fundamentally incompatible with system timer granularity.

## Acceptance Criteria Status
- ✅ AC1: benches/parser_benchmarks.rs with three benchmarks exists
- ✅ AC2: Input pre-tokenized outside loop
- ✅ AC3: estimates.json generated for each benchmark
- ❌ AC4: CV < 5% for all benchmarks (2/3 fail)

## Next Steps
1. Update `benches/parser_benchmarks.rs` with the Criterion configuration above
2. Run `cargo bench --bench parser_benchmarks` and verify all three benchmarks show CV < 5% in estimates.json
3. Confirm no test failures and all AC criteria met
