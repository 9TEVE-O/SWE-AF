# Product Requirements Document: Diagrams-as-Code CLI Tool

## Product Vision

A Rust-based CLI tool that transforms a custom DSL into SVG architecture diagrams with an ASCII terminal preview mode. Developers describe system architectures in a text-based DSL, compile to SVG for documentation, and preview in the terminal during development.

## Current State Analysis

**Repository Status**: Empty repository (greenfield project)
- No Rust project structure exists
- No source files present
- Only `.git` and `.artifacts` directories

**Delta Definition**: Build entire CLI tool from scratch including:
- Rust project scaffolding (Cargo.toml, src/, tests/)
- DSL parser and lexer
- SVG generator
- ASCII renderer for terminal preview
- CLI interface with subcommands

## Validated Product Description

A command-line tool that accepts a custom DSL for defining architecture diagrams, compiles it to production-quality SVG output, and provides an ASCII-art preview mode for rapid iteration in the terminal. The DSL supports nodes (services, databases, external systems), connections with labels, and layout hints. The tool validates DSL syntax, reports meaningful errors, and generates clean, scalable SVG graphics suitable for embedding in documentation.

---

## Acceptance Criteria (Machine-Verifiable)

### AC1: Project Structure and Build System
```bash
# PASS if all commands exit 0
cargo build --release
cargo test --all
cargo clippy -- -D warnings
cargo fmt -- --check
test -f Cargo.toml
test -d src/
test -f src/main.rs
```

### AC2: CLI Interface Exists with Required Subcommands
```bash
# PASS if all commands exit 0 and output contains expected text
cargo build --release
./target/release/diagrams --help | grep -q "compile"
./target/release/diagrams --help | grep -q "preview"
./target/release/diagrams compile --help | grep -q "output"
./target/release/diagrams preview --help | grep -q "input"
```

### AC3: DSL Compilation to SVG
```bash
# PASS if command exits 0 and output file is valid SVG
echo 'node "API" as api
node "DB" as db
api -> db : "SQL query"' > /tmp/test_diagram.dsl

cargo run --release -- compile /tmp/test_diagram.dsl -o /tmp/output.svg
test -f /tmp/output.svg
head -1 /tmp/output.svg | grep -q "<svg"
xmllint --noout /tmp/output.svg  # validates XML structure
```

### AC4: ASCII Preview Mode Renders to Terminal
```bash
# PASS if command exits 0 and stdout contains box-drawing characters
echo 'node "API" as api
node "DB" as db
api -> db : "query"' > /tmp/test_diagram.dsl

cargo run --release -- preview /tmp/test_diagram.dsl | grep -qE '[\u2500-\u257F]'
```

### AC5: DSL Syntax Validation and Error Reporting
```bash
# PASS if command exits non-zero and stderr contains meaningful error
echo 'invalid syntax here' > /tmp/invalid.dsl

cargo run --release -- compile /tmp/invalid.dsl -o /tmp/out.svg 2>&1 | grep -qi "syntax error"
test $? -eq 0  # grep found error message

# Verify it exits non-zero
! cargo run --release -- compile /tmp/invalid.dsl -o /tmp/out.svg
```

### AC6: SVG Output Contains All DSL Elements
```bash
# PASS if SVG contains nodes and connections defined in DSL
echo 'node "Service A" as svc_a
node "Service B" as svc_b
svc_a -> svc_b : "HTTP"' > /tmp/test.dsl

cargo run --release -- compile /tmp/test.dsl -o /tmp/test.svg
grep -q "Service A" /tmp/test.svg
grep -q "Service B" /tmp/test.svg
grep -q "HTTP" /tmp/test.svg
```

### AC7: Performance - Compilation Completes in <1s for 100-node diagram
```bash
# Generate 100-node DSL file
for i in {1..100}; do
  echo "node \"Node$i\" as n$i"
done > /tmp/large.dsl
for i in {1..99}; do
  j=$((i+1))
  echo "n$i -> n$j"
done >> /tmp/large.dsl

# PASS if mean execution time < 1.0 second
hyperfine --warmup 3 --runs 10 \
  'cargo run --release -- compile /tmp/large.dsl -o /tmp/large.svg' \
  --export-json /tmp/perf.json

mean=$(jq '.results[0].mean' /tmp/perf.json)
awk -v m="$mean" 'BEGIN {exit !(m < 1.0)}'
```

### AC8: Binary Size Constraint
```bash
# PASS if release binary is under 10MB
cargo build --release
size=$(stat -f%z target/release/diagrams)
test "$size" -lt 10485760  # 10MB in bytes
```

### AC9: Unit Test Coverage for Parser
```bash
# PASS if parser tests exist and pass
cargo test --lib parser 2>&1 | grep -q "test result: ok"
# Verify at least 5 parser test cases exist
test $(cargo test --lib parser -- --list | grep -c "test") -ge 5
```

### AC10: Integration Tests for End-to-End Workflow
```bash
# PASS if integration test suite passes
cargo test --test integration
test $? -eq 0
```

