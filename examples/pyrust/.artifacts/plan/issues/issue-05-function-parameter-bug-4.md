# issue-05-function-parameter-bug-4: Fix register allocation for parameter operations

## Description
Fix register allocation collision in vm.rs when function parameters are used in multiple operations within the function body. Currently, test_function_using_param_in_multiple_operations returns incorrect value (38) instead of expected value (28) due to parameters not being correctly placed in both registers AND local_vars during CallFrame initialization.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section Phase 4 (Bug #4: Register allocation collision in parameter usage) for:
- CallFrame structure with saved_registers and local_vars
- Instruction::Call handler modification requirements
- Parameter placement strategy (registers 0..N-1 AND local_vars HashMap)

## Interface Contracts
- **Modifies**: `VM::execute()` method in src/vm.rs, Instruction::Call handler
- **Fix**: Ensure parameters copied to BOTH `frame.saved_registers[i]` AND `frame.local_vars.insert(param_id, value)`
- **Signature**: No signature changes, internal CallFrame initialization logic only

## Files
- **Modify**: `src/vm.rs` (Instruction::Call handler, lines ~393-432)

## Dependencies
- issue-03-function-parameter-bug-3 (provides: parameter name interning in bytecode)

## Provides
- Correct register allocation for parameter operations
- Fixed test_function_using_param_in_multiple_operations

## Acceptance Criteria
- [ ] test_function_using_param_in_multiple_operations returns "28" (complex(10) = 11 + 20 + 7)
- [ ] All 664 currently passing tests still pass (no regressions)
- [ ] Parameters accessible in function body via both direct register access and LoadVar instruction

## Testing Strategy

### Test Files
- `tests/test_functions.rs`: Contains test_function_using_param_in_multiple_operations

### Test Categories
- **Unit test**: test_function_using_param_in_multiple_operations (function with param used in a+1, x*2, x-3)
- **Regression tests**: Full cargo test --release suite (664 tests must remain passing)
- **Edge cases**: Multiple parameter operations, nested arithmetic with same parameter

### Run Command
```bash
cargo test test_function_using_param_in_multiple_operations --release
cargo test --release  # Verify no regressions
```
