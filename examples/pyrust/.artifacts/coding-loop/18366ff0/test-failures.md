# Test Failures — Iteration 18366ff0

## Summary
The compiler benchmarks implementation **FAILS** acceptance criteria validation. While the benchmarks execute successfully and produce correct output files, **AC4 (CV < 5%) is violated** for 2 out of 3 benchmarks.

## Status by Acceptance Criteria

### ✅ AC1: Create benches/compiler_benchmarks.rs with compiler_simple, compiler_complex, compiler_variables benchmarks
**Status**: PASS

All three benchmark functions exist in `benches/compiler_benchmarks.rs`:
- `compiler_simple`: Simple arithmetic (2 + 3)
- `compiler_complex`: Complex nested arithmetic ((10 + 20) * 3 / 2)
- `compiler_variables`: Variable assignment and usage (x = 10; y = 20; x + y)

### ✅ AC2: Pre-parse input outside benchmark loop to isolate compiler performance
**Status**: PASS

All benchmarks correctly pre-parse the AST outside the benchmark loop:
- AST is constructed before `c.bench_function()`
- Only `compiler::compile(black_box(&ast))` is inside the `b.iter()` loop
- This correctly isolates compiler performance from lexer/parser performance

### ✅ AC3: Criterion generates estimates.json for each benchmark
**Status**: PASS

All three benchmarks generate valid estimates.json files:
- `target/criterion/compiler_simple/base/estimates.json` ✓
- `target/criterion/compiler_complex/base/estimates.json` ✓
- `target/criterion/compiler_variables/base/estimates.json` ✓

### ❌ AC4: CV < 5% for all benchmarks
**Status**: FAIL - **CRITICAL ISSUE**

Coefficient of Variation (CV) results:

| Benchmark | Mean (ns) | Std Dev (ns) | CV | Status |
|-----------|-----------|--------------|-----|--------|
| compiler_simple | 127.69 | 3.46 | **2.71%** | ✅ PASS |
| compiler_complex | 245.44 | 330.17 | **134.53%** | ❌ FAIL |
| compiler_variables | 345.62 | 48.69 | **14.09%** | ❌ FAIL |

**Required**: CV < 5% for all benchmarks
**Actual**: Only 1 out of 3 benchmarks meets the requirement

---

## Test Failure Details

### test_compiler_benchmarks_cv_under_5_percent
- **File**: `tests/test_compiler_benchmarks.rs`
- **Error**: AC4 FAILED: One or more benchmarks have CV >= 5%
- **Expected**: All benchmarks should have CV < 5%
- **Actual**:
  - compiler_simple: CV = 2.71% ✓
  - compiler_complex: CV = 134.53% ✗ (26.9x over threshold)
  - compiler_variables: CV = 14.09% ✗ (2.8x over threshold)

**Root Cause Analysis**:

1. **compiler_complex** has extremely high variance (CV = 134.53%)
   - Standard deviation (330.17ns) is larger than the mean (245.44ns)
   - This indicates severe measurement instability
   - Benchmark output shows 13.9% outliers (139 out of 1000 samples)
   - Likely causes:
     - System interference (background processes, thermal throttling)
     - Memory allocation variance
     - Cache effects from nested AST structure

2. **compiler_variables** has moderately high variance (CV = 14.09%)
   - Standard deviation is 48.69ns on mean of 345.62ns
   - Benchmark output shows 5.5% outliers (55 out of 1000 samples)
   - Likely causes:
     - String allocation variance for variable names
     - HashMap operations for variable storage
     - More complex AST with multiple statements

**Impact**: This is a **blocking failure**. The benchmarks do not provide reliable, reproducible measurements as required by AC4.

---

## Edge Case Test Results

All edge case tests **PASSED**:

### ✅ test_edge_case_compiler_simple_isolation
Verified that compiler_simple only compiles a simple binary operation, ensuring true compiler isolation.

### ✅ test_edge_case_compiler_complex_nested_operations
Verified that compiler_complex has nested operations (depth=2) to test compiler complexity.

### ✅ test_edge_case_compiler_variables_has_assignments
Verified that compiler_variables benchmarks variable compilation with 2 assignments.

### ✅ test_edge_case_no_lexer_or_parser_in_loop
Verified that no lexer/parser calls are included in the benchmark measurement loops.

### ✅ test_edge_case_black_box_usage
Verified that black_box is correctly used in all benchmarks to prevent compiler optimization.

---

## Recommendations

### Critical (Must Fix)

1. **Increase sample size and measurement time**
   - Current: 1000 samples, 10s measurement time
   - Recommendation: Try 5000 samples, 30s measurement time
   - This may reduce variance by averaging over more measurements

2. **Isolate system effects**
   - Disable CPU frequency scaling (performance governor)
   - Close background applications
   - Pin benchmark process to specific CPU cores
   - Run benchmarks multiple times and take the run with lowest CV

3. **Investigate allocation variance**
   - Profile memory allocations during benchmarks
   - Consider pre-allocating data structures
   - Use dhat or similar tools to identify allocation hotspots

4. **Simplify compiler_complex**
   - Current nesting depth may cause cache/memory variance
   - Try reducing to 2-level nesting instead of 3-level
   - Or use a different complex expression with less nesting

### Alternative Approach

If variance cannot be reduced below 5%, consider:
- Relaxing AC4 threshold to CV < 10% (document rationale)
- Using median instead of mean for comparison (more robust to outliers)
- Implementing warm-up iterations before measurement
- Using criterion's "noisy benchmark" mode

---

## Test Run Summary

**Total Tests**: 10
**Passed**: 9
**Failed**: 1
**Ignored**: 0

### Passing Tests
- test_compiler_benchmarks_file_exists
- test_compiler_benchmarks_preparsed_ast
- test_compiler_benchmarks_estimates_json_exist
- test_compiler_benchmarks_run_successfully
- test_edge_case_compiler_simple_isolation
- test_edge_case_compiler_complex_nested_operations
- test_edge_case_compiler_variables_has_assignments
- test_edge_case_no_lexer_or_parser_in_loop
- test_edge_case_black_box_usage

### Failing Tests
- test_compiler_benchmarks_cv_under_5_percent ❌

---

## Conclusion

The implementation is **functionally correct** but **fails quality requirements**:

✅ All benchmark code is correctly structured
✅ All benchmarks execute successfully
✅ All output files are generated correctly
✅ Compiler performance is correctly isolated
❌ **Measurement stability does not meet AC4 requirements**

**Verdict**: **FAIL** - AC4 violation is a blocking issue that must be resolved before this implementation can be accepted.
