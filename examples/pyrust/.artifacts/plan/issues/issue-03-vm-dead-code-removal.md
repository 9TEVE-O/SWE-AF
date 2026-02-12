# issue-03-vm-dead-code-removal: Remove Unused body_len Field and clear_register_valid Method

## Description
Remove unused `body_len` field from `FunctionMetadata` struct (vm.rs line 97), its initialization site (line 365), and the unused `clear_register_valid` method (lines 191-195). This eliminates 2 dead code warnings and improves code quality per PRD requirements.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section "Component 3: Dead Code Removal - vm.rs body_len and clear_register_valid" for:
- Pre-implementation grep search strategy for locating all `body_len` usages
- Transformation rules for struct definition, initialization, and pattern matching
- Method removal specification for `clear_register_valid`
- Verification commands for confirming warning elimination

## Interface Contracts
- **Removes from struct**: `body_len: usize` field at line 97
- **Removes from initialization**: `body_len: *body_len,` assignment at line 365
- **Removes method**: `clear_register_valid` method definition (lines 191-195)
- **Preserves**: All test code using body_len in DefineFunction instruction literals (tests only)

## Isolation Context
- Available: None (no dependencies)
- NOT available: Code from sibling issues (compiler-dead-code-removal, daemon-client-redundant-closures)
- Source of truth: architecture document at path above

## Files
- **Modify**: `src/vm.rs` (lines 97, 191-195, 365)

## Dependencies
None

## Provides
- FunctionMetadata struct with unused body_len field removed
- VM implementation with unused clear_register_valid method removed
- Elimination of two dead code warnings

## Acceptance Criteria
- [ ] `cargo build --lib 2>&1 | grep -c "field.*body_len.*never read"` outputs 0
- [ ] `cargo build --lib 2>&1 | grep -c "method.*clear_register_valid.*never used"` outputs 0
- [ ] `cargo build --lib 2>&1` exits with code 0 (compilation succeeds)

## Testing Strategy

### Test Files
- `src/vm.rs`: Contains 35+ unit tests at bottom of file that reference body_len in DefineFunction instruction literals (test data only, not production code)

### Test Categories
- **Unit tests**: All existing VM unit tests must continue to pass (tests use body_len in DefineFunction instruction construction but don't read FunctionMetadata.body_len field)
- **Functional tests**: VM execution tests verify that function calls still work after field removal
- **Edge cases**: Tests at lines 974 and 1627 explicitly assert `func.body_len` - these lines MUST be removed

### Run Command
`cargo test --lib vm::tests`

## Verification Commands
- Build: `cargo build --lib 2>&1`
- Test: `cargo test --lib vm::tests 2>&1`
- Check: `cargo build --lib 2>&1 | grep -E "(body_len|clear_register_valid)" | wc -l` (expect: 0)
