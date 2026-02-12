# Test Failures — Iteration 4c48abca

## Acceptance Criteria Validation Results

### AC1: Create benches/lexer_benchmarks.rs with lexer_simple, lexer_complex, lexer_variables benchmarks
- **Status**: ✓ PASS
- **Verification**: File `benches/lexer_benchmarks.rs` exists with all three benchmark functions

### AC2: Each benchmark uses black_box() and samples ≥1000 iterations
- **Status**: ✓ PASS
- **Verification**:
  - All benchmarks use `black_box()` on inputs and outputs
  - Criterion configured with `sample_size(3000)` (exceeds ≥1000 requirement)
  - Each benchmark performs 1000 iterations per sample (batching strategy)

### AC3: Criterion generates estimates.json for each benchmark
- **Status**: ✓ PASS
- **Verification**: All required JSON files exist:
  - `target/criterion/lexer_simple/base/estimates.json` ✓
  - `target/criterion/lexer_complex/base/estimates.json` ✓
  - `target/criterion/lexer_variables/base/estimates.json` ✓

### AC4: CV (coefficient of variation) < 5% for all benchmarks
- **Status**: ✗ FAIL
- **Results**:
  - `lexer_simple`: CV=4.07% ✓ PASS
  - `lexer_complex`: CV=2.99% ✓ PASS
  - `lexer_variables`: CV=14.53% ✗ FAIL

## Test Failure Details

### lexer_variables benchmark - CV exceeds 5% threshold
- **File**: `benches/lexer_benchmarks.rs`
- **Benchmark**: `lexer_variables`
- **Error**: Coefficient of Variation (CV) = 14.53% exceeds acceptance criteria threshold of 5%
- **Expected**: CV < 5.0%
- **Actual**: CV = 14.53%
- **Measurements**:
  - Mean: 180,599.54 ns
  - Standard Deviation: 26,238.77 ns
  - CV: (26238.77 / 180599.54) × 100 = 14.53%

### Root Cause Analysis

The `lexer_variables` benchmark exhibits high variance (14.53% CV) despite the coder's optimization efforts with 1000-iteration batching and extended measurement time. This is significantly higher than the other two benchmarks:
- lexer_simple: 4.07% CV (acceptable)
- lexer_complex: 2.99% CV (acceptable)

The coder's summary acknowledges this issue: "lexer_simple CV=20.5%, lexer_variables CV=22.7%" were the original values, improved to current levels but still above the 5% target for lexer_variables.

### Potential Causes

1. **Memory allocation variance**: The lexer_variables test case processes a longer input string with multiple lines and variable assignments ("x = 10\ny = 20\nx + y"), which may cause more heap allocations and memory access patterns with higher variance
2. **Cache effects**: The multi-line input may interact differently with CPU caches across iterations
3. **System noise**: Even with 3000 samples and 20-second measurement time, external system noise may disproportionately affect this longer operation

### Impact

The acceptance criteria AC4 requires **ALL** benchmarks to achieve CV < 5%. Since `lexer_variables` fails this requirement, the overall issue does not pass acceptance testing, despite meeting the other three acceptance criteria.

## Coverage Assessment

### Missing Test Coverage

No additional test coverage is missing. The coder correctly implemented:
- ✓ All three required benchmarks (lexer_simple, lexer_complex, lexer_variables)
- ✓ Proper use of black_box() to prevent compiler optimizations
- ✓ Sample size ≥1000 (configured at 3000)
- ✓ Criterion configuration for robust statistics
- ✓ 1000-iteration batching to reduce measurement noise

### Edge Cases

The benchmark suite does not need traditional "edge cases" like empty inputs or error conditions, as it is performance testing, not functional testing. However, for completeness:

**Covered edge cases:**
- Simple expression (minimal tokenization overhead)
- Complex expression (nested operators, parentheses)
- Multi-line with variables (multiple tokens, assignments)

**No missing edge cases identified** - the three benchmark cases adequately cover the lexer performance spectrum from simple to complex.

## Recommendations

1. **Increase batching iterations**: Try 5000 or 10000 iterations per sample for lexer_variables specifically
2. **Isolate CPU core**: Run benchmarks with `taskset` (Linux) or similar to bind to a specific CPU core
3. **Longer measurement time**: Increase from 20s to 30s or 60s for lexer_variables
4. **Review acceptance criteria**: Consider if 5% CV is achievable for all lexer benchmarks, or if lexer_variables should have a relaxed threshold (e.g., 10% CV) due to its inherent complexity

## Summary

- **Total ACs**: 4
- **Passing ACs**: 3 (AC1, AC2, AC3)
- **Failing ACs**: 1 (AC4 - lexer_variables CV too high)
- **Overall Status**: FAIL
