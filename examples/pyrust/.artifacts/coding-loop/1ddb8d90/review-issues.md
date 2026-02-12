# Code Review Issues - bytecode-extensions-functions

## BLOCKING Issues

### 1. Missing BytecodeBuilder emit methods for function instructions

**Severity**: BLOCKING
**Location**: src/bytecode.rs - BytecodeBuilder implementation

**Description**:
The acceptance criteria explicitly require "BytecodeBuilder methods: emit_define_function(), emit_call(), emit_return()" but these methods are completely missing from the implementation.

**Current State**:
- ✅ Instruction variants exist (DefineFunction, Call, Return)
- ❌ Missing `emit_define_function()` method
- ❌ Missing `emit_call()` method
- ❌ Missing `emit_return()` method

**Why This Is Blocking**:
This is a core requirement that makes the new instructions usable. Without these emit methods, users cannot easily create bytecode with function operations using the builder pattern that is established for all other instructions (emit_load_const, emit_print, etc.). The instructions exist but are not accessible through the builder API.

**Required Fix**:
Add three public methods to BytecodeBuilder (after line 175):

```rust
/// Emit DefineFunction instruction
pub fn emit_define_function(&mut self, func_name: &str, param_count: u8, body_start: usize, body_len: usize) {
    let name_index = self.add_var_name(func_name);
    self.instructions.push(Instruction::DefineFunction {
        name_index,
        param_count,
        body_start,
        body_len,
    });
}

/// Emit Call instruction
pub fn emit_call(&mut self, func_name: &str, arg_count: u8, dest_reg: u8) {
    let name_index = self.add_var_name(func_name);
    self.instructions.push(Instruction::Call {
        name_index,
        arg_count,
        dest_reg,
    });
}

/// Emit Return instruction
pub fn emit_return(&mut self, has_value: bool, src_reg: Option<u8>) {
    self.instructions.push(Instruction::Return { has_value, src_reg });
}
```

**Testing Requirements**:
The acceptance criteria also require "At least 10 new unit tests" that should include:
- Tests for emit_define_function() method
- Tests for emit_call() method
- Tests for emit_return() method
- Tests verifying function name deduplication in var_names pool

Currently only 4 new tests exist (testing direct instruction creation), but tests for the emit methods and name deduplication are missing.

---

## Summary

Total Issues: 1 BLOCKING

The implementation is 60% complete:
- ✅ Instruction variants added correctly
- ✅ Basic instruction creation tests added
- ❌ Emit methods missing (core functionality)
- ❌ Insufficient test coverage (4/10+ tests)
- ❌ No tests for function name deduplication

This must be fixed before approval.
