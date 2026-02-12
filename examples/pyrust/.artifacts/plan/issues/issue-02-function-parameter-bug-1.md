# issue-02-function-parameter-bug-1: Fix function argument evaluation order

## Description
Reverse argument evaluation order in `compile_call()` to fix stack convention mismatch. Currently evaluates left-to-right but VM expects right-to-left per stack-based calling convention, causing `test_function_call_with_expression_args` to return 20 instead of expected 100.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Phase 4, Component 4.1 (Bug #1) for:
- Current buggy code in `compile_call()` function
- Exact fix implementation (single line: `arg_regs.reverse();`)
- Bug analysis explaining stack convention requirement
- Validation command and expected test output

## Interface Contracts
- **Modifies**: `Compiler::compile_call()` in `src/compiler.rs` (lines ~290-305)
- **Change**: Add `arg_regs.reverse();` after argument compilation loop
- **Effect**: Reverses argument register order before VM instruction emission

## Files
- **Modify**: `src/compiler.rs` (add single line after argument loop in `compile_call()`)

## Dependencies
None (standalone bug fix)

## Provides
- Correct argument evaluation order in function calls
- Fixed `test_function_call_with_expression_args` (returns 100)

## Acceptance Criteria
- [ ] AC4.3: `test_function_call_with_expression_args` returns 100 (verified via isolated test run)
- [ ] AC4.2: All 664 currently passing tests still pass (no regressions)

## Testing Strategy

### Test Files
- `tests/compiler_tests.rs` or similar: Contains `test_function_call_with_expression_args`

### Test Categories
- **Unit test**: `test_function_call_with_expression_args` - validates expression arguments evaluate in correct order for stack convention
- **Regression**: Full test suite (`cargo test --release`) - ensures no side effects from argument order reversal

### Run Commands
```bash
# Verify fix
cargo test test_function_call_with_expression_args --release

# Verify no regressions
cargo test --release
```
