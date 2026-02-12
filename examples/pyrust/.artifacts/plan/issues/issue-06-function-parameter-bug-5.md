# issue-06-function-parameter-bug-5: Fix early return parameter scope preservation

## Description
Fix CallFrame parameter scope preservation on early return in vm.rs. Currently, the call frame is popped before capturing the return value, destroying local_vars (including parameters) before they can be accessed. This causes "Parameter not found" errors when return statements reference parameters.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section 4.1 (Bug #5: Early return parameter scope) for:
- Return instruction handling in `execute()` method
- CallFrame lifecycle and register state management
- Order of operations: capture return value → pop frame → restore registers

## Interface Contracts
- Modifies: `Instruction::Return` handler in `src/vm.rs` `execute()` method
- Signature (no change): `Instruction::Return { has_value: bool, src_reg: Option<u8> }`
- Behavior change: Capture return value BEFORE `call_stack.pop()` instead of after

## Files
- **Modify**: `src/vm.rs` (lines ~441-470, search for "Instruction::Return")

## Dependencies
None (standalone bug fix)

## Provides
- Correct parameter scope preservation on early return
- Fixed test_function_with_multiple_return_paths_early_return

## Acceptance Criteria
- [ ] AC4.3: test_function_with_multiple_return_paths_early_return passes without "Parameter not found" error
- [ ] AC4.2: All 664 currently passing tests still pass (no regressions)
- [ ] Return value correctly captured before call frame destruction
- [ ] Register restoration still occurs after return value capture

## Testing Strategy

### Test Files
- `tests/test_functions.rs::test_function_with_multiple_return_paths_early_return`: Early return with unused parameter should return 42

### Test Categories
- **Unit test**: Verify early return with parameter in scope returns correct value
- **Regression test**: Ensure all existing function call tests still pass
- **Edge case**: Test return value capture with parameter references

### Run Commands
```bash
# Test specific fix
cargo test test_function_with_multiple_return_paths_early_return --release

# Verify no regressions
cargo test --release
```
