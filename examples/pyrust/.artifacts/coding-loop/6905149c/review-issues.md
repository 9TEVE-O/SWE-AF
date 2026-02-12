# Code Review Issues - lexer-benchmarks

## BLOCKING Issues

### ❌ BLOCKING: CV exceeds 5% threshold for lexer_variables benchmark

**Severity**: BLOCKING
**Location**: `benches/lexer_benchmarks.rs` - `lexer_variables` benchmark
**Issue**: The coefficient of variation (CV) for the `lexer_variables` benchmark is 18.23%, which significantly exceeds the 5% threshold specified in the acceptance criteria.

**Details**:
- Measured CV: 18.23% (std_dev: 29.16ns / mean: 160.01ns)
- Required CV: < 5%
- Other benchmarks meet the requirement:
  - `lexer_simple`: CV = 3.44%
  - `lexer_complex`: CV = 3.50%

**Root Cause**: The `lexer_variables` test case (`x = 10\ny = 20\nx + y`) produces highly variable execution times, likely due to:
1. Multi-line input with newline characters requiring more complex state management
2. Higher allocation variance when processing variable assignments
3. Potential cache effects or branch prediction issues with the newline handling path

**Impact**: This violates acceptance criterion #4: "CV (coefficient of variation) < 5% for all benchmarks". The high variance makes the benchmark unreliable for detecting performance regressions.

**Recommended Fix**:
1. Increase sample_size further (try 5000 or 10000 samples)
2. Consider using a single-line input for lexer_variables: `x = 10; y = 20; x + y` (if semicolons are supported, otherwise use a different pattern)
3. Alternatively, use a simpler multi-line test case that doesn't involve variable assignments
4. Add warmup iterations to stabilize cache behavior before measurement

---

## Summary

The implementation correctly creates the three required benchmarks with proper use of `black_box()` and Criterion configuration. All benchmarks execute successfully and generate the required JSON output files. However, one benchmark (`lexer_variables`) fails to meet the CV < 5% stability requirement, which blocks approval.

**Acceptance Criteria Status**:
- ✅ AC1: Create benches/lexer_benchmarks.rs with lexer_simple, lexer_complex, lexer_variables benchmarks
- ✅ AC2: Each benchmark uses black_box() and samples ≥1000 iterations
- ✅ AC3: Criterion generates estimates.json for each benchmark
- ❌ AC4: CV < 5% for all benchmarks (lexer_variables: 18.23% > 5%)
