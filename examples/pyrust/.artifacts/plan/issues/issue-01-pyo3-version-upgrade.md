# issue-01-pyo3-version-upgrade: Upgrade PyO3 Dependency from v0.20 to v0.22

## Description
Upgrade PyO3 dependency in Cargo.toml from version 0.20 to 0.22 to enable test execution on Python 3.14. This resolves the Python version incompatibility blocking `cargo test` execution.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section "Component 1: PyO3 Dependency Version Upgrade" for:
- Exact line location (Cargo.toml line 17 in `[dev-dependencies]`)
- Verification command using `cargo metadata`
- Error handling for version format validation

## Interface Contracts
- **Modifies**: `Cargo.toml` line 17 in `[dev-dependencies]` section
- **Before**: `pyo3 = { version = "0.20", features = ["auto-initialize"] }`
- **After**: `pyo3 = { version = "0.22", features = ["auto-initialize"] }`
- **Preserves**: `features = ["auto-initialize"]` array unchanged

## Isolation Context
- Available: None (foundational component - no dependencies)
- NOT available: All sibling issues (run first in Phase 1)
- Source of truth: architecture.md Component 1 for implementation steps

## Files
- **Modify**: `Cargo.toml` (line 17, `[dev-dependencies]` section)

## Dependencies
None (foundational component)

## Provides
- PyO3 v0.22 compatibility for Python 3.14 test execution
- Unblocked `cargo test` compilation

## Acceptance Criteria
- [ ] `grep 'pyo3.*version.*=' Cargo.toml | grep -E '(0\.2[2-9]|0\.[3-9][0-9]|[1-9]\.)' && echo PASS` exits with code 0
- [ ] `cargo metadata --format-version=1 2>/dev/null | jq -r '.packages[] | select(.name == "pyrust") | .dependencies[] | select(.name == "pyo3") | .req'` outputs `^0.22`
- [ ] `cargo build --lib 2>&1` exits with code 0 (compilation succeeds)

## Testing Strategy

### Test Files
No new test files - validation via cargo metadata and build

### Test Categories
- **Build validation**: Verify compilation succeeds with new PyO3 version
- **Metadata verification**: Confirm dependency version upgrade via cargo metadata
- **Edge cases**: Ensure TOML syntax remains valid, features preserved

### Run Command
```bash
cargo build --lib 2>&1 && cargo metadata --format-version=1 | jq -r '.packages[] | select(.name == "pyrust") | .dependencies[] | select(.name == "pyo3") | .req'
```

## Verification Commands
- Build: `cargo build --lib 2>&1`
- Test: `cargo metadata --format-version=1 | jq -r '.packages[] | select(.name == "pyrust") | .dependencies[] | select(.name == "pyo3") | .req'`
- Check: `grep 'pyo3.*version.*=' Cargo.toml | grep -E '(0\.2[2-9]|0\.[3-9][0-9]|[1-9]\.)' && echo PASS`
