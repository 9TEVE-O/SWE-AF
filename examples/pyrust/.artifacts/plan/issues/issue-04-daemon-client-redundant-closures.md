# issue-04-daemon-client-redundant-closures: Fix Redundant Closure Warnings

## Description
Replace 8 redundant closure patterns in daemon_client.rs with direct function pointers to satisfy clippy redundant_closure lint. Transform `.map_err(|e| ErrorVariant(e))` to `.map_err(ErrorVariant)` for idiomatic Rust error handling.

## Architecture Reference
Read `architecture.md` Section "Component 6: Clippy Warning Fixes - daemon_client.rs Redundant Closures" for:
- Exact line numbers (126, 130, 132, 139, 141, 146, 167, 209)
- Complete transformation patterns for each closure site
- Before/after code examples showing DaemonClientError variants

## Interface Contracts
- Pattern: `.map_err(|e| DaemonClientError::XXX(e))` → `.map_err(DaemonClientError::XXX)`
- Applies to 8 occurrences in execute_via_daemon() and stop_daemon() methods
- Error variants: ConnectionFailed, SocketConfig, WriteFailed, ReadFailed, PidFileRead

## Isolation Context
- Available: All Phase 1 prerequisite components (code formatting, other clippy fixes)
- NOT available: None (no same-level dependencies)
- Source of truth: architecture.md Component 6 interface specification

## Files
- **Modify**: `src/daemon_client.rs` (lines 126, 130, 132, 139, 141, 146, 167, 209)

## Dependencies
None (runs in parallel with Components 1, 2, 3, 7, 8, 9)

## Provides
- daemon_client.rs with 8 redundant closures eliminated
- Idiomatic Rust error handling patterns

## Acceptance Criteria
- [ ] `cargo clippy --lib -- -D warnings 2>&1 | grep -c 'redundant_closure'` outputs 0
- [ ] `cargo build --lib 2>&1` exits with code 0 (compilation succeeds)
- [ ] All 8 occurrences transformed: ConnectionFailed (line 126), SocketConfig (130, 132), WriteFailed (139, 141), ReadFailed (146, 167), PidFileRead (209)

## Testing Strategy

### Test Files
- `src/daemon_client.rs`: Unit tests verify error enum Display implementations remain correct

### Test Categories
- **Compilation test**: Verify all 8 transformations compile without errors
- **Clippy verification**: Confirm redundant_closure warnings eliminated
- **Functional preservation**: Existing daemon_client tests must pass unchanged

### Run Command
```bash
cargo clippy --lib -- -D warnings 2>&1
cargo test --lib daemon_client 2>&1
```

## Verification Commands
- Build: `cargo build --lib 2>&1 && echo "SUCCESS" || echo "FAILED"`
- Clippy: `cargo clippy --lib -- -D warnings 2>&1 | grep -c redundant_closure`
- Check: Verify output is 0 (all 8 warnings eliminated)
