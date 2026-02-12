# issue-05-profiling-cast-warning-fix: Fix cast_abs_to_unsigned Warning

## Description
Replace `.abs() as u64` pattern with `.unsigned_abs()` idiom in profiling.rs
line 79. This eliminates the clippy cast_abs_to_unsigned warning while
preserving identical semantics and type safety.

## Architecture Reference
Read architecture.md Section "Component 7: Clippy Warning Fix - profiling.rs
cast_abs_to_unsigned" (lines 500-541) for:
- Exact line location and transformation pattern
- Clippy warning name and verification command
- Contribution to total clippy warning fix count (12 total)

## Interface Contracts
- Implements: Single-line expression rewrite
```rust
// Before (line 79):
let diff = (sum as i64 - self.total_ns as i64).abs() as u64;
// After:
let diff = (sum as i64 - self.total_ns as i64).unsigned_abs();
```
- Exports: profiling.rs with cast_abs_to_unsigned warning eliminated
- Consumes: None (independent clippy fix)
- Consumed by: issue-13-final-validation (AC2 clippy verification)

## Isolation Context
- Available: Clean profiling.rs from repo baseline
- NOT available: Code changes from sibling issues (all Phase 1 parallel)
- Source of truth: architecture.md Component 7 (lines 500-541)

## Files
- **Modify**: `src/profiling.rs` (replace line 79)

## Dependencies
None (Phase 1 component - runs in parallel)

## Provides
- profiling.rs with cast_abs_to_unsigned warning eliminated
- Modern Rust idiom for absolute value to unsigned conversion

## Acceptance Criteria
- [ ] `cargo clippy --lib -- -D warnings 2>&1 | grep -c 'cast_abs_to_unsigned'` outputs 0
- [ ] `cargo build --lib 2>&1` exits with code 0 (compilation succeeds)
- [ ] Line 79 contains `.unsigned_abs()` instead of `.abs() as u64`

## Testing Strategy

### Test Files
- `src/profiling.rs`: Lines 128-210 contain existing unit tests that verify
  profiling functionality remains intact after change

### Test Categories
- **Unit tests**: Run existing `test_validate_timing_sum` to verify arithmetic
  unchanged
- **Functional tests**: Run all profiling tests to ensure timing calculations
  produce identical results
- **Edge cases**: Test with zero total_ns values (existing coverage)

### Run Command
`cargo test --lib profiling::tests`

## Verification Commands
- Build: `cargo build --lib 2>&1`
- Test: `cargo test --lib profiling::tests 2>&1`
- Check: `cargo clippy --lib -- -D warnings 2>&1 | grep cast_abs_to_unsigned || echo "PASS"`
