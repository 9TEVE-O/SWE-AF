# issue-00-allocation-profiling-test: Create dhat-based allocation counting test

## Description
Implement allocation profiling test using dhat crate to measure exact allocation
count for `execute_python('2 + 3')`. Critical for AC2 validation (≤5 allocations).
Uses `dhat::HeapStats::get()` for precise measurement with <1% overhead.

## Architecture Reference
Read architecture.md Section 4.2 (Allocation Profiling with dhat) for:
- dhat integration strategy (Section 4.2.1)
- Allocation test implementation pattern (Section 4.2.2)
- Allocation budget breakdown and clarification (Section 4.2.3)
- Feature flag configuration (`#[cfg(feature = "dhat-heap")]`)
- Warm-up loop methodology (100 iterations to populate caches)

## Interface Contracts
- Implements: Two test functions with signature `fn test_allocation_count() -> ()`
- Uses: `dhat::Profiler::new_heap()`, `dhat::HeapStats::get()`
- Test attributes: `#[test]`, `#[ignore]`, `#[cfg(not(miri))]`
- Allocation measurement: `stats_after.total_blocks - stats_before.total_blocks`
- Assertion: `assert!(alloc_count <= 5)` for simple, `<= 8` for variables

## Files
- **Create**: `tests/allocation_count_test.rs`
- **Modify**: `Cargo.toml` (add `dhat = "0.3"` to dev-dependencies)

## Dependencies
None (this is the first test infrastructure issue)

## Provides
- Exact allocation counting infrastructure via dhat
- AC2 validation test (≤5 allocations for `execute_python("2 + 3")`)
- Allocation profiling methodology for future optimization validation

## Acceptance Criteria
- [ ] `tests/allocation_count_test.rs` created with `test_allocation_count` function
- [ ] Second test `test_allocation_count_with_variables` implemented
- [ ] dhat 0.3 added to Cargo.toml dev-dependencies
- [ ] Tests marked with `#[ignore]` and `#[cfg(not(miri))]`
- [ ] Warm-up loop (100 iterations) before measurement
- [ ] Assert allocation count ≤ 5 for simple, ≤ 8 for variables
- [ ] Tests output allocation count to stderr with `eprintln!`
- [ ] Tests validate correctness even when dhat feature disabled

## Testing Strategy

### Test Files
- `tests/allocation_count_test.rs`: Allocation profiling tests for simple and
  variables programs

### Test Categories
- **Functional tests**: Verify `execute_python("2 + 3")` returns "5" and
  `execute_python("x = 10\ny = 20\nx + y")` returns "30"
- **Profiling tests**: Count exact allocations via dhat when feature enabled
- **Edge cases**: Test runs without dhat feature, validating correctness only

### Run Command
```bash
cargo test --features dhat-heap test_allocation_count -- --ignored --nocapture
```
Expected output: Allocation count ≤5 printed to stderr, test passes
