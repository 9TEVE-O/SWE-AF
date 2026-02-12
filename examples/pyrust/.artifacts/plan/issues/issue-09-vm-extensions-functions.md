# issue-09-vm-extensions-functions: Execute function calls with call stack and local scope

## Description
Extend the VM to execute function bytecode instructions (DefineFunction, Call, Return). Implement call frame stack for tracking function calls, local variable scopes isolated from global scope, function storage (HashMap mapping name to bytecode offset), and call/return execution logic. This is the runtime component that makes functions executable.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section 9 (Virtual Machine Module) and Extension Point 2 (lines 1565-1713) for:
- VM struct extension with call_stack and functions storage
- CallFrame structure (return_address, base_register for local scope)
- Call instruction handler: push CallFrame, copy args, jump to function
- Return instruction handler: pop CallFrame, restore state, return value
- Function storage design (HashMap<String, FunctionMetadata>)

## Interface Contracts

### Implements
```rust
struct CallFrame {
    return_address: usize,    // IP to resume after function returns
    base_register: u8,        // Register offset for local variables
}

struct VM {
    // ... existing fields
    call_stack: Vec<CallFrame>,
    functions: HashMap<String, FunctionMetadata>,
}

// New instruction handlers in VM::execute() match block:
Instruction::DefineFunction { name, param_count, bytecode_offset } => { ... }
Instruction::Call { dest, func_index, arg_regs } => { ... }
Instruction::Return { src } => { ... }
```

### Exports
- CallFrame struct for managing function call state
- Call stack (Vec<CallFrame>) for nested/recursive calls
- Function storage for runtime function lookup
- Local scope isolation mechanism

### Consumes
- Instruction::DefineFunction, Call, Return from issue-07 (bytecode-extensions-functions)
- Compiled function bytecode from issue-08 (compiler-extensions-functions)

### Consumed by
- issue-10 (integration-regression-functions) validates function execution

## Files
- **Modify**: `src/vm.rs` (add CallFrame struct, extend VM struct, add instruction handlers)

## Dependencies
- issue-07 (bytecode-extensions-functions): Provides DefineFunction, Call, Return instruction types
- issue-08 (compiler-extensions-functions): Generates function bytecode that VM will execute

## Provides
- CallFrame struct with return_address, saved state
- Call stack (Vec<CallFrame>) managing nested calls
- Function storage (HashMap<String, FunctionMetadata>)
- DefineFunction, Call, Return instruction execution logic
- Local scope isolation from global scope

## Acceptance Criteria
- [ ] AC2.2: Zero-parameter functions execute and return values correctly
- [ ] AC2.3: Functions with parameters execute (arguments passed as values)
- [ ] AC2.4: Local variables isolated from global scope (function x != global x)
- [ ] AC2.5: Return without value works (returns None, empty output)
- [ ] AC2.8 (partial): Function call overhead measurable via benchmarks
- [ ] DefineFunction stores function metadata in HashMap
- [ ] Call instruction creates CallFrame, saves state, jumps to function body
- [ ] Return instruction restores CallFrame, returns value (if any), jumps back
- [ ] All 199 existing VM tests continue to pass (regression check)
- [ ] At least 20 new VM tests for function execution scenarios

## Testing Strategy

### Test Files
- `src/vm.rs` #[cfg(test)] mod tests: Add function execution tests following existing pattern

### Test Categories
- **Zero-param functions**: Define and call empty functions, verify return values
- **Parameterized functions**: Pass values as arguments, verify parameter binding
- **Return values**: Functions returning expressions vs empty return
- **Local scope**: Variables defined in function don't leak to global scope
- **Nested calls**: Function calling another function (call stack depth)
- **Recursion**: Simple recursive functions (e.g., countdown)
- **Error cases**: Undefined function call, wrong argument count
- **Regression**: All existing VM tests pass (verify no breakage)

### Run Command
```bash
cargo test --lib vm::tests
```
