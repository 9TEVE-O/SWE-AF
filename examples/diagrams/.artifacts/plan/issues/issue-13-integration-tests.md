# issue-13-integration-tests: Create comprehensive end-to-end integration test suite

## Description
Implement integration tests that verify the complete CLI workflow using tempfile for isolated file I/O. Test all three commands (compile, preview, validate), error handling with correct exit codes, and SVG content verification.

## Architecture Reference
Read architecture.md Section "Component 9: Application Layer" and "Integration Tests" for:
- App interface: `compile()`, `preview()`, `validate()` method signatures
- Error exit code mapping: 1=syntax, 2=semantic, 3=I/O
- Integration test patterns using `std::process::Command` and `tempfile::TempDir`
- Test structure and verification strategies

## Interface Contracts
Tests invoke CLI via `std::process::Command`:
```rust
Command::new("cargo")
    .args(&["run", "--release", "--", "compile", input, "-o", output])
    .status()
```
- Verifies: exit codes, file existence, SVG/ASCII content, error messages on stderr

## Isolation Context
- Available: All completed modules (types, error, lexer, parser, validator, layout, svg, ascii, app, cli)
- NOT available: N/A (last issue in dependency chain)
- Source of truth: architecture.md "Integration Tests" section (lines 1491-1586)

## Files
- **Create**: `tests/integration.rs`
- **Create**: `tests/fixtures/simple.dsl`
- **Create**: `tests/fixtures/three_tier.dsl`
- **Create**: `tests/fixtures/invalid_syntax.dsl`

## Dependencies
- cli-module (provides: CLI binary entry point)
- app-module (provides: compile, preview, validate orchestration)
- svg-renderer (provides: SVG output generation)
- ascii-renderer (provides: ASCII output generation)

## Provides
- Complete integration test coverage for all PRD acceptance criteria
- End-to-end workflow verification using CLI binary
- Error handling validation with exit code checks
- Reusable DSL test fixtures for manual verification

## Acceptance Criteria
- [ ] tests/integration.rs compiles and all tests pass
- [ ] Test: compile valid DSL creates SVG file with `<svg` tag
- [ ] Test: SVG contains all node display names from input DSL
- [ ] Test: SVG contains all connection labels from input DSL
- [ ] Test: preview command outputs ASCII with Unicode box-drawing characters
- [ ] Test: validate command on valid DSL exits with code 0
- [ ] Test: validate command on syntax error exits with code 1 and prints error message
- [ ] Test: validate command on semantic error exits with code 2 and prints error message
- [ ] Test: compile with nonexistent input file exits with code 3
- [ ] tests/fixtures/ contains 3+ example DSL files
- [ ] `cargo test --test integration` exits 0

## Testing Strategy

### Test Files
- `tests/integration.rs`: All integration test functions using Command::new
- `tests/fixtures/simple.dsl`: Minimal 2-node diagram for basic compile/preview tests
- `tests/fixtures/three_tier.dsl`: Complex multi-node diagram for SVG content verification
- `tests/fixtures/invalid_syntax.dsl`: Malformed DSL for error handling tests

### Test Categories
- **Functional tests**: End-to-end compile workflow, preview ASCII output, validate command
- **Error handling tests**: Syntax error exit code 1, semantic error exit code 2, I/O error exit code 3
- **Content verification**: SVG contains node names, connection labels, valid XML structure
- **Edge cases**: Empty input, nonexistent files, invalid DSL syntax patterns

### Run Command
`cargo test --test integration`

## Verification Commands
- Build: `cargo build --release`
- Test: `cargo test --test integration`
- Check: `cargo test --test integration 2>&1 | grep -q "test result: ok"`
