# issue-10-smoke-test-core-components: Verify core components integrate correctly

## Description
Create integration test exercising the parsing and layout pipeline end-to-end. Verifies lexer → parser → validator → layout chain works for simple diagrams. Catches integration issues before rendering phase.

## Architecture Reference
Read architecture.md Section "Component Definitions" for interface signatures:
- Component 3 (Lexer Module): `Lexer::new()`, `tokenize()` → `Vec<PositionedToken>`
- Component 4 (Parser Module): `Parser::new()`, `parse()` → `Diagram`
- Component 5 (Validator Module): `Validator::validate(&Diagram)` → `Result<()>`
- Component 6 (Layout Module): `LayoutEngine::layout(&Diagram)` → `LayoutDiagram`

## Interface Contracts
- Implements: Integration test function `test_smoke_pipeline()`
- Exports: Verification that parsing pipeline works end-to-end
- Consumes: Lexer, Parser, Validator, LayoutEngine public APIs
- Consumed by: Final acceptance verification (issue-14)

## Isolation Context
- Available: lexer, parser, validator, layout modules (completed dependencies)
- NOT available: svg, ascii renderers (same-level siblings)
- Source of truth: architecture.md for module interfaces

## Files
- **Create**: `tests/smoke_test.rs`

## Dependencies
- issue-04 (lexer-module)
- issue-05 (parser-module)
- issue-06 (validator-module)
- issue-07 (layout-module)

## Provides
- Early integration verification before rendering phase
- Confirmation that parsing pipeline works end-to-end
- Foundation for full integration tests

## Acceptance Criteria
- [ ] `tests/smoke_test.rs` exists and compiles
- [ ] Test creates simple DSL with 2 nodes and 1 connection
- [ ] Test tokenizes with Lexer successfully
- [ ] Test parses to Diagram AST with Parser successfully
- [ ] Test validates with Validator successfully
- [ ] Test computes layout with LayoutEngine successfully
- [ ] LayoutDiagram contains 2 positioned nodes with valid coordinates
- [ ] LayoutDiagram contains 1 positioned connection
- [ ] `cargo test --test smoke_test` exits 0
- [ ] Test fails gracefully with clear error if any component fails

## Testing Strategy

### Test Files
- `tests/smoke_test.rs`: Single integration test exercising full pipeline

### Test Categories
- **Functional test**: End-to-end DSL → LayoutDiagram transformation
- **Integration test**: Verifies Lexer → Parser → Validator → Layout chain
- **Edge case validation**: Asserts positioned nodes have non-negative coordinates

### Run Command
`cargo test --test smoke_test`

## Verification Commands
- Build: `cargo build --tests`
- Test: `cargo test --test smoke_test`
- Check: `cargo test --test smoke_test -- --nocapture | grep -q "test result: ok"`
