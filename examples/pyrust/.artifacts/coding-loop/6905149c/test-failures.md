# Test Failures — Iteration 6905149c

## Summary
The lexer benchmarks were created successfully and execute correctly, but **2 out of 3 benchmarks fail the CV < 5% requirement** (AC4). This is a performance stability issue, not a code error.

**QA Agent Added**:
- Created comprehensive test suite: `tests/test_lexer_benchmarks.rs` with 18 tests
- 17 out of 18 tests PASS
- 1 test FAILS: `test_lexer_benchmarks_cv_under_5_percent` (AC4 requirement)
- Added 10 edge case tests covering: empty input, whitespace, very long expressions, special characters, Unicode, large integers, isolation testing, and black_box usage verification

## Acceptance Criteria Validation

### AC1: Create benches/lexer_benchmarks.rs with lexer_simple, lexer_complex, lexer_variables benchmarks
**Status**: ✅ PASSED
- File created: `benches/lexer_benchmarks.rs`
- All 3 benchmarks present: lexer_simple, lexer_complex, lexer_variables

### AC2: Each benchmark uses black_box() and samples ≥1000 iterations
**Status**: ✅ PASSED
- All benchmarks use `black_box()` on both input and output
- Configuration: `sample_size(1000)` ✅
- Configuration: `measurement_time(10s)` ✅

### AC3: Criterion generates estimates.json for each benchmark
**Status**: ✅ PASSED
- `target/criterion/lexer_simple/base/estimates.json` exists (980 bytes)
- `target/criterion/lexer_complex/base/estimates.json` exists (987 bytes)
- `target/criterion/lexer_variables/base/estimates.json` exists (981 bytes)

### AC4: CV (coefficient of variation) < 5% for all benchmarks
**Status**: ❌ FAILED (2 out of 3 benchmarks exceed 5%)

## Benchmark Results

### lexer_simple
- **Mean**: 37.06 ns
- **Std Dev**: 17.07 ns
- **CV**: 46.06% ❌ EXCEEDS 5% THRESHOLD
- **Expected**: CV < 5%
- **Actual**: CV = 46.06%
- **Issue**: Extreme variance - the standard deviation (17.07ns) is nearly half the mean (37.06ns). This suggests the benchmark is experiencing significant measurement noise, likely because the operation is too fast (sub-40ns) to measure accurately.

### lexer_complex
- **Mean**: 140.75 ns
- **Std Dev**: 3.90 ns
- **CV**: 2.77% ✅ PASSED
- **Expected**: CV < 5%
- **Actual**: CV = 2.77%
- **Status**: This benchmark meets the requirement

### lexer_variables
- **Mean**: 159.47 ns
- **Std Dev**: 32.51 ns
- **CV**: 20.38% ❌ EXCEEDS 5% THRESHOLD
- **Expected**: CV < 5%
- **Actual**: CV = 20.38%
- **Issue**: High variance - the standard deviation (32.51ns) is about 20% of the mean. This is better than lexer_simple but still exceeds the 5% threshold.

## Root Cause Analysis

The high CV values are likely caused by:

1. **Measurement noise at nano-second scale**: The lexer operations are extremely fast (37-160ns), making them difficult to measure accurately. At this scale, CPU frequency scaling, cache effects, and OS scheduling can introduce variance.

2. **System interference**: Background processes, thermal throttling, and other system-level effects can impact measurements.

3. **Insufficient warmup or outliers**: The benchmark shows significant outliers:
   - lexer_simple: 94 outliers (9.40% of samples)
   - lexer_variables: 42 outliers (4.20% of samples)

## Recommended Fixes

To achieve CV < 5%, consider:

1. **Increase work per iteration**: Batch multiple lex operations in a loop to increase the time-per-iteration and reduce relative measurement noise
2. **Increase measurement time**: Extend beyond 10s to capture more stable statistics
3. **Run on isolated core**: Use CPU affinity to pin benchmark to a specific core
4. **Disable CPU frequency scaling**: Lock CPU frequency during benchmarking
5. **Filter outliers**: Configure Criterion to be more aggressive with outlier removal

## Code Coverage Assessment

**QA Agent Created Test Suite**: `tests/test_lexer_benchmarks.rs`

This comprehensive test file validates all acceptance criteria and adds edge case coverage:

### Tests Created (18 total)

#### AC Validation Tests (7 tests):
1. ✅ `test_lexer_benchmarks_file_exists` - AC1: File exists
2. ✅ `test_lexer_benchmarks_has_three_benchmarks` - AC1: All 3 benchmarks present
3. ✅ `test_lexer_benchmarks_uses_black_box` - AC2: black_box usage
4. ✅ `test_lexer_benchmarks_sample_size_1000` - AC2: sample_size ≥ 1000
5. ✅ `test_lexer_simple_estimates_json_exists` - AC3: JSON output for lexer_simple
6. ✅ `test_lexer_complex_estimates_json_exists` - AC3: JSON output for lexer_complex
7. ✅ `test_lexer_variables_estimates_json_exists` - AC3: JSON output for lexer_variables
8. ❌ `test_lexer_benchmarks_cv_under_5_percent` - AC4: CV < 5% (FAILS)

#### Edge Case Tests (10 tests):
1. ✅ `test_edge_case_lexer_simple_isolation` - Verifies no parser/compiler calls
2. ✅ `test_edge_case_lexer_complex_has_operators` - Verifies multiple operators
3. ✅ `test_edge_case_lexer_variables_has_assignments` - Verifies assignment operators
4. ✅ `test_edge_case_black_box_usage` - Verifies black_box on input AND output
5. ✅ `test_edge_case_empty_input` - Handles empty string
6. ✅ `test_edge_case_whitespace_only` - Handles whitespace-only input
7. ✅ `test_edge_case_very_long_expression` - Handles 100+ token expressions
8. ✅ `test_edge_case_special_characters` - Handles invalid characters gracefully
9. ✅ `test_edge_case_unicode_identifiers` - Handles Unicode without panic
10. ✅ `test_edge_case_maximum_integer` - Handles very large integers

### Test Execution Results

```
running 18 tests
test test_edge_case_empty_input ... ok
test test_edge_case_lexer_complex_has_operators ... ok
test test_edge_case_lexer_variables_has_assignments ... ok
test test_edge_case_maximum_integer ... ok
test test_edge_case_lexer_simple_isolation ... ok
test test_edge_case_black_box_usage ... ok
test test_edge_case_special_characters ... ok
test test_edge_case_unicode_identifiers ... ok
test test_edge_case_whitespace_only ... ok
test test_lexer_benchmarks_file_exists ... ok
test test_edge_case_very_long_expression ... ok
test test_lexer_benchmarks_sample_size_1000 ... ok
test test_lexer_benchmarks_uses_black_box ... ok
test test_lexer_benchmarks_has_three_benchmarks ... ok
test test_lexer_complex_estimates_json_exists ... ok
test test_lexer_simple_estimates_json_exists ... ok
test test_lexer_variables_estimates_json_exists ... ok
test test_lexer_benchmarks_cv_under_5_percent ... FAILED

test result: FAILED. 17 passed; 1 failed; 0 ignored; 0 measured
```

**Coverage Summary**:
- AC1, AC2, AC3: **FULLY COVERED** by tests and **PASSING**
- AC4 (CV < 5%): **COVERED** by test but **FAILING** due to performance variance
- Edge cases: **COMPREHENSIVE COVERAGE** (10 additional tests)
- Existing lexer unit tests: 41 tests in `src/lexer.rs` (all passing)

The issue is **performance stability**, not missing test coverage. All code paths are tested.
