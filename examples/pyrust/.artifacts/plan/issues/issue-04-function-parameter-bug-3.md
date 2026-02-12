# issue-04-function-parameter-bug-3: Fix parameter name interning in bytecode

## Description
Add `builder.ensure_var_name()` call in function compilation loop to register parameter names in bytecode var_names pool. Currently, parameter names are interned in VariableInterner but not added to bytecode, causing "Parameter not found" errors in VM execution.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section "Phase 4: Bug Fixes (14 Tests)" → Component 4.1 → Bug #3 (lines 1451-1488) for:
- Bug analysis explaining missing bytecode var_names registration
- Exact fix location in `compile_program()` function body compilation
- Single-line code change: `self.builder.ensure_var_name(&param_name, var_id);`

## Interface Contracts
- Modifies: `src/compiler.rs::compile_program()` function parameter interning loop (lines 376-383)
- Calls: `BytecodeBuilder::ensure_var_name(&self, name: &str, var_id: u32) -> usize`
- Ensures: Parameter names exist in both `VariableInterner` AND `Bytecode.var_names` pool

## Files
- **Modify**: `src/compiler.rs` (add one line inside parameter interning loop at ~line 382)

## Dependencies
None (independent bug fix)

## Provides
- Correct parameter name registration in bytecode
- Fixed test_function_calling_convention_multiple_args

## Acceptance Criteria
- [ ] AC4.3: `cargo test test_function_calling_convention_multiple_args --release` passes without "Parameter not found" error
- [ ] AC4.2: All 664 currently passing tests still pass (`cargo test --release` shows 0 regressions)

## Testing Strategy

### Test Files
- `tests/integration_tests.rs`: Contains `test_function_calling_convention_multiple_args` (validates multi-parameter function calls)

### Test Categories
- **Unit tests**: N/A (fix is in compiler, validated by integration test)
- **Functional tests**: `test_function_calling_convention_multiple_args` verifies parameter names are accessible in VM during function execution
- **Edge cases**: Implicitly covered by existing parameter handling tests (0 params, 1 param, multiple params)

### Run Command
```bash
# Target test (must pass)
cargo test test_function_calling_convention_multiple_args --release

# Full regression check (must show 0 failures)
cargo test --release
```
