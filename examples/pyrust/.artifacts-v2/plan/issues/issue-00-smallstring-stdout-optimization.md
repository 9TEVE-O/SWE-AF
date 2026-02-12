# issue-00-smallstring-stdout-optimization: Optimize stdout buffer with SmallString inline storage

## Description
Replace VM.stdout String with SmallString enum to eliminate heap allocations for outputs ≤23 bytes. Simple print statements like `print(42)` produce "42\n" (3 bytes), currently requiring heap allocation. SmallString provides inline storage, reducing allocations by 1-2 per print operation.

## Architecture Reference
Read architecture.md Section 3.5.1 (SmallString Implementation) for:
- SmallString enum definition (Inline/Heap variants)
- SmallString::new(), push_str(), as_str() method signatures
- VM integration strategy with stdout field type change
- Inline/heap promotion logic when size exceeds 23 bytes

## Interface Contracts
- Implements:
  ```rust
  enum SmallString {
      Inline { len: u8, data: [u8; 23] },
      Heap(String),
  }
  fn new() -> Self
  fn push_str(&mut self, s: &str)
  fn as_str(&self) -> &str
  ```
- Exports: SmallString type with inline storage for ≤23 byte strings
- Consumes: None (self-contained optimization)
- Consumed by: VM.stdout field, VM::format_output() method

## Files
- **Modify**: `src/vm.rs`
  - Add SmallString enum definition with Inline/Heap variants
  - Add impl block with new(), push_str(), as_str() methods
  - Change VM.stdout field type from String to SmallString
  - Update VM::new() to initialize stdout with SmallString::new()
  - Update VM::format_output() to use stdout.as_str() instead of stdout.clone()
  - Update all Print instruction handlers to use stdout.push_str()

## Dependencies
- issue-11-register-state-optimization (provides: register state optimization)

## Provides
- SmallString inline storage eliminating allocations for outputs ≤23 bytes
- 1-2 allocation reduction per print statement (architecture section 3.5.1)

## Acceptance Criteria
- [ ] SmallString enum created in vm.rs with Inline { len: u8, data: [u8; 23] } and Heap(String) variants
- [ ] SmallString::new(), push_str(&mut self, s: &str), and as_str(&self) methods implemented
- [ ] SmallString::push_str promotes to heap when total size exceeds 23 bytes
- [ ] VM.stdout field type changed from String to SmallString
- [ ] VM::new() initializes stdout with SmallString::new()
- [ ] VM::format_output() uses stdout.as_str() instead of stdout.clone()
- [ ] All print-related tests pass (test_execute_print, test_format_output_*, test_function_with_print_statement)

## Testing Strategy

### Test Files
- `src/vm.rs`: Existing tests for print functionality

### Test Categories
- **Unit tests**: SmallString::new(), push_str() inline case, push_str() heap promotion, as_str() for both variants
- **Functional tests**: VM print statements with inline output (≤23 bytes), VM print statements requiring heap (>23 bytes)
- **Edge cases**: Empty string, exactly 23 bytes, 24 bytes (promotion), multiple push_str calls crossing threshold

### Run Command
`cargo test vm` (runs all VM tests including print functionality)
