# Issue: Public API and lib.rs Implementation

## Summary
Implement the public API entry point and module declarations in lib.rs. Orchestrates the full pipeline: lex → parse → compile → execute → format output.

## Context
This is the final integration module that ties all components together. It provides the single public function execute_python() that external callers use. Must handle all error types and return properly formatted output.

## Architecture Reference
See architecture.md lines 150-221 for complete API specification.

## Implementation Requirements

### 1. Create `src/lib.rs` with Exact Implementation

```rust
//! PyRust - Microsecond Python Compiler
//!
//! A high-performance Python execution engine that achieves < 100μs execution time
//! for basic arithmetic expressions through bytecode compilation.

// Module declarations
pub mod error;
pub mod lexer;
pub mod ast;
pub mod parser;
pub mod value;
pub mod bytecode;
pub mod compiler;
pub mod vm;

// Re-export main API
pub use error::PyRustError;

/// Execute Python source code and return the result.
///
/// # Arguments
/// * `code` - Python source code as UTF-8 string slice
///
/// # Returns
/// * `Ok(String)` - Execution result formatted as: {stdout}{final_expression_value}
/// * `Err(PyRustError)` - Parse error, compile error, or runtime error
///
/// # Output Format
/// The returned string contains:
/// 1. All output from print() statements (each followed by \n)
/// 2. The value of the last expression statement (if any), WITHOUT trailing \n
/// 3. If no expression statements exist, only print output is returned
/// 4. If input is empty or contains only assignments, returns empty string ""
///
/// # Output Format Examples
/// ```
/// use pyrust::execute_python;
///
/// assert_eq!(execute_python("2 + 3").unwrap(), "5");
/// assert_eq!(execute_python("print(42)").unwrap(), "42\n");
/// assert_eq!(execute_python("print(42)\n10 + 5").unwrap(), "42\n15");
/// assert_eq!(execute_python("x = 10").unwrap(), "");
/// assert_eq!(execute_python("").unwrap(), "");
/// ```
///
/// # Performance
/// Target: < 100μs for arithmetic expressions like "2 + 3"
///
/// # Example
/// ```
/// use pyrust::execute_python;
///
/// let result = execute_python("2 + 3 * 4").unwrap();
/// assert_eq!(result, "14");
///
/// let result = execute_python("x = 10\ny = 20\nprint(x + y)\nx * y").unwrap();
/// assert_eq!(result, "30\n200");
/// ```
pub fn execute_python(code: &str) -> Result<String, PyRustError> {
    // 1. Lex source code into tokens
    let tokens = lexer::lex(code)?;

    // 2. Parse tokens into AST
    let ast = parser::parse(tokens)?;

    // 3. Compile AST to bytecode
    let bytecode = compiler::compile(&ast)?;

    // 4. Execute bytecode in VM
    let mut vm = vm::VM::new();
    let result = vm.execute(&bytecode)?; // Returns Option<Value>

    // 5. Format output (stdout + final value)
    Ok(vm.format_output(result))
}
```

### 2. Integration Tests

Create `tests/api_integration_test.rs`:

```rust
//! Integration tests for the public API
//! These tests verify the complete pipeline from code to output

use pyrust::execute_python;

#[test]
fn test_api_exists() {
    // Verify function signature is correct
    let _: Result<String, pyrust::PyRustError> = execute_python("1");
}

#[test]
fn test_simple_integer() {
    let result = execute_python("42").unwrap();
    assert_eq!(result, "42");
}

#[test]
fn test_addition() {
    let result = execute_python("2 + 3").unwrap();
    assert_eq!(result, "5");
}

#[test]
fn test_operator_precedence() {
    let result = execute_python("2 + 3 * 4").unwrap();
    assert_eq!(result, "14");
}

#[test]
fn test_parentheses() {
    let result = execute_python("(2 + 3) * 4").unwrap();
    assert_eq!(result, "20");
}

#[test]
fn test_variable_assignment() {
    let result = execute_python("x = 10\nx").unwrap();
    assert_eq!(result, "10");
}

