# Test Failures — Iteration 0ad5bab9

## Summary
2 out of 15 tests failed. The parser_benchmarks implementation successfully creates all required benchmarks with pre-tokenization, but **FAILS** to meet the CV < 5% threshold for 2 out of 3 benchmarks.

## Acceptance Criteria Coverage

### AC1: Create benches/parser_benchmarks.rs with parser_simple, parser_complex, parser_variables benchmarks
✅ **PASS** - All three benchmarks exist and are properly configured in criterion_group

### AC2: Pre-tokenize input outside benchmark loop to isolate parser performance
✅ **PASS** - Code inspection confirms `lexer::lex()` is called outside `bench_function`, tokens are cloned inside the loop

### AC3: Criterion generates estimates.json for each benchmark
✅ **PASS** - All three estimates.json files exist at:
- target/criterion/parser_simple/base/estimates.json
- target/criterion/parser_complex/base/estimates.json
- target/criterion/parser_variables/base/estimates.json

### AC4: CV < 5% for all benchmarks
❌ **FAIL** - Only 1 out of 3 benchmarks meets the threshold

## Test Failures

### test_parser_simple_cv_below_5_percent
- **File**: tests/test_parser_benchmarks.rs:107-140
- **Error**: `AC4 FAILED: parser_simple CV 45.38% exceeds 5% threshold`
- **Expected**: CV < 5% (coefficient of variation)
- **Actual**: CV = 45.38%
- **Details**:
  - Mean: 1,256,842.13 ns (~1.26 ms for 12,000 iterations = 104.7 ns per parse)
  - Std Dev: 570,353.57 ns
  - The extremely high CV (45%) indicates severe measurement instability
  - 95 outliers detected (12.67% of samples), with 89 severe outliers
  - The 12,000 iteration batching is NOT sufficient to dominate noise for this operation

### test_parser_variables_cv_below_5_percent
- **File**: tests/test_parser_benchmarks.rs:179-212
- **Error**: `AC4 FAILED: parser_variables CV 6.07% exceeds 5% threshold`
- **Expected**: CV < 5% (coefficient of variation)
- **Actual**: CV = 6.07%
- **Details**:
  - Mean: 784,669.31 ns (~0.78 ms for 12,000 iterations = 65.4 ns per parse)
  - Std Dev: 47,615.83 ns
  - Narrowly exceeds threshold by 1.07 percentage points
  - 19 outliers detected (2.53% of samples)
  - Very close to passing, but still fails acceptance criteria

### test_parser_complex_cv_below_5_percent
✅ **PASS** - CV = 2.98%
- Mean: 2,900,387.06 ns (~2.9 ms for 12,000 iterations = 241.7 ns per parse)
- Std Dev: 86,404.12 ns
- 3 outliers (0.40% of samples)
- **This benchmark demonstrates the configuration CAN work for longer operations**

## Root Cause Analysis

The fundamental issue is that **very fast parser operations (65-105ns per parse) are too quick to measure reliably** even with aggressive batching:

1. **parser_simple** (104.7 ns/parse): 45.38% CV - completely unstable
   - At ~100ns per parse, even 12,000 iterations = only 1.26ms total
   - System noise (context switches, CPU frequency scaling) dominates
   - The coder's claim that "12000 iterations dominate system noise for very fast operations (80-250ns)" is **empirically false** for the lower end of that range

2. **parser_variables** (65.4 ns/parse): 6.07% CV - barely unstable
   - Even faster operation (~65ns) but somehow more stable than parser_simple
   - Still exceeds threshold, proving the strategy is insufficient

3. **parser_complex** (241.7 ns/parse): 2.98% CV - **STABLE**
   - At ~240ns per parse, the operation is long enough to measure reliably
   - This proves the Criterion configuration works for operations ≥200ns

## Missing Test Coverage

The existing test suite is **comprehensive** and adequately covers:
- ✅ File existence validation (AC1)
- ✅ Code pattern inspection for pre-tokenization (AC2)
- ✅ JSON file generation and schema validation (AC3)
- ✅ CV threshold validation (AC4)
- ✅ Edge cases (empty input, deeply nested expressions, all operators, multiple statements, invalid syntax)
- ✅ Criterion configuration verification

**No additional tests are needed.** The existing tests correctly identify the AC4 failure.

## Recommendations for Coder

To fix the CV < 5% requirement for all benchmarks, the coder must either:

1. **Increase iteration count dramatically** for fast operations:
   - parser_simple/variables need 50,000-100,000 iterations per sample
   - This makes each sample 5-10ms, reducing relative noise

2. **Add workload** to make operations slower:
   - Parse more complex expressions to push timing above 200ns
   - NOT recommended as it changes what's being measured

3. **Accept that sub-100ns operations cannot be benchmarked reliably** at CV<5%:
   - Relax AC4 to "CV < 5% OR operation time < 100ns"
   - Document the measurement limitations

4. **Use CPU cycle counters** instead of wall-clock time:
   - Requires `criterion-perf-events` crate
   - More stable for very fast operations
   - Platform-specific (Linux only)

## Test Execution Details

```bash
# Benchmarks executed successfully:
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 cargo bench --bench parser_benchmarks

# Results:
parser_simple:     1.26 ms ± 570 µs (CV: 45.38%) ❌
parser_complex:    2.90 ms ± 86 µs  (CV: 2.98%)  ✅
parser_variables:  0.78 ms ± 48 µs  (CV: 6.07%)  ❌

# Tests run:
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 cargo test --test test_parser_benchmarks

# Results: 13 passed, 2 failed
```

## Verdict

**The implementation FAILS acceptance criteria** because AC4 requires ALL benchmarks to have CV < 5%, but only 1 out of 3 meets this threshold. The coder's iteration 2 configuration changes were insufficient to stabilize measurements for sub-100ns operations.
