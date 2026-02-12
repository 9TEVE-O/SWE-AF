# issue-00-register-state-optimization: Optimize function call register copying

## Description
Modify CallFrame to save only used registers instead of all 256, tracked via compiler metadata max_register_used. Reduces function call overhead from ~2000 cycles to ~50-150 cycles (~90-95% improvement).

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts-v2/plan/architecture.md` Section 3.4.2 (Optimized Register State Management) for:
- CompilerMetadata struct with max_register_used tracking
- save_register_state() and restore_register_state() signatures
- Modified CallFrame structure with saved_registers, saved_register_valid, max_saved_reg
- Call instruction handler integration pattern

## Interface Contracts
**Implements:**
```rust
pub struct CompilerMetadata { pub max_register_used: u8 }
impl VM {
    fn save_register_state(&self, max_reg: u8) -> Vec<Value>;
    fn restore_register_state(&mut self, saved: Vec<Value>);
}
struct CallFrame {
    saved_registers: Vec<Value>,
    saved_register_valid: [u64; 4],
    max_saved_reg: u8,
}
```

**Exports:** Optimized register state copying for function calls
**Consumes:** Bitmap-based register validity from issue-02-vm-register-bitmap, variable name interning (u32 IDs) from issue-03-variable-name-interning
**Consumed by:** issue-11-integration-verification, issue-12-performance-validation

## Files
- **Modify**: `src/compiler.rs` (add CompilerMetadata tracking, populate max_register_used)
- **Modify**: `src/bytecode.rs` (add metadata: CompilerMetadata field to Bytecode)
- **Modify**: `src/vm.rs` (add save/restore helpers, update CallFrame, modify Call instruction handler)

## Dependencies
- issue-03-variable-name-interning (provides: HashMap<u32, Value> variable storage)

## Provides
- Optimized register state copying saving only used registers
- 90-95% reduction in function call overhead (architecture section 3.4.2)
- CompilerMetadata with max_register_used tracking

## Acceptance Criteria
- [ ] CompilerMetadata struct with max_register_used: u8 field exists in bytecode.rs
- [ ] Compiler tracks max_register_used during compilation, stores in Bytecode.metadata
- [ ] FunctionMetadata includes max_register_used: Option<u8> field
- [ ] VM implements save_register_state(max_reg: u8) copying only registers [0..=max_reg]
- [ ] VM implements restore_register_state(saved: Vec<Value>) restoring saved registers and updating validity bitmap
- [ ] CallFrame stores saved_registers: Vec<Value>, saved_register_valid: [u64; 4], max_saved_reg: u8
- [ ] Call instruction handler uses max_register_used from compiler metadata to minimize saved registers
- [ ] All function call tests pass (70+ function tests in vm.rs and test_functions.rs)

## Testing Strategy

### Test Files
- `tests/vm.rs`: Function call tests validating register save/restore behavior
- `tests/test_functions.rs`: 70+ comprehensive function tests including nested calls

### Test Categories
- **Unit tests**: save_register_state(), restore_register_state() with various max_reg values (0, 5, 255)
- **Functional tests**: test_registers_restored_after_function_call, test_nested_function_calls, test_deeply_nested_calls, test_call_stack_depth
- **Edge cases**: max_reg=0 (no registers), max_reg=255 (all registers), function calls with no local variables

### Run Command
`cargo test test_functions`