#[test]
fn test_multiple_variables() {
    let result = execute_python("x = 10\ny = 20\nx + y").unwrap();
    assert_eq!(result, "30");
}

#[test]
fn test_print_statement() {
    let result = execute_python("print(42)").unwrap();
    assert_eq!(result, "42\n");
}

#[test]
fn test_print_with_expression() {
    let result = execute_python("print(2 + 3)").unwrap();
    assert_eq!(result, "5\n");
}

#[test]
fn test_print_and_expression() {
    let result = execute_python("print(42)\n10 + 5").unwrap();
    assert_eq!(result, "42\n15");
}

#[test]
fn test_multiple_prints() {
    let result = execute_python("print(10)\nprint(20)\nprint(30)").unwrap();
    assert_eq!(result, "10\n20\n30\n");
}

// BLOCKER 1 RESOLUTION: Output format edge cases
#[test]
fn test_output_format_empty_input() {
    let result = execute_python("").unwrap();
    assert_eq!(result, "");
}

#[test]
fn test_output_format_assignment_only() {
    let result = execute_python("x = 10").unwrap();
    assert_eq!(result, "");
}

#[test]
fn test_output_format_print_only() {
    let result = execute_python("print(42)").unwrap();
    assert_eq!(result, "42\n");
}

#[test]
fn test_output_format_expression_only() {
    let result = execute_python("2 + 3").unwrap();
    assert_eq!(result, "5");
}

#[test]
fn test_output_format_multiple_expressions() {
    let result = execute_python("10\n20\n30").unwrap();
    assert_eq!(result, "30", "Last expression should win");
}

#[test]
fn test_output_format_assignment_then_expression() {
    let result = execute_python("x = 10\nx").unwrap();
    assert_eq!(result, "10");
}

#[test]
fn test_output_format_print_then_assignment() {
    let result = execute_python("print(1)\nx = 5").unwrap();
    assert_eq!(result, "1\n");
}

#[test]
fn test_output_format_all_statement_types() {
    let result = execute_python("x = 10\nprint(x)\nx * 2").unwrap();
    assert_eq!(result, "10\n20");
}

#[test]
fn test_all_operators() {
    assert_eq!(execute_python("10 + 5").unwrap(), "15");
    assert_eq!(execute_python("10 - 5").unwrap(), "5");
    assert_eq!(execute_python("10 * 5").unwrap(), "50");
    assert_eq!(execute_python("20 / 4").unwrap(), "5");
    assert_eq!(execute_python("17 // 5").unwrap(), "3");
    assert_eq!(execute_python("17 % 5").unwrap(), "2");
}

#[test]
fn test_error_parse_error() {
    let result = execute_python("2 + + 3");
    assert!(result.is_err());

    let err = result.unwrap_err().to_string();
    assert!(err.contains("ParseError") || err.contains("Expected"));
}

#[test]
fn test_error_division_by_zero() {
    let result = execute_python("10 / 0");
    assert!(result.is_err());

    let err = result.unwrap_err().to_string();
    assert!(err.contains("Division by zero"));
}

#[test]
fn test_error_undefined_variable() {
    let result = execute_python("print(x)");
    assert!(result.is_err());

    let err = result.unwrap_err().to_string();
    assert!(err.contains("Undefined variable") || err.contains("x"));
}

#[test]
fn test_complex_program() {
    let code = r#"
x = 10
y = 20
z = x + y
print(z)
z * 2
"#;

    let result = execute_python(code).unwrap();
    assert_eq!(result, "30\n60");
}

#[test]
fn test_nested_expressions() {
    let result = execute_python("((2 + 3) * (4 + 5)) - 10").unwrap();
    assert_eq!(result, "35");
}

#[test]
fn test_variable_reassignment() {
    let result = execute_python("x = 10\nx = x + 5\nx").unwrap();
    assert_eq!(result, "15");
}

#[test]
fn test_zero_result() {
    // CRITICAL: Distinguish "0" from empty result
    let result = execute_python("0").unwrap();
    assert_eq!(result, "0");

    let result = execute_python("5 - 5").unwrap();
    assert_eq!(result, "0");
}

