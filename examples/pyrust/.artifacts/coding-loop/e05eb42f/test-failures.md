# Test Failures — Iteration e05eb42f

## Summary
**Status**: ✅ ALL TESTS PASSED

All 338 tests passed successfully, including:
- 199 existing tests (regression check passed)
- 139 new tests (133 from initial implementation + 6 new edge case tests added by QA)

## Test Coverage by Acceptance Criteria

### AC2.2: Zero-parameter functions execute correctly and return values
✅ Covered by:
- `test_zero_param_function_call`
- `test_function_with_zero_result_printed`

### AC2.3: Functions with parameters execute correctly (arguments passed as values)
✅ Covered by:
- `test_function_with_one_parameter`
- `test_function_with_two_parameters`
- `test_function_with_three_parameters`
- `test_function_with_negative_parameters`
- `test_function_using_arithmetic_on_parameters`

### AC2.4: Local variables are isolated from global scope (function x != global x)
✅ Covered by:
- `test_local_scope_isolation`
- `test_local_variable_shadows_global`
- `test_function_parameter_names_dont_leak`
- `test_function_can_access_global_variables`

### AC2.5: Return without value works (returns None, empty output)
✅ Covered by:
- `test_function_return_without_value`
- `test_empty_function_body_returns_none`
- `test_function_with_none_return_value`

### AC2.8 (partial): Function call overhead is measurable
✅ Tests validate function execution works correctly
⚠️ Performance benchmarks not included (unit tests only)

### Additional Coverage:
- **DefineFunction instruction**: `test_define_function_stores_metadata`, `test_multiple_function_definitions`, `test_function_redefine_overwrites`
- **Call instruction**: All function call tests verify CallFrame creation, state saving, and jumping
- **Return instruction**: `test_registers_restored_after_function_call` explicitly tests CallFrame restoration
- **Error handling**: `test_undefined_function_error`, `test_wrong_argument_count_error`, `test_return_outside_function_error`
- **Complex scenarios**: `test_nested_function_calls`, `test_deeply_nested_calls`, `test_call_stack_depth`, `test_recursive_function_countdown`

## New Edge Case Tests Added by QA

1. **test_function_with_none_return_value**: Validates that Value::None is properly stored in variables
2. **test_multiple_function_calls_in_sequence**: Tests multiple function calls with results stored in variables
3. **test_function_using_arithmetic_on_parameters**: Complex arithmetic operations on parameters
4. **test_function_with_negative_parameters**: Ensures negative values work correctly
5. **test_call_stack_depth**: Tests 5-level deep nested function calls
6. **test_function_with_zero_result_printed**: Validates zero is distinguished from None

## Regression Check
✅ All 199 existing VM tests continue to pass (AC requirement met)

## Test Count Validation
✅ 31 function-specific tests created (exceeds "at least 20 new VM tests" requirement)

## No Failures Detected
No test failures were found. Implementation is production-ready.
