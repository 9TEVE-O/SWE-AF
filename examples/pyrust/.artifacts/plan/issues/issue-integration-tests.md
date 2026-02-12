# Issue: Integration Tests (AC1-AC4, AC7-AC8)

## Summary
Implement comprehensive integration tests covering API contract, arithmetic operations, variables, print statements, and error handling. These tests validate acceptance criteria AC1-AC4 and AC7-AC8 from the PRD.

## Context
Integration tests verify the complete pipeline works correctly from end to end. These are the primary validation that Phase 1 meets its functional requirements.

## Architecture Reference
See architecture.md lines 2104-2201 for integration test specification.

## Implementation Requirements

### 1. Create `tests/integration_test.rs`

```rust
//! Integration tests for PyRust Phase 1
//!
//! These tests validate acceptance criteria AC1-AC4 and AC7-AC8 from the PRD.

use pyrust::execute_python;

// ============================================================================
// AC1: API Contract
// ============================================================================

#[test]
fn test_ac1_api_contract() {
    // Verify function signature exists and returns Result
    let result = execute_python("2 + 3");
    assert!(result.is_ok(), "API should return Ok for valid input");
    assert_eq!(result.unwrap(), "5");
}

#[test]
fn test_ac1_api_returns_string() {
    let result = execute_python("42");
    assert!(result.is_ok());
    let output: String = result.unwrap();
    assert_eq!(output, "42");
}

#[test]
fn test_ac1_api_returns_error() {
    let result = execute_python("2 + + 3");
    assert!(result.is_err(), "API should return Err for invalid input");
}

// ============================================================================
// AC2: Arithmetic Expression Support
// ============================================================================

#[test]
fn test_ac2_addition() {
    assert_eq!(execute_python("2 + 3").unwrap(), "5");
    assert_eq!(execute_python("10 + 20").unwrap(), "30");
    assert_eq!(execute_python("0 + 0").unwrap(), "0");
}

#[test]
fn test_ac2_subtraction() {
    assert_eq!(execute_python("10 - 5").unwrap(), "5");
    assert_eq!(execute_python("100 - 50").unwrap(), "50");
    assert_eq!(execute_python("5 - 10").unwrap(), "-5");
}

#[test]
fn test_ac2_multiplication() {
    assert_eq!(execute_python("3 * 4").unwrap(), "12");
    assert_eq!(execute_python("10 * 10").unwrap(), "100");
    assert_eq!(execute_python("7 * 0").unwrap(), "0");
}

#[test]
fn test_ac2_division() {
    assert_eq!(execute_python("20 / 4").unwrap(), "5");
    assert_eq!(execute_python("100 / 10").unwrap(), "10");
    assert_eq!(execute_python("7 / 2").unwrap(), "3", "Integer division");
}

#[test]
fn test_ac2_floor_division() {
    assert_eq!(execute_python("17 // 5").unwrap(), "3");
    assert_eq!(execute_python("20 // 4").unwrap(), "5");
    assert_eq!(execute_python("7 // 2").unwrap(), "3");
}

#[test]
fn test_ac2_modulo() {
    assert_eq!(execute_python("17 % 5").unwrap(), "2");
    assert_eq!(execute_python("20 % 4").unwrap(), "0");
    assert_eq!(execute_python("7 % 3").unwrap(), "1");
}

#[test]
fn test_ac2_operator_precedence_multiply_first() {
    assert_eq!(execute_python("2 + 3 * 4").unwrap(), "14");
    assert_eq!(execute_python("10 - 2 * 3").unwrap(), "4");
}

#[test]
fn test_ac2_operator_precedence_divide_first() {
    assert_eq!(execute_python("20 + 10 / 2").unwrap(), "25");
    assert_eq!(execute_python("100 - 50 / 5").unwrap(), "90");
}

#[test]
fn test_ac2_parentheses_override_precedence() {
    assert_eq!(execute_python("(2 + 3) * 4").unwrap(), "20");
    assert_eq!(execute_python("(10 - 5) * 2").unwrap(), "10");
    assert_eq!(execute_python("100 / (2 + 3)").unwrap(), "20");
}

#[test]
fn test_ac2_nested_parentheses() {
    assert_eq!(execute_python("((2 + 3) * 4) - 5").unwrap(), "15");
    assert_eq!(execute_python("2 * (3 + (4 * 5))").unwrap(), "46");
}

#[test]
fn test_ac2_complex_expression() {
    assert_eq!(execute_python("2 + 3 * 4 - 5 / 2").unwrap(), "12");
    assert_eq!(execute_python("10 + 20 * 30 - 40 / 2").unwrap(), "590");
}

// ============================================================================
// AC3: Variable Assignment & Retrieval
// ============================================================================

#[test]
fn test_ac3_simple_assignment() {
    assert_eq!(execute_python("x = 10\nx").unwrap(), "10");
}

#[test]
fn test_ac3_assignment_with_expression() {
    assert_eq!(execute_python("x = 2 + 3\nx").unwrap(), "5");
    assert_eq!(execute_python("x = 10 * 5\nx").unwrap(), "50");
}

#[test]
fn test_ac3_multiple_assignments() {
    assert_eq!(execute_python("x = 10\ny = 20\nx + y").unwrap(), "30");
    assert_eq!(execute_python("a = 5\nb = 10\nc = 15\na + b + c").unwrap(), "30");
}

#[test]
fn test_ac3_variable_reuse() {
    assert_eq!(execute_python("x = 10\ny = x\ny").unwrap(), "10");
    assert_eq!(execute_python("x = 5\ny = x * 2\nz = y + 3\nz").unwrap(), "13");
}

#[test]
fn test_ac3_variable_reassignment() {
    assert_eq!(execute_python("x = 10\nx = 20\nx").unwrap(), "20");
    assert_eq!(execute_python("x = 5\nx = x + 1\nx").unwrap(), "6");
    assert_eq!(execute_python("x = 1\nx = x * 2\nx = x * 2\nx").unwrap(), "4");
}

#[test]
fn test_ac3_multiple_variables_in_expression() {
    assert_eq!(execute_python("x = 10\ny = 20\nz = 30\nx + y + z").unwrap(), "60");
    assert_eq!(execute_python("a = 2\nb = 3\nc = 4\na * b + c").unwrap(), "10");
}

// ============================================================================
// AC4: Print Statement Support
// ============================================================================

#[test]
fn test_ac4_print_literal() {
    assert_eq!(execute_python("print(42)").unwrap(), "42\n");
    assert_eq!(execute_python("print(0)").unwrap(), "0\n");
    assert_eq!(execute_python("print(12345)").unwrap(), "12345\n");
}

#[test]
fn test_ac4_print_variable() {
    assert_eq!(execute_python("x = 10\nprint(x)").unwrap(), "10\n");
    assert_eq!(execute_python("y = 99\nprint(y)").unwrap(), "99\n");
}

#[test]
fn test_ac4_print_expression() {
    assert_eq!(execute_python("print(2 + 3)").unwrap(), "5\n");
    assert_eq!(execute_python("print(10 * 5)").unwrap(), "50\n");
    assert_eq!(execute_python("print((2 + 3) * 4)").unwrap(), "20\n");
}

#[test]
fn test_ac4_multiple_prints() {
    assert_eq!(execute_python("print(1)\nprint(2)\nprint(3)").unwrap(), "1\n2\n3\n");
    assert_eq!(execute_python("print(10)\nprint(20)").unwrap(), "10\n20\n");
}

#[test]
fn test_ac4_print_with_variables() {
    let code = "x = 10\ny = 20\nprint(x)\nprint(y)";
    assert_eq!(execute_python(code).unwrap(), "10\n20\n");
}

#[test]
fn test_ac4_print_and_expression() {
    assert_eq!(execute_python("print(10)\n20").unwrap(), "10\n20");
    assert_eq!(execute_python("print(5)\nprint(10)\n15").unwrap(), "5\n10\n15");
}

#[test]
fn test_ac4_print_in_complex_program() {
    let code = r#"
x = 10
y = 20
print(x + y)
x * y
"#;
    assert_eq!(execute_python(code).unwrap(), "30\n200");
}

// ============================================================================
// AC7: Error Handling - Parse Errors
// ============================================================================

#[test]
fn test_ac7_double_operator() {
    let result = execute_python("2 + + 3");
    assert!(result.is_err());
    let err = result.unwrap_err().to_string();
    assert!(err.contains("ParseError") || err.contains("Expected"));
}

#[test]
fn test_ac7_missing_operand() {
    let result = execute_python("2 +");
    assert!(result.is_err());
    let err = result.unwrap_err().to_string();
    // Should report missing operand or unexpected EOF
    assert!(err.contains("ParseError") || err.contains("Expected") || err.contains("Eof"));
}

#[test]
fn test_ac7_unmatched_left_paren() {
    let result = execute_python("(2 + 3");
    assert!(result.is_err());
    let err = result.unwrap_err().to_string();
    assert!(err.contains("ParseError") || err.contains("Expected") || err.contains("RightParen"));
}

#[test]
fn test_ac7_unmatched_right_paren() {
    let result = execute_python("2 + 3)");
    assert!(result.is_err());
    // Extra closing paren should cause error
}

#[test]
fn test_ac7_invalid_character() {
    let result = execute_python("2 @ 3");
    assert!(result.is_err());
    let err = result.unwrap_err().to_string();
    assert!(err.contains("LexError") || err.contains("Unexpected"));
}

#[test]
fn test_ac7_error_has_location() {
    let result = execute_python("2 + + 3");
    assert!(result.is_err());
    let err = result.unwrap_err().to_string();
    // Error message should include line/column information
    assert!(err.contains("1:") || err.contains("line") || err.contains("column"));
}

// ============================================================================
// AC8: Error Handling - Runtime Errors
// ============================================================================

#[test]
fn test_ac8_division_by_zero() {
    let result = execute_python("10 / 0");
    assert!(result.is_err());
    let err = result.unwrap_err().to_string();
    assert!(err.contains("Division by zero") || err.contains("division"));
}

#[test]
fn test_ac8_modulo_by_zero() {
    let result = execute_python("10 % 0");
    assert!(result.is_err());
    let err = result.unwrap_err().to_string();
    assert!(err.contains("Modulo by zero") || err.contains("zero"));
}

#[test]
fn test_ac8_undefined_variable() {
    let result = execute_python("print(x)");
    assert!(result.is_err());
    let err = result.unwrap_err().to_string();
    assert!(err.contains("Undefined variable") || err.contains("x"));
}

#[test]
fn test_ac8_undefined_variable_in_expression() {
    let result = execute_python("y + 10");
    assert!(result.is_err());
    let err = result.unwrap_err().to_string();
    assert!(err.contains("Undefined variable") || err.contains("y"));
}

#[test]
fn test_ac8_integer_overflow_add() {
    let code = format!("{} + 1", i64::MAX);
    let result = execute_python(&code);
    assert!(result.is_err());
    let err = result.unwrap_err().to_string();
    assert!(err.contains("overflow") || err.contains("RuntimeError"));
}

#[test]
fn test_ac8_integer_overflow_multiply() {
    let code = format!("{} * 2", i64::MAX);
    let result = execute_python(&code);
    assert!(result.is_err());
}

#[test]
fn test_ac8_runtime_error_in_print() {
    let result = execute_python("print(10 / 0)");
    assert!(result.is_err());
    let err = result.unwrap_err().to_string();
    assert!(err.contains("Division by zero"));
}

// ============================================================================
// Additional Edge Cases
// ============================================================================

#[test]
fn test_empty_input() {
    assert_eq!(execute_python("").unwrap(), "");
}

#[test]
fn test_only_whitespace() {
    assert_eq!(execute_python("   \n\n  \n  ").unwrap(), "");
}

#[test]
fn test_assignment_returns_empty() {
    assert_eq!(execute_python("x = 10").unwrap(), "");
    assert_eq!(execute_python("x = 10\ny = 20").unwrap(), "");
}

#[test]
fn test_zero_value() {
    assert_eq!(execute_python("0").unwrap(), "0");
    assert_eq!(execute_python("5 - 5").unwrap(), "0");
    assert_eq!(execute_python("0 * 1000").unwrap(), "0");
}

#[test]
fn test_negative_result() {
    assert_eq!(execute_python("5 - 10").unwrap(), "-5");
    assert_eq!(execute_python("0 - 42").unwrap(), "-42");
}

#[test]
fn test_large_integers() {
    let code = format!("{}", i64::MAX);
    let result = execute_python(&code).unwrap();
    assert_eq!(result, format!("{}", i64::MAX));
}

#[test]
fn test_mixed_statement_types() {
    let code = r#"
x = 10
print(x)
y = 20
print(y)
x + y
"#;
    assert_eq!(execute_python(code).unwrap(), "10\n20\n30");
}
```