#[test]
fn test_negative_numbers() {
    // Negative numbers as part of expressions
    let result = execute_python("10 + -5").unwrap();
    assert_eq!(result, "5");

    let result = execute_python("0 - 10").unwrap();
    assert_eq!(result, "-10");
}

#[test]
fn test_whitespace_handling() {
    let result = execute_python("  2   +   3  ").unwrap();
    assert_eq!(result, "5");
}

#[test]
fn test_newline_variations() {
    // Unix newlines
    let result = execute_python("x = 10\ny = 20\nx + y").unwrap();
    assert_eq!(result, "30");

    // Multiple newlines
    let result = execute_python("x = 10\n\n\ny = 20\n\nx + y").unwrap();
    assert_eq!(result, "30");
}
```

## Acceptance Criteria

1. ✅ `src/lib.rs` exists with execute_python() function matching architecture exactly
2. ✅ All modules declared: error, lexer, ast, parser, value, bytecode, compiler, vm
3. ✅ PyRustError re-exported from lib root
4. ✅ execute_python() orchestrates full pipeline: lex → parse → compile → execute → format
5. ✅ Returns formatted string following output format specification
6. ✅ Error propagation works via ? operator (From trait implementations)
7. ✅ Integration tests pass: `cargo test --test api_integration_test`
8. ✅ All output format edge cases pass (empty, assignment-only, etc.)
9. ✅ Documentation examples compile and pass
10. ✅ Code compiles: `cargo build`

## Testing Instructions

```bash
# Run integration tests
cargo test --test api_integration_test

# Run output format edge case tests
cargo test --test api_integration_test test_output_format

# Run error handling tests
cargo test --test api_integration_test test_error

# Check compilation
cargo build

# Run all tests
cargo test
```

## Dependencies

- All modules: error, lexer, ast, parser, value, bytecode, compiler, vm

## Provides

- `execute_python(code: &str) -> Result<String, PyRustError>` - main public API
- Re-exports: `PyRustError`

## Interface Contract

**Input:**
- UTF-8 string containing Python source code
- Can be empty string
- No size limit in Phase 1 (PRD specifies ≤ 10KB)

**Output:**
- `Ok(String)` with formatted output: {stdout}{final_expression_value}
- `Err(PyRustError)` with one of: LexError, ParseError, CompileError, RuntimeError

**Output Format Guarantees** (BLOCKER 1 Resolution):
```rust
execute_python("")           → Ok("")
execute_python("x = 10")     → Ok("")
execute_python("2 + 3")      → Ok("5")
execute_python("print(42)")  → Ok("42\n")
execute_python("print(42)\n10 + 5") → Ok("42\n15")
execute_python("10\n20\n30") → Ok("30")
```

## Critical Implementation Notes

**Pipeline Flow:**
1. `lexer::lex(code)` → `Result<Vec<Token>, LexError>`
2. `parser::parse(tokens)` → `Result<Program, ParseError>`
3. `compiler::compile(&ast)` → `Result<Bytecode, CompileError>`
4. `vm.execute(&bytecode)` → `Result<Option<Value>, RuntimeError>`
5. `vm.format_output(result)` → `String`

**Error Handling:**
- All errors convert to PyRustError via From trait
- Use ? operator for clean propagation
- No panic in normal execution path

**Output Formatting:**
- VM tracks stdout and result separately
- format_output() combines them per specification
- No trailing newline after final expression value

## Performance Notes

- Target: < 100μs total for "2 + 3"
- No caching in Phase 1 (each call re-compiles)
- Phase 2: Add compilation cache keyed by source hash

## Documentation Notes

The doc comments on execute_python() are CRITICAL:
- They serve as the API contract
- Examples must compile and pass (doctest)
- Output format must be explicitly documented
- Performance target must be stated

## Notes

- This is the ONLY public function in Phase 1
- All other modules are implementation details
- Users only interact with execute_python() and PyRustError
- Future: Can add execute_python_cached(), execute_python_to_bytecode(), etc.
