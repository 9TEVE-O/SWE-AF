# Feedback: lexer-benchmarks

## Status: FIX Required

### Summary
The lexer benchmarks implementation is structurally correct and meets AC1-3, but **AC4 (CV < 5%) is failing**. One or more benchmarks exceed the variance threshold due to measurement noise at nano-second timescales.

### Critical Issue
**AC4 (Coefficient of Variation < 5%): FAILED**

Reporting discrepancies between QA and review, but consensus: `lexer_variables` benchmark has CV > 5% (18-20% range).

- ❌ lexer_variables: ~18-20% CV (FAILS)
- ⚠️ lexer_simple: 3-46% CV (reporting variance, but appears to pass based on code review)
- ✅ lexer_complex: 2-3% CV (PASSES)

### Root Cause
Operations are executing in 37-160 nanoseconds — below the precision threshold where relative measurement noise becomes significant. The benchmark harness is stable, but the timed operations finish too quickly for consistent sampling.

### Action Required
**Batch multiple lexer operations per iteration to increase measurement duration.** This reduces relative noise without changing the benchmark's validity.

**Specific fix for `benches/lexer_benchmarks.rs`:**

1. **lexer_variables benchmark** (priority fix):
   - Instead of `lexer.lex(var_input)` once per iteration, wrap in a loop
   - Example: Run lexing 100x per iteration using `(0..100).fold(vec![], |mut acc, _| { acc.push(lexer.lex(var_input.clone())); acc })`
   - Adjust iteration count to keep total benchmark duration ~1-10s (Criterion default)

2. **lexer_simple benchmark** (if still failing after lexer_variables fix):
   - Apply same batching strategy with appropriate iteration multiplier

3. **Validation**:
   - Re-run benchmarks: `cargo bench --bench lexer_benchmarks`
   - Verify CV < 5% in all three: `target/criterion/lexer_*/base/estimates.json`
   - All 18 edge case tests must still pass

### Files to Modify
- `benches/lexer_benchmarks.rs` — Add batching loops to lexer_variables and lexer_simple benchmarks

### Testing
- Existing test suite (tests/test_lexer_benchmarks.rs) must remain passing (17/18 currently pass, 1 fails due to CV)
- Re-run benchmark to generate new estimates.json with reduced variance

---
**Do not modify acceptance criteria or benchmark requirements.** The solution is to increase measurement granularity, not loosen constraints.
