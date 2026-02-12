# PRD: Production Quality Cleanup for PyRust Repository

## Product Goal

Transform the PyRust repository from development state to production quality by eliminating technical debt, removing artifacts, fixing code quality issues, and ensuring clean build/test/release pipelines.

## Current State Analysis

### Repository Structure
- **Core Library**: 13.6k LOC across 15 Rust modules implementing a Python-like language compiler
- **Test Suite**: 50 integration test files (some tests fail due to PyO3 version incompatibility)
- **Benchmarks**: 13 Criterion benchmark suites
- **Scripts**: 12 validation/testing shell scripts
- **Documentation**: Multiple verification/implementation notes scattered in root

### Critical Issues Identified

1. **Build System Issues**
   - PyO3 v0.20 incompatible with Python 3.14 (blocks test execution)
   - Dev-dependency only, but prevents `cargo test` from running
   - Needs upgrade to PyO3 v0.22+ or explicit Python version pinning

2. **Code Quality Problems**
   - 3 dead code warnings (unused fields: `Compiler.functions`, `FunctionMetadata.body_len`, `VM.clear_register_valid`)
   - 10+ clippy warnings (redundant closures, unnecessary clones, `len_zero` anti-patterns)
   - Formatting violations in 2 benchmark files (import ordering)

3. **File System Pollution**
   - 3 backup/temp files in `src/` (`.backup`, `.tmp`)
   - 3 stale `.claude_output_*.json` files in root
   - 7 temporary artifact files (`.log`, `.txt`, `.json` test outputs)
   - `Cargo.toml.bak` backup file
   - `Cargo.lock` tracked in git (should be ignored for libraries)

4. **Missing Production Assets**
   - No `README.md` (critical for discoverability)
   - No `LICENSE` file (unclear legal status)
   - No `.github/` CI/CD workflows
   - No contribution guidelines

