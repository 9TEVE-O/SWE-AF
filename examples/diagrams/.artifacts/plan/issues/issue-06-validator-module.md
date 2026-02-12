# issue-06-validator-module: Implement semantic validation for AST correctness

## Description
Create src/validator.rs with Validator that performs semantic checks on Diagram AST. Verify all connection endpoints reference defined nodes, no duplicate node identifiers, and no self-connections. Return SemanticError variants with position information when validation fails.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-diagrams/.artifacts/plan/architecture.md` Section 5 (Component 5: Parser - Validator Module) for:
- Validator struct definition and public interface
- Three validation check functions: check_duplicate_nodes, check_undefined_connections, check_self_connections
- HashMap and HashSet usage patterns for efficient checking
- Complete implementation details (lines 562-644)

## Interface Contracts
```rust
// Implements:
pub struct Validator;
impl Validator {
    pub fn validate(diagram: &Diagram) -> Result<(), DiagramError>;
}
```

- **Exports**: Validator struct with validate() static method
- **Consumes**: Diagram (from types-module), DiagramError and SemanticError (from error-module)
- **Consumed by**: app-module (orchestrates validation in pipeline)

## Isolation Context
- **Available**: types-module (Diagram, Node, Connection), error-module (DiagramError, SemanticError)
- **NOT available**: lexer, parser, layout (same-level or later modules)
- **Source of truth**: Architecture document Section 5

## Files
- **Create**: `src/validator.rs`
- **Modify**: `src/main.rs` (add `mod validator;`)

## Dependencies
- issue-02-types-module (provides: Diagram, Node, Connection types)
- issue-03-error-module (provides: DiagramError, SemanticError variants)

## Provides
- Validator struct with validate() method
- Semantic validation: undefined node detection
- Semantic validation: duplicate node detection
- Semantic validation: self-connection detection

## Acceptance Criteria
- [ ] src/validator.rs exists and compiles
- [ ] Validator::validate(diagram: &Diagram) returns Result<(), DiagramError>
- [ ] Validator detects undefined nodes in connections and returns SemanticError::UndefinedNode
- [ ] Validator detects duplicate node identifiers and returns SemanticError::DuplicateNode with both positions
- [ ] Validator detects self-connections and returns SemanticError::SelfConnection
- [ ] Valid diagrams pass validation without errors
- [ ] At least 5 unit tests pass covering: valid diagram, undefined source, undefined target, duplicate node, self-connection

## Testing Strategy

### Test Files
- `src/validator.rs`: Unit tests in #[cfg(test)] module

### Test Categories
- **Unit tests**:
  - `test_validate_success`: Valid diagram with nodes and connections passes
  - `test_error_undefined_source`: Connection with undefined source node triggers SemanticError::UndefinedNode
  - `test_error_undefined_target`: Connection with undefined target node triggers SemanticError::UndefinedNode
  - `test_error_duplicate_node`: Duplicate node IDs trigger SemanticError::DuplicateNode with both positions
  - `test_error_self_connection`: Self-connection triggers SemanticError::SelfConnection

- **Functional tests**: Validator returns correct SemanticError variant for each error type
- **Edge cases**: Empty diagram (valid), diagram with only nodes (valid), diagram with only connections (invalid)

### Run Command
`cargo test --lib validator`

## Verification Commands
- Build: `cargo build`
- Test: `cargo test --lib validator`
- Check: `cargo test --lib validator -- --list | grep -c 'test' | awk '{exit !($1 >= 5)}'`
