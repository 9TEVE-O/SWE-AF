# issue-01-project-scaffold: Initialize Rust project with Cargo scaffolding and dependencies

## Description
Create the foundational Rust project structure with Cargo.toml, dependency specifications, and release optimizations. This establishes the build system required by all other modules, enabling parallel development of parsing, layout, and rendering streams.

## Architecture Reference
This issue establishes the project structure described in Architecture Section "External Dependencies" and "File Structure". No specific component implementation — pure scaffolding only.

## Interface Contracts
- Implements: N/A (foundation layer, no code interfaces)
- Exports: Build system configuration, project structure, dependency resolution
- Consumes: Nothing (root dependency)
- Consumed by: All subsequent issues (types-module, error-module, etc.)

## Isolation Context
- Available: Empty repository (greenfield project)
- NOT available: No modules exist yet
- Source of truth: PRD AC1 requirements, Architecture "External Dependencies" section

## Files
- **Create**: `Cargo.toml` (with package metadata, dependencies, dev-dependencies, release profile)
- **Create**: `src/main.rs` (minimal stub: `fn main() { println!("diagrams"); }`)
- **Create**: `src/lib.rs` (empty file for future module exports)

## Dependencies
None (root issue)

## Provides
- Cargo.toml with complete dependency specification (clap, insta, tempfile)
- Standard Rust project structure (src/, tests/ directories initialized)
- Build system configuration with release optimizations (lto, strip, codegen-units)

## Acceptance Criteria
- [ ] `cargo build --release` exits 0
- [ ] `cargo fmt --check` exits 0
- [ ] `cargo clippy -- -D warnings` exits 0
- [ ] `test -f Cargo.toml` passes
- [ ] `test -d src/` passes
- [ ] Cargo.toml contains `[package]` with name="diagrams", edition="2021", rust-version="1.70"
- [ ] Cargo.toml contains clap dependency with derive feature
- [ ] Cargo.toml contains dev-dependencies: insta and tempfile
- [ ] Cargo.toml contains `[profile.release]` with lto=true, strip=true, codegen-units=1

## Testing Strategy

### Test Files
- No test files required (scaffolding verification only)

### Test Categories
- **Build verification**: Ensure Cargo.toml is valid and project compiles
- **Lint compliance**: Verify clippy and rustfmt configurations work
- **Dependency resolution**: Confirm all dependencies download and link correctly

### Run Command
```bash
cargo build --release && cargo clippy -- -D warnings && cargo fmt --check
```

## Verification Commands
- Build: `cargo build --release`
- Test: `cargo test --all` (will pass with no tests)
- Check: `cargo fmt --check && cargo clippy -- -D warnings`