### AC11: Zero Unsafe Rust Code
```bash
# PASS if no unsafe blocks found in src/
! grep -r "unsafe" src/ --include="*.rs"
```

### AC12: Documentation Comments on Public API
```bash
# PASS if cargo doc builds without warnings
cargo doc --no-deps 2>&1 | grep -q "Documenting diagrams"
! cargo doc --no-deps 2>&1 | grep -i "warning"
```

---

## Must-Have Features

### Core DSL Syntax
1. **Node Declaration**: `node "Display Name" as identifier`
   - Supports alphanumeric identifiers
   - Display names can contain spaces and special characters
2. **Connection Declaration**: `id1 -> id2 : "label"`
   - Directional arrows (->)
   - Optional label text
3. **Node Types**: `node "Name" as id [type: service]`
   - Types: service, database, external, queue
   - Type determines visual styling in SVG
4. **Comments**: Lines starting with `#` are ignored

### CLI Commands
1. **compile**: `diagrams compile <input.dsl> -o <output.svg>`
   - Parses DSL, generates SVG, writes to file
   - Returns exit code 0 on success, non-zero on error
2. **preview**: `diagrams preview <input.dsl>`
   - Renders ASCII representation to stdout
   - Uses box-drawing Unicode characters
3. **validate**: `diagrams validate <input.dsl>`
   - Checks syntax without generating output
   - Reports all errors found

### SVG Output Requirements
1. **Valid SVG XML**: Well-formed, passes xmllint validation
2. **Scalable**: Uses viewBox for resolution independence
3. **Readable**: Font sizes and spacing suitable for documentation
4. **Node Styling**: Distinct visual styles per node type (rectangles for services, cylinders for databases)
5. **Arrow Rendering**: Directional arrows with labels positioned clearly

### ASCII Preview Requirements
1. **Box-Drawing Characters**: Use Unicode U+2500-U+257F range
2. **Node Representation**: ASCII boxes with labels inside
3. **Connection Representation**: Lines and arrows between nodes
4. **Terminal Fit**: Automatically scales to fit typical 80x24 or larger terminals

### Error Handling
1. **Syntax Errors**: Report line number and character position
2. **Semantic Errors**: Undefined identifiers in connections
3. **File I/O Errors**: Clear messages for missing input or unwritable output
4. **Exit Codes**: 0=success, 1=syntax error, 2=semantic error, 3=I/O error

### Testing Infrastructure
1. **Unit Tests**: All parser, layout, and rendering modules
2. **Integration Tests**: Full compile and preview workflows
3. **Fixture Files**: Example DSL files in `tests/fixtures/`
4. **Snapshot Testing**: SVG output validation against golden files

---

## Nice-to-Have Features

1. **Auto-Layout Algorithms**: Hierarchical or force-directed graph layouts (current: simple left-to-right)
2. **Color Customization**: DSL syntax for node/arrow colors
3. **PNG Export**: `diagrams compile input.dsl -o output.png --format png`
4. **Interactive Mode**: `diagrams edit input.dsl` with live preview
5. **Syntax Highlighting**: Export VSCode/Sublime syntax definition files
6. **Multi-File Support**: Import/include statements for modular diagrams
7. **Style Themes**: Pre-defined color schemes (light, dark, high-contrast)
8. **Watch Mode**: `diagrams watch input.dsl -o output.svg` auto-regenerates on file changes
9. **LSP Server**: Language server for IDE integration with autocomplete
10. **HTML Export**: Standalone HTML with embedded SVG and interactivity

---

## Out of Scope

1. **GUI Editor**: No graphical drag-and-drop interface
2. **Cloud Storage**: No built-in integration with S3, Dropbox, etc.
3. **Version Control**: No built-in diff/merge tools for DSL files (use git)
4. **Animation**: No SVG animations or transitions
5. **3D Diagrams**: Only 2D layouts
6. **Database Schema Import**: No automatic generation from SQL/ORM definitions
7. **Real-Time Collaboration**: No multi-user editing features
8. **Web API**: No HTTP server mode (CLI only)
9. **PDF Export**: SVG only (users can convert with external tools)
10. **Undo/Redo**: No stateful editing session (DSL files are the source of truth)
11. **Internationalization**: Error messages in English only
12. **Plugin System**: No external plugin loading mechanism
13. **Diagram Libraries**: No pre-built component libraries or templates

---

## Assumptions

1. **Target Platform**: Linux and macOS (x86_64 and ARM64); Windows support is best-effort
2. **Rust Toolchain**: rustc >= 1.70, stable channel
3. **Terminal Support**: Target terminals support Unicode box-drawing characters (UTF-8 locale)
4. **SVG Viewers**: Users have tools to view SVG (browsers, documentation platforms)
5. **Input File Size**: DSL files under 10MB; larger files may exhaust memory
6. **Node Count**: Diagrams with <1000 nodes perform acceptably; larger graphs may render slowly
7. **DSL Evolution**: Breaking changes to DSL syntax are acceptable pre-1.0 release
8. **No External Data**: DSL files are self-contained; no network requests during compilation
9. **Filesystem Access**: CLI has read access to input files and write access to output directories
10. **Error Message Language**: English is the universal language for error messages
11. **Layout Algorithm**: Simple auto-layout is sufficient; users can manually adjust node positions in DSL if needed
12. **Dependency Philosophy**: Minimize external crates; prefer std library where reasonable

