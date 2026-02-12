# Code Review Issues - parser-benchmarks

## BLOCKING Issues

### 1. CV Exceeds 5% Threshold for All Benchmarks
**Severity**: BLOCKING
**File**: `benches/parser_benchmarks.rs`
**Acceptance Criteria**: AC4 - CV < 5% for all benchmarks

**Issue**: All three parser benchmarks have Coefficient of Variation (CV) significantly exceeding the 5% threshold specified in the acceptance criteria:

- `parser_simple`: CV = 5.60% (target: <5%)
- `parser_complex`: CV = 14.80% (target: <5%)
- `parser_variables`: CV = 48.01% (target: <5%)

**Evidence**: Calculated from estimates.json files:
```
parser_simple: std_dev=91656.89 / mean=1638042.49 * 100 = 5.60%
parser_complex: std_dev=772132.20 / mean=5216638.11 * 100 = 14.80%
parser_variables: std_dev=704507.60 / mean=1467136.89 * 100 = 48.01%
```

**Why This Blocks**: The acceptance criteria explicitly requires "CV < 5% for all benchmarks". This is a quantifiable requirement that is not met. The benchmarks fail to provide the statistical stability needed for reliable performance measurement.

**Root Cause**: The batching approach (12000 iterations per sample) is measuring the wrong thing. Instead of measuring individual parse operations with low variance, it's measuring batches of 12000 operations, which includes clone overhead and accumulates variance. Additionally, the very fast operation times (80-250ns per parse) are at the limit of measurement precision, making it difficult to achieve low CV.

**Required Fix**: The benchmark configuration needs to be adjusted to achieve CV < 5%. This may require:
1. Different batching strategy or no batching
2. Longer warm-up/measurement times
3. More samples
4. Different approach to handling very fast operations

---

## Summary
The implementation correctly creates the three required benchmarks (parser_simple, parser_complex, parser_variables) and properly pre-tokenizes input outside the benchmark loop. The Criterion configuration generates estimates.json files as required. However, the critical acceptance criterion of CV < 5% is not met for any of the three benchmarks, with CVs ranging from 5.60% to 48.01%.
