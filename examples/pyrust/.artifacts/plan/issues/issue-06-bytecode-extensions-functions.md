# issue-06-bytecode-extensions-functions: Add bytecode instructions for function operations

## Description
Extend the bytecode instruction set to support function operations: defining functions, calling functions, and returning from functions. This includes updating the BytecodeBuilder with emit methods for the new instructions. Does not implement any execution logic (VM implementation is issue-09).

## Architecture Reference
Read `architecture.md` Section 7 (Bytecode Module) and Extension Point 2 (Function Call Support) for:
- `Instruction` enum extension pattern
- `BytecodeBuilder` emit method signatures
- Constant pool and variable name pool deduplication strategy
- Register-based instruction format (dest, src registers as u8)

## Interface Contracts
```rust
// Implements (add to src/bytecode.rs):
Instruction::DefineFunction { name_index: usize, param_count: u8, body_start: usize, body_len: usize }
Instruction::Call { name_index: usize, arg_count: u8, dest_reg: u8 }
Instruction::Return { has_value: bool, src_reg: Option<u8> }

// Builder methods:
BytecodeBuilder::emit_define_function(name: &str, param_count: u8, body_start: usize, body_len: usize)
BytecodeBuilder::emit_call(func_name: &str, arg_count: u8, dest_reg: u8)
BytecodeBuilder::emit_return(src_reg: Option<u8>)
```

## Files
- **Modify**: `src/bytecode.rs` (add 3 instruction variants, 3 builder methods)

## Dependencies
None (pure bytecode format definition)

## Provides
- `Instruction::DefineFunction` bytecode variant
- `Instruction::Call` bytecode variant
- `Instruction::Return` bytecode variant
- `BytecodeBuilder` emit methods for function instructions

## Acceptance Criteria
- [ ] New `Instruction::DefineFunction` variant with name_index, param_count, body_start, body_len fields
- [ ] New `Instruction::Call` variant with name_index, arg_count, dest_reg fields
- [ ] New `Instruction::Return` variant with has_value bool and src_reg Option<u8>
- [ ] BytecodeBuilder::emit_define_function() method deduplicates function names in var_names pool
- [ ] BytecodeBuilder::emit_call() method deduplicates function names in var_names pool
- [ ] BytecodeBuilder::emit_return() method handles both valued and void returns
- [ ] All existing bytecode tests pass (regression check)
- [ ] At least 10 new unit tests for function instructions and builder methods

## Testing Strategy

### Test Files
- `src/bytecode.rs`: `#[cfg(test)] mod tests` (extend existing test module)

### Test Categories
- **Instruction creation**: Verify DefineFunction, Call, Return variants can be created
- **Builder emit methods**: Test emit_define_function, emit_call, emit_return correctness
- **Pool deduplication**: Ensure function names deduplicate in var_names pool
- **Serialization**: Verify instruction fields are correctly set
- **Regression**: All existing bytecode tests pass (builder, pooling, all operators)

### Run Command
```bash
cargo test --lib bytecode
```