## Acceptance Criteria

1. ✅ `tests/integration_test.rs` exists with all AC1-AC4, AC7-AC8 tests
2. ✅ AC1 tests verify API contract (function signature, Result type)
3. ✅ AC2 tests verify all arithmetic operators and precedence
4. ✅ AC3 tests verify variable assignment and retrieval
5. ✅ AC4 tests verify print statement functionality
6. ✅ AC7 tests verify parse error handling with location info
7. ✅ AC8 tests verify runtime error handling (division by zero, undefined vars, overflow)
8. ✅ All tests pass: `cargo test --test integration_test`
9. ✅ Test coverage includes edge cases (empty input, zero values, negative results)
10. ✅ Tests are well-organized with clear section comments

## Testing Instructions

```bash
# Run all integration tests
cargo test --test integration_test

# Run specific AC tests
cargo test --test integration_test test_ac1
cargo test --test integration_test test_ac2
cargo test --test integration_test test_ac3
cargo test --test integration_test test_ac4
cargo test --test integration_test test_ac7
cargo test --test integration_test test_ac8

# Run with output
cargo test --test integration_test -- --nocapture

# Check test count
cargo test --test integration_test -- --list
```

## Dependencies

- `pyrust::execute_python` function
- All modules must be implemented and working

## Provides

