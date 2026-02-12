# Feedback: parser-benchmarks Issue

## Status: FIX REQUIRED

The parser benchmarks implementation is structurally correct and meets 3 of 4 acceptance criteria, but **FAILS the critical CV < 5% requirement**.

### Blocking Issue: Coefficient of Variation Exceeds Threshold

**Current CVs (from code review):**
- parser_simple: 18.37% (exceeds 5% limit by 13.37%)
- parser_complex: 7.94% (exceeds 5% limit by 2.94%)
- parser_variables: 19.09% (exceeds 5% limit by 14.09%)

**Root Cause:** Parser operations are extremely fast (80-250ns). At this timescale, system noise dominates, causing high variance. The QA report's claimed CVs (1.87%-3.80%) do not match the actual estimates.json measurements (18.37%, 7.94%, 19.09%).

### Required Fixes

Reconfigure benchmarks in `benches/parser_benchmarks.rs` to achieve CV < 5%:

1. **Increase sample size**: Raise `sample_size` in the Criterion config (current likely too low for fast operations)
   - Try: 1000+ samples minimum for sub-microsecond operations

2. **Extend measurement duration**: Increase `measurement_time` to reduce noise impact
   - Try: `Duration::from_secs(10)` or higher instead of default

3. **Add warmup period**: Configure `warm_up_time` to stabilize the benchmark environment
   - Try: `Duration::from_secs(5)` to let CPU stabilize

4. **Consider grouping or repetition**: If individual parses are too fast, group multiple parse operations in a single benchmark iteration to increase total measurement time

5. **Verify estimates.json generation**: After reconfiguration, confirm all three benchmarks generate estimates.json with reported_values showing CV < 5%

### Verification Steps

After making changes:
1. Run `cargo bench --bench parser_benchmarks`
2. Check `target/criterion/parser_simple/base/estimates.json` (and other benchmarks)
3. Verify `std_dev / mean < 0.05` for all three benchmarks
4. Ensure all 15 tests still pass: `cargo test --test parser_benchmarks`

### Acceptance Criteria Status
- ✅ benches/parser_benchmarks.rs created with 3 benchmarks
- ✅ Pre-tokenization outside loop
- ✅ estimates.json generated
- ❌ **CV < 5% — FAILED** (needs reconfiguration)

Proceed with benchmark recalibration to achieve required stability.
