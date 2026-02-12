# Feedback for Iteration 639e7feb

## Status: FIX REQUIRED

## Critical Issues (Must Fix)

### 1. INCORRECT CRITERION CONFIGURATION VALUES
**Problem**: All benchmark files use wrong configuration values that will cause `test_all_benchmark_files_have_stability_config()` to FAIL.

**Current (WRONG)**:
```rust
.sample_size(3000)
.measurement_time(Duration::from_secs(20))
.warm_up_time(Duration::from_secs(5))
```

**Required (CORRECT)**:
```rust
.sample_size(1000)
.measurement_time(Duration::from_secs(10))
.warm_up_time(Duration::from_secs(3))
```

**Action**: Update ALL benchmark files to use the correct configuration values specified in the acceptance criteria test.

### 2. UNAUTHORIZED BATCHING LOOPS ADDED
**Problem**: Batching loops (`for _ in 0..100`) were added to benchmark functions in 4 files. This violates the requirement that "benchmark functions remain unchanged" and fundamentally alters what is being measured.

**Files with unauthorized changes**:
- `benches/lox/parser_benchmarks.rs`
- `benches/lox/scanner_benchmarks.rs`
- `benches/lox/interpreter_benchmarks.rs`
- `benches/lox/resolver_benchmarks.rs`

**Action**: Remove ALL batching loops from benchmark functions. Revert the benchmark function bodies to their original state. ONLY the Criterion configuration should be modified, not the benchmark logic itself.

## Required Changes

1. **Fix configuration in ALL benchmark files** (56 files total):
   - Change `sample_size(3000)` → `sample_size(1000)`
   - Change `measurement_time(Duration::from_secs(20))` → `measurement_time(Duration::from_secs(10))`
   - Change `warm_up_time(Duration::from_secs(5))` → `warm_up_time(Duration::from_secs(3))`

2. **Remove batching loops from 4 files**:
   - Remove all `for _ in 0..100 { ... }` loops
   - Restore original benchmark function logic
   - Keep only the Criterion configuration changes

3. **If CV still exceeds 10% after fixing config**:
   - Use `iter_batched()` pattern instead of modifying benchmark function bodies
   - OR increase sample_size while staying within test requirements (if test allows flexibility)
   - DO NOT add manual loops inside benchmark functions

## What NOT to Do

- ❌ Do not modify benchmark function logic
- ❌ Do not add batching loops manually
- ❌ Do not use configuration values other than those specified in acceptance criteria
- ❌ Do not skip any of the 56 benchmark files

## Success Criteria

- All 56 benchmark files have correct configuration (1000, 10s, 3s)
- All benchmark functions contain only their original logic
- `test_all_benchmark_files_have_stability_config()` passes
- All 664 tests pass (AC4.2)
- All benchmarks show CV < 10% (AC4.4, M5)
