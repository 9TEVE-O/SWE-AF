# issue-03-function-parameter-bug-2: Add forward reference validation for function calls

## Description
Add HashSet-based validation to reject function calls before function definitions. Currently, `test_function_calling_before_definition` succeeds incorrectly when it should return a CompileError. This fix ensures functions cannot be called before they are defined in the program, preventing undefined behavior.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section 4.2.2 (Bug #2: Missing forward reference check) for:
- HashSet tracking for defined_functions
- validate_no_forward_references() method signature and logic
- validate_expression_no_forward_refs() recursive validation
- CompileError construction with "Function '{}' called before definition" message

## Interface Contracts
- Implements:
  ```rust
  fn validate_no_forward_references(&self, stmt: &Statement, defined: &HashSet<String>) -> Result<(), CompileError>
  fn validate_expression_no_forward_refs(&self, expr: &Expression, defined: &HashSet<String>) -> Result<(), CompileError>
  ```
- Exports: Forward reference validation preventing undefined function calls
- Consumes: HashSet from std::collections, CompileError from error.rs
- Consumed by: issue-08-bug-fixes-verification (test suite validation)

## Files
- **Modify**: `src/compiler.rs`
  - Add `use std::collections::HashSet;` import
  - Add validation logic in `compile_program()` before main statement compilation
  - Add two validation methods to `impl Compiler` block

## Dependencies
- None (standalone bug fix)

## Provides
- Forward reference validation preventing undefined function calls
- Fixed test_function_calling_before_definition

## Acceptance Criteria
- [ ] test_function_calling_before_definition returns CompileError (currently succeeds incorrectly)
- [ ] All 664 currently passing tests still pass after fix
- [ ] CompileError message format: "Function '<name>' called before definition"
- [ ] Validation covers Expression::Call in all expression contexts (BinaryOp, UnaryOp, Print, etc.)

## Testing Strategy

### Test Files
- `tests/test_functions.rs`: Contains test_function_calling_before_definition (line 777)

### Test Categories
- **Unit test**: `test_function_calling_before_definition` should return `Err(CompileError)` when calling `foo()` before `def foo()`
- **Regression tests**: All 664 currently passing tests must still pass
- **Edge cases**: Function calls in nested expressions (BinaryOp, UnaryOp), Print statements

### Run Commands
```bash
cargo test test_function_calling_before_definition --release
cargo test --release  # Verify no regressions (664 tests pass)
```
