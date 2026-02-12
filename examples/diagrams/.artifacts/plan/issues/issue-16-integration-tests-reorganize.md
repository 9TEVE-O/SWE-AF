# issue-16-integration-tests-reorganize: Consolidate Integration Tests

## Description
Create `tests/integration.rs` by consolidating existing integration tests from `test_app_integration.rs` and `smoke_test.rs`. This satisfies PRD AC10 which requires `cargo test --test integration` to pass. All functionality already exists - this is purely a reorganization to meet the naming convention specified in the PRD.

## Architecture Reference
Read architecture.md Section 9 (Application Layer) and the Testing Strategy section for:
- `App::compile()`, `App::preview()`, `App::validate()` signatures
- Integration test patterns covering full pipeline workflows
- Error handling patterns (DiagramError variants)

## Interface Contracts
- Implements: No new functionality
- Exports: `tests/integration.rs` test file
- Consumes: Existing test code from `test_app_integration.rs` and `smoke_test.rs`
- Consumed by: `cargo test --test integration` command (PRD AC10)

## Isolation Context
- Available: Complete `diagrams` crate (all modules: app, lexer, parser, validator, layout, svg, ascii, types, error)
- NOT available: None (this is final reorganization task)
- Source of truth: Existing tests in `test_app_integration.rs` and `smoke_test.rs`

## Files
- **Create**: `tests/integration.rs`
- **Reference**: `tests/test_app_integration.rs` (copy App-level integration tests)
- **Reference**: `tests/smoke_test.rs` (copy pipeline smoke tests)

## Dependencies
- cli-module (provides CLI entry point)
- app-module (provides App::compile, App::preview, App::validate)
- svg-renderer (provides SVG rendering for compile workflow)
- ascii-renderer (provides ASCII rendering for preview workflow)

## Provides
- `tests/integration.rs` file enabling `cargo test --test integration` to pass
- Complete integration test coverage (reorganized from existing 22 tests)
- Satisfaction of PRD AC10 acceptance criterion

## Acceptance Criteria
- [ ] File `tests/integration.rs` exists
- [ ] Running `cargo test --test integration` exits 0
- [ ] At least 10 integration tests present in `tests/integration.rs`
- [ ] Tests cover: compile workflow, preview workflow, validate workflow
- [ ] Tests cover: syntax errors, semantic errors, I/O errors
- [ ] All tests in `tests/integration.rs` pass

## Testing Strategy

### Test Files
- `tests/integration.rs`: Consolidates all integration tests from `test_app_integration.rs` (12 tests) and `smoke_test.rs` (12 tests)

### Test Categories
- **Compile workflow**: `test_app_compile_end_to_end`, `test_app_compile_overwrites_existing_file`, `test_app_empty_diagram_compiles_successfully`, `test_app_full_pipeline_with_multiple_nodes_and_connections`
- **Preview workflow**: `test_app_preview_returns_ascii_art`, `test_app_preview_handles_nonexistent_file`
- **Validate workflow**: `test_app_validate_accepts_valid_dsl`, `test_app_validate_rejects_invalid_syntax`, `test_app_validate_rejects_semantic_errors`
- **Error handling**: `test_app_compile_handles_nonexistent_input_file`, `test_app_compile_handles_unwritable_output_path`, `test_smoke_pipeline_handles_syntax_error`, `test_smoke_pipeline_handles_semantic_error`
- **Pipeline smoke tests**: `test_smoke_parsing_pipeline_simple_diagram`, `test_smoke_pipeline_nodes_only`, `test_smoke_pipeline_connection_without_label`, `test_smoke_pipeline_with_node_types`, `test_smoke_pipeline_multiple_connections`, `test_smoke_pipeline_empty_input`, `test_smoke_pipeline_lexer_error`, `test_smoke_pipeline_self_connection_error`, `test_smoke_pipeline_duplicate_node_error`

### Run Command
`cargo test --test integration`

## Verification Commands
- Build: `cargo build --release`
- Test: `cargo test --test integration`
- Check AC10: `cargo test --test integration && echo "PASS: AC10 satisfied"`