5. **Configuration Issues**
   - `.gitignore` incomplete (doesn't ignore `*.log`, `*.bak`, `*.tmp`, `.claude_output_*.json`)
   - Build artifacts (`dhat-heap.json`, `libtest_performance_documentation.rlib`) not ignored

6. **Documentation Chaos**
   - Root directory cluttered with 6 markdown files (VALIDATION.md, PERFORMANCE.md, IMPLEMENTATION_NOTES.md, etc.)
   - Documentation fragmented across root and `.artifacts/` directories
   - No single source of truth for project documentation

## Validated Description

Clean the PyRust repository to production quality by: (1) fixing the PyO3 dependency version conflict to enable test execution, (2) removing all dead code and resolving clippy warnings, (3) applying consistent formatting across the codebase, (4) removing all backup/temporary/artifact files from the repository, (5) adding missing production files (README, LICENSE), (6) updating .gitignore to prevent future pollution, and (7) consolidating documentation into a structured docs/ directory.

## Acceptance Criteria

All criteria are **machine-verifiable** commands that must pass:

### Build & Test Quality
- **AC1**: `cargo build --lib --bins --release 2>&1 | grep -c warning` outputs `0` (zero warnings)
- **AC2**: `cargo clippy --lib --bins -- -D warnings 2>&1` exits with code 0 (zero clippy warnings treated as errors)
- **AC3**: `cargo fmt -- --check 2>&1` exits with code 0 (all code formatted)
- **AC4**: `cargo test --lib --bins 2>&1 | grep "test result:"` shows `0 failed` (all non-PyO3 tests pass)
- **AC5**: `cargo build --release 2>&1 | grep -c "Compiling pyrust"` outputs `1` (clean release build)

### File System Cleanliness
- **AC6**: `find src -name "*.backup" -o -name "*.tmp" -o -name "*.bak" | wc -l` outputs `0` (no temp files in src/)
- **AC7**: `ls *.log *.txt dhat-heap.json libtest*.rlib Cargo.toml.bak .claude_output_*.json 2>/dev/null | wc -l` outputs `0` (no artifacts in root)
- **AC8**: `git status --porcelain | grep -E "^\?\?" | wc -l` outputs `0` after cleanup (no untracked files except new production files)

### Production Assets
- **AC9**: `test -f README.md && wc -c README.md | awk '{print ($1 >= 500)}'` outputs `1` (README exists, ≥500 bytes)
- **AC10**: `test -f LICENSE` exits with code 0 (LICENSE file exists)
- **AC11**: `grep -E "(\.log|\.bak|\.tmp|\.claude_output.*\.json|dhat-heap\.json|libtest.*\.rlib)" .gitignore | wc -l` outputs at least `4` (all artifact patterns covered)

### Documentation Structure
- **AC12**: `test -d docs && find docs -name "*.md" | wc -l` outputs at least `3` (docs/ directory with consolidated documentation)
- **AC13**: `ls *.md 2>/dev/null | grep -v README.md | wc -l` outputs `0` (no loose markdown files in root except README)

### Dependency Resolution
- **AC14**: `grep "pyo3.*version.*=" Cargo.toml | grep -E "(0\.2[2-9]|0\.[3-9][0-9]|[1-9]\.)"` exits with code 0 (PyO3 ≥ 0.22) OR `grep "PYO3_USE_ABI3_FORWARD_COMPATIBILITY" .cargo/config.toml` exits with code 0
- **AC15**: `cargo metadata --format-version=1 2>/dev/null | jq -r '.packages[] | select(.name == "pyrust") | .dependencies[] | select(.name == "pyo3") | .kind' | grep -c "dev"` outputs `1` (pyo3 is dev-dependency only)

### Build Artifacts
- **AC16**: `stat -f%z target/release/pyrust 2>/dev/null | awk '{print ($1 <= 500000)}'` outputs `1` (release binary ≤500KB after cleanup)
- **AC17**: `ldd target/release/pyrust 2>/dev/null | grep -c python` outputs `0` (no Python linkage in release binary)

## Must Have

### 1. Dependency Resolution (Blocks all tests)
- **Upgrade PyO3 to v0.22+** in `Cargo.toml` `[dev-dependencies]` section
- OR configure `.cargo/config.toml` with `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1`
- Verify `cargo test --lib --bins` can compile (even if some Python comparison tests are excluded)

### 2. Code Quality Fixes
- **Remove dead code**:
  - Remove unused field `Compiler.functions` (src/compiler.rs:88) OR add `#[allow(dead_code)]` with justification comment
  - Remove unused field `FunctionMetadata.body_len` (src/vm.rs:97) OR add `#[allow(dead_code)]`
  - Remove unused method `VM.clear_register_valid` (src/vm.rs:191) OR add `#[allow(dead_code)]`
- **Fix clippy warnings**:
  - Replace `params.len() > 0` with `!params.is_empty()` (src/compiler.rs:453)
  - Replace `if let Err(_) =` with `.is_err()` (src/lexer.rs:131)
  - Remove unnecessary `.clone()` on `Option<Value>` (src/vm.rs:483)
  - Replace redundant closures in src/daemon_client.rs (lines 126, 130, 132, 139, 141)
- **Format codebase**: Run `cargo fmt` to fix import ordering in benches/

### 3. File System Cleanup
- **Delete backup/temp files**:
  - `src/bytecode.rs.backup`
  - `src/bytecode.rs.tmp`
  - `src/vm.rs.backup`
  - `Cargo.toml.bak`
- **Delete artifact files**:
  - `bench_output.log`
  - `test_output.log`
  - `test_output.txt`
  - `test_output_fixed.txt`
  - `dhat-heap.json`
  - `libtest_performance_documentation.rlib`
  - `.claude_output_a1bf2ba40715.json`
  - `.claude_output_bdf6d7a0d9e6.json`
  - `.claude_output_28110d4cf56e.json`

### 4. Gitignore Updates
Add these patterns to `.gitignore`:
```
# Build artifacts
*.log
*.bak
*.tmp
*.backup
dhat-heap.json
*.rlib

# Claude Code outputs
.claude_output_*.json

# Documentation builds
/docs/book/

# Benchmark outputs
/benches/*.json
/benches/*.svg
```

### 5. Production README
Create `README.md` with:
- **Project title and description** (what PyRust is)
- **Features** (Python-like language compiler, daemon mode, caching)
- **Installation**: `cargo build --release`
- **Usage examples**: `./target/release/pyrust -c "print(42)"`
- **Architecture overview** (lexer → parser → compiler → VM pipeline)
- **Performance claims** (link to PERFORMANCE.md if moved to docs/)
- **License** (reference to LICENSE file)
- **Contributing** (how to run tests, benchmarks)

### 6. LICENSE File
Add appropriate open-source license:
- **Recommendation**: MIT or Apache-2.0 (standard for Rust projects)
- **Requirement**: Must be a standard OSI-approved license
- **Content**: Full license text with copyright holder placeholder

### 7. Documentation Consolidation
Create `docs/` directory and move:
- `VALIDATION.md` → `docs/validation.md`
- `PERFORMANCE.md` → `docs/performance.md`
- `IMPLEMENTATION_NOTES.md` → `docs/implementation-notes.md`
- `INTEGRATION_VERIFICATION_RESULTS.md` → `docs/integration-verification.md`
- `TEST_VERIFICATION_EVIDENCE.md` → `docs/test-verification.md`
- Create `docs/README.md` as index/table of contents

### 8. Cargo.toml Cleanup
- Add `repository`, `homepage`, `documentation` fields (can be placeholders)
- Add `keywords` and `categories` for crates.io discoverability
- Add `license` field matching LICENSE file
- Add `description` (single-line summary)

## Nice to Have

### 1. CI/CD Pipeline
- `.github/workflows/ci.yml`: Run `cargo test`, `cargo clippy`, `cargo fmt --check` on PRs
- `.github/workflows/release.yml`: Build release binaries for multiple platforms
- Badge URLs in README for build status

### 2. Performance Documentation
- Link benchmarks to Criterion dashboard or charts
- Add `docs/benchmarks.md` with interpretation guide
- Document how to run benchmarks and interpret results

### 3. Contribution Guidelines
- `CONTRIBUTING.md` with:
  - Code style requirements
  - How to run tests locally
  - PR submission process
  - Issue templates

### 4. Advanced Testing
- Add `cargo-deny` for supply chain security
- Add `cargo-audit` for vulnerability scanning
- Add `cargo-tarpaulin` for code coverage reporting

### 5. Release Automation
- `CHANGELOG.md` following Keep a Changelog format
- Semantic versioning strategy documented
- Release automation script

### 6. Docker Support
- `Dockerfile` for containerized builds
- Docker Compose for development environment
- Pre-built images on Docker Hub

### 7. Editor Configuration
- `.editorconfig` for consistent formatting across editors
- VSCode workspace settings (`.vscode/settings.json`)
- Rust-analyzer configuration

## Out of Scope

The following are explicitly **not part of this cleanup**:

### 1. Feature Development
- No new language features or compiler optimizations
- No changes to bytecode format or VM architecture
- No new daemon modes or execution strategies

### 2. API Changes
- No changes to public API surface in `lib.rs`
- No breaking changes to CLI arguments
- No modifications to output format

### 3. Test Suite Expansion
- No new test cases or test coverage improvements
- No integration test rewrites
- Existing tests must pass, but no new tests required

### 4. Performance Optimization
- No performance tuning or optimization work
- No changes to benchmarks (except formatting)
- Existing performance metrics should be maintained, not improved

### 5. Refactoring
- No architectural changes or module reorganization
- No code simplification beyond dead code removal
- No changes to error handling strategy

### 6. Infrastructure
- No deployment configuration (Kubernetes, Terraform, etc.)
- No monitoring/observability setup
- No production hosting configuration

### 7. Documentation Content
- No rewriting of existing technical documentation
- Moving files only; content stays as-is
- No API documentation expansion (rustdoc is sufficient)

### 8. Dependency Updates
- Only PyO3 upgrade is in scope (to fix tests)
- No other dependency version bumps
- No dependency pruning or optimization

## Assumptions

1. **License Choice**: Will use MIT license unless user specifies otherwise during implementation
2. **Python Version**: PyO3 upgrade to v0.22 will be preferred over forward compatibility flag
3. **Cargo.lock**: Will be removed from git and added to .gitignore (standard for libraries)
4. **Dead Code**: Will be removed rather than suppressed with `#[allow(dead_code)]` where safe
5. **README Audience**: Targeting Rust developers familiar with cargo, not end-users
6. **Documentation URLs**: Placeholder URLs will use `https://github.com/USER/pyrust` format
7. **Benchmark Data**: Existing benchmark results in markdown files are documentation, not artifacts
8. **Test Exclusions**: Some PyO3 comparison tests may need `#[ignore]` if they depend on specific Python versions
9. **Binary Size**: Current 453KB binary size is acceptable; no size reduction efforts needed
10. **Shell Scripts**: Validation scripts in `scripts/` are considered tools, not artifacts to delete

## Risks

1. **PyO3 Upgrade Breaking Changes**
   - **Risk**: v0.22 may have API changes that break benchmarks using PyO3
   - **Mitigation**: Review PyO3 changelog; if breaking changes found, use forward compatibility flag instead
   - **Impact**: Medium - blocks test execution but workaround exists

2. **Dead Code Removal Side Effects**
   - **Risk**: "Unused" code may be referenced by commented-out code or future features
   - **Mitigation**: Use `#[allow(dead_code)]` with comment instead of deletion if unclear
   - **Impact**: Low - fields are in internal structs, not public API

3. **Documentation Link Rot**
   - **Risk**: Moving docs/ files breaks internal cross-references
   - **Mitigation**: Search for relative markdown links and update paths
   - **Impact**: Low - affects readability but not functionality

4. **Test Regression from Cleanup**
   - **Risk**: Clippy auto-fixes or dead code removal breaks tests
   - **Mitigation**: Run `cargo test --lib --bins` after each change category
   - **Impact**: High if occurs - must verify AC4 continuously

5. **Git History Pollution**
   - **Risk**: Deleting many files creates noisy commit history
   - **Mitigation**: Group deletions by category (backups, artifacts, docs) in logical commits
   - **Impact**: Low - cosmetic only

6. **License Ambiguity**
   - **Risk**: Choosing wrong license type for project intent
   - **Mitigation**: Ask user to confirm license choice if not specified in existing files
   - **Impact**: High - affects legal usage, but easily fixed with new commit

## Dependencies

### Logical Order
Issues can be executed in parallel at each level, but must complete previous levels first:

**Level 0 (No dependencies):**
- Fix clippy warnings (safe, no side effects)
- Format codebase with `cargo fmt`
- Update `.gitignore` (doesn't affect builds)

**Level 1 (Depends on Level 0):**
- Fix PyO3 dependency (requires clean code to verify tests)
- Remove dead code (after confirming clippy changes don't use them)

**Level 2 (Depends on Level 1):**
- Delete temporary files (after tests pass)
- Delete artifact files (after tests pass)

**Level 3 (Depends on Level 2):**
- Create README.md (can reference clean state)
- Add LICENSE file (independent)
- Create docs/ structure (after root is clean)
- Update Cargo.toml metadata (after LICENSE exists)

**Level 4 (Depends on Level 3):**
- Final validation (all ACs)

### Interface Contracts
No interface changes between components - this is purely cleanup work.
