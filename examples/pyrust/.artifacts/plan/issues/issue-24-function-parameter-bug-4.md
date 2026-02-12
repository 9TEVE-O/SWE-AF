# issue-24-function-parameter-bug-4: Fix test expectation for parameter operations

## Description
Correct the test expectation in test_function_using_param_in_multiple_operations from "28" to "38". The VM register allocation is already correct; the test expectation is mathematically incorrect (a=11, b=20, c=7, sum=38).

## Architecture Reference
Read architecture.md Section "Phase 4: Bug Fixes (14 Tests)" → Bug #4 (lines 1492-1564) for:
- Context on parameter register allocation (VM implementation is correct)
- Test validation requirements and expected behavior

## Interface Contracts
- **Modifies**: `tests/test_functions.rs::test_function_using_param_in_multiple_operations`
- **Change**: `assert_eq!(execute_python(code).unwrap(), "28");` → `assert_eq!(execute_python(code).unwrap(), "38");`
- **Rationale**: x=10: a=x+1=11, b=x*2=20, c=x-3=7, sum=11+20+7=38

## Files
- **Modify**: `tests/test_functions.rs` (line 683, update assertion from "28" to "38")

## Dependencies
- None (test correction only, VM implementation already correct)

## Provides
- Correct test expectation for test_function_using_param_in_multiple_operations
- Mathematically accurate validation of parameter operations

## Acceptance Criteria
- [ ] test_function_using_param_in_multiple_operations expects and returns "38" (11+20+7)
- [ ] All 664+ currently passing tests still pass (no regressions)
- [ ] Test validates correct parameter access in multiple operations

## Testing Strategy

### Test Files
- `tests/test_functions.rs`: Line 674-684, test_function_using_param_in_multiple_operations

### Test Categories
- **Functional test**: Validates parameter used in multiple arithmetic operations (a=x+1, b=x*2, c=x-3)
- **Regression check**: Full test suite must pass after correction (cargo test --release)
- **Mathematical validation**: Sum 11+20+7=38 for complex(10)

### Run Command
```bash
cargo test test_function_using_param_in_multiple_operations --release
cargo test --release  # Verify all tests pass
```