---

## Risks and Mitigations

### Risk 1: DSL Syntax Ambiguity
**Impact**: Parser cannot handle edge cases (e.g., quotes in labels, special characters in IDs)
**Mitigation**: Define grammar formally in EBNF notation in docs; use fuzzing tests to discover edge cases early

### Risk 2: SVG Rendering Inconsistencies
**Impact**: Generated SVGs appear differently across viewers (Chrome, Firefox, Inkscape)
**Mitigation**: Use SVG 1.1 spec strictly; test output in multiple viewers; avoid vendor-specific features

### Risk 3: Layout Algorithm Naive
**Impact**: ASCII preview and SVG layouts overlap nodes or have poor spacing for complex graphs
**Mitigation**: Start with simple left-to-right layout; document limitation; add auto-layout as nice-to-have Phase 2

### Risk 4: Performance Degrades with Large Graphs
**Impact**: >100 nodes cause compilation to exceed 1s, frustrating users
**Mitigation**: AC7 enforces <1s for 100 nodes; if fails, profile and optimize parser/renderer hot paths

### Risk 5: Unicode Rendering Failures in Terminals
**Impact**: ASCII preview displays garbage characters on misconfigured terminals
**Mitigation**: Detect locale; if not UTF-8, print warning and fall back to ASCII-only mode (-, |, +)

### Risk 6: Dependency Bloat
**Impact**: Binary size exceeds 10MB, making distribution cumbersome
**Mitigation**: AC8 enforces 10MB limit; audit dependencies regularly; prefer lightweight crates; consider static linking optimizations

---

## Dependencies (Technical Context)

This PRD produces a dependency graph with three major parallel streams:

**Stream A: DSL Parsing**
- Lexer → Parser → AST definition → Semantic validator

**Stream B: SVG Rendering**
- SVG structure generator → Node renderer → Connection renderer → File writer

**Stream C: ASCII Rendering**
- Layout calculator → Box-drawing renderer → Terminal output formatter

**Convergence Point**: CLI command dispatcher that invokes Stream A, then either Stream B or C

Agents working on Stream A, B, and C can execute in parallel once core types are defined.

---

## Success Metrics (Machine-Verifiable)

1. **All Acceptance Criteria Pass**: `cargo test --all && bash .artifacts/verify_all_acs.sh` exits 0
2. **Binary Builds**: `cargo build --release` exits 0
3. **Clippy Clean**: `cargo clippy -- -D warnings` exits 0
4. **Formatted Code**: `cargo fmt -- --check` exits 0
5. **Documentation Builds**: `cargo doc --no-deps` exits 0 without warnings
6. **Performance Target**: 100-node compilation <1s (AC7)
7. **Binary Size Target**: <10MB release binary (AC8)

---

## Execution Notes for Autonomous Agents

- **No Temporal Constraints**: This PRD defines WHAT must exist, not WHEN it will be delivered
- **Parallel Work Streams**: Lexer/parser, SVG renderer, and ASCII renderer can be built concurrently once core types (AST, Node, Connection) are defined
- **Interface Contracts**: See "Dependencies" section for required types and function signatures
- **Verification**: Every acceptance criterion maps to a shell command; no human judgment required
- **Scope Creep Prevention**: If a feature is not in "Must-Have" or "Nice-to-Have", reject it
- **Assumption Constraints**: If an assumption is violated (e.g., Rust <1.70), document and propose PRD amendment

---

## Appendix: Example DSL Syntax

```dsl
# Simple three-tier architecture
node "Web Frontend" as web [type: service]
node "API Gateway" as api [type: service]
node "PostgreSQL" as db [type: database]
node "Redis Cache" as cache [type: database]
node "External Auth" as auth [type: external]

web -> api : "HTTPS"
api -> db : "SQL queries"
api -> cache : "Cache lookups"
api -> auth : "OAuth2"
```

**Expected SVG Output**: Four rectangular nodes (web, api, auth as services), two cylindrical nodes (db, cache as databases), with labeled directional arrows connecting them.

**Expected ASCII Preview**:
```
┌──────────────┐       ┌─────────────┐
│ Web Frontend │──────>│ API Gateway │
└──────────────┘       └─────────────┘
                              │
                 ┌────────────┼────────────┐
                 │            │            │
                 v            v            v
          ┌──────────┐  ┌─────────┐  ┌──────────┐
          │PostgreSQL│  │  Redis  │  │External  │
          │          │  │  Cache  │  │   Auth   │
          └──────────┘  └─────────┘  └──────────┘
```

---

**END OF PRD**
