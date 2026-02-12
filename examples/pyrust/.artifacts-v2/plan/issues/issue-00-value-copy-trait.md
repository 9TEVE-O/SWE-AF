# issue-00-value-copy-trait: Add Copy trait to Value enum for zero-cost integer copies

## Description
Implement Copy trait for Value enum to eliminate clone overhead in VM register operations. Both Integer(i64) and None variants are Copy-compatible. This optimization reduces value copy time from ~10-15 cycles to ~2-3 cycles, contributing to the AC1 target of 40% VM overhead reduction.

## Architecture Reference
Read architecture.md Section 3.2 (Value Optimization: Copy Trait for Integer) for:
- Copy trait implementation strategy and rationale
- Performance impact analysis (80% reduction in value copy overhead)
- Assembly comparison (before/after)
- Modified as_integer() panic behavior specification

## Interface Contracts
- **Implements**:
  ```rust
  #[derive(Debug, Clone, Copy, PartialEq, Eq)]
  pub enum Value { Integer(i64), None }

  impl Value {
      pub fn as_integer(&self) -> i64  // Panics on None with detailed error
  }
  ```
- **Exports**: Copy semantics for Value::Integer, documented as_integer() panic behavior
- **Consumes**: None (standalone optimization)
- **Consumed by**: issue-03-vm-register-bitmap (uses Copy for register operations)

## Files
- **Modify**: `src/value.rs`
  - Add `Copy` to derive list (line 14)
  - Update `as_integer()` documentation with panic behavior (lines 155-167)

## Dependencies
None (foundational optimization)

## Provides
- Copy semantics for Value::Integer enabling direct register-to-register copies
- Documented Value::as_integer() behavior for None cases

## Acceptance Criteria
- [ ] Value enum derives Copy trait in addition to Clone
- [ ] Value::as_integer() documents panic behavior on None with detailed error message
- [ ] All existing tests pass without modification (cargo test --release exits with code 0)
- [ ] No compilation errors or warnings

## Testing Strategy

### Test Files
- `src/value.rs`: Existing test module (25+ tests covering Value operations)

### Test Categories
- **Unit tests**: All existing value.rs tests verify Copy trait compatibility
- **Functional tests**: test_value_clone() validates Copy semantics work correctly
- **Edge cases**: test_binary_op_* tests verify Copy doesn't change behavior

### Run Command
```bash
cargo test --release value
```

All existing tests must pass unchanged, validating Copy trait compatibility.