- Validation that AC1-AC4, AC7-AC8 are satisfied
- Regression test suite for future changes
- Documentation of expected behavior through tests

## Test Organization

Tests are organized by acceptance criteria:
- **AC1**: API Contract (3 tests)
- **AC2**: Arithmetic (15 tests covering all operators and precedence)
- **AC3**: Variables (6 tests covering assignment and retrieval)
- **AC4**: Print (7 tests covering literals, variables, expressions)
- **AC7**: Parse Errors (6 tests covering syntax errors)
- **AC8**: Runtime Errors (8 tests covering runtime failures)
- **Edge Cases**: Additional tests for robustness

Total: ~45 integration tests

## Critical Test Cases

**Output Format Validation:**
```rust
execute_python("")           → ""
execute_python("x = 10")     → ""
execute_python("10")         → "10"
execute_python("print(10)")  → "10\n"
execute_python("print(10)\n20") → "10\n20"
```

**Error Handling:**
```rust
execute_python("2 + + 3")    → Err(ParseError with location)
execute_python("10 / 0")     → Err(RuntimeError: division by zero)
execute_python("print(x)")   → Err(RuntimeError: undefined variable)
```

## Notes

- These tests are the PRIMARY validation for Phase 1 completion
- All tests must pass before Phase 1 is considered done
- Tests serve as documentation of expected behavior
- AC5, AC6, AC9, AC10 are covered by separate test files
