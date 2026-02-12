# issue-00-vm-register-bitmap: Replace Vec<Option<Value>> with bitmap-based register validity

## Description
Replace VM's `Vec<Option<Value>>` register file with `Vec<Value>` + `[u64; 4]` bitmap for validity tracking. This eliminates Option pattern matching overhead (15-20 cycles → 8-10 cycles per access), delivering 40-50% reduction in register access time. Critical optimization for AC1 (VM overhead < 150ns).

## Architecture Reference
Read architecture.md Section 3.1 (VM Register File Optimization) for:
- Bitmap operations: `is_register_valid`, `set_register_valid`, `clear_register_valid` (section 3.1.2)
- Modified VM structure with `ip: usize` field (section 3.1.3)
- Register access helpers: `get_register`, `set_register` with actual IP tracking (section 3.1.2)
- Performance characteristics: 40-50% cycle reduction vs Option pattern match (section 3.1.2)

## Interface Contracts
- Implements:
  ```rust
  registers: Vec<Value>              // 256 preallocated slots
  register_valid: [u64; 4]           // 256-bit validity bitmap
  ip: usize                          // Instruction pointer for error tracking
  fn is_register_valid(&self, reg: u8) -> bool
  fn get_register(&self, reg: u8, ip: usize) -> Result<Value, RuntimeError>
  fn set_register(&mut self, reg: u8, value: Value)
  ```
- Exports: Bitmap-based register validity, instruction pointer tracking for accurate RuntimeError.instruction_index
- Consumes: Value with Copy trait (from issue-01-value-copy-trait)
- Consumed by: All VM benchmarks (issue-05-vm-benchmarks), allocation profiling (issue-08-allocation-profiling-test)

## Files
- **Modify**: `src/vm.rs` (update VM struct, add bitmap helpers, update all instruction handlers)

## Dependencies
- issue-01-value-copy-trait (provides: Copy semantics for Value::Integer)

## Provides
- Bitmap-based register validity eliminating Option overhead
- Instruction pointer tracking for accurate error messages
- 40-50% reduction in register access overhead (architecture section 3.1.2)

## Acceptance Criteria
- [ ] VM struct has `registers: Vec<Value>` and `register_valid: [u64; 4]` fields
- [ ] Inline helper methods implemented: `is_register_valid`, `set_register_valid`, `clear_register_valid`, `get_register`, `set_register`
- [ ] VM::new() initializes all registers to `Value::Integer(0)` with all validity bits cleared
- [ ] All instruction handlers (LoadConst, LoadVar, BinaryOp, UnaryOp, Print, SetResult, Call, Return) use `get_register`/`set_register`
- [ ] VM has `ip: usize` field, updated in execute() loop
- [ ] RuntimeError uses actual instruction pointer (`self.ip`) instead of placeholder 0
- [ ] All existing VM tests pass: `cargo test vm` and `cargo test integration`

## Testing Strategy

### Test Files
- `src/vm.rs`: 600+ existing unit tests covering all instruction handlers
- `tests/integration_test.rs`: End-to-end integration tests

### Test Categories
- **Unit tests**: `test_execute_load_const`, `test_execute_binary_op_add`, `test_execute_store_and_load_var`, `test_execute_print`, `test_execute_set_result`, `test_function_with_parameters`
- **Functional tests**: Register operations, function calls with register saving/restoration, error handling with correct IP
- **Edge cases**: `test_division_by_zero_error` (verify `instruction_index` is correct), `test_undefined_variable_error`, `test_registers_restored_after_function_call`

### Run Command
```bash
cargo test vm && cargo test integration
```
