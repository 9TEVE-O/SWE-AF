# issue-03-error-module: Implement comprehensive error types with Display formatting

## Description
Define all error types in src/error.rs: DiagramError enum, SyntaxError, SemanticError enum with variants, IoError. Implement Display and Error traits. Provides exit code mapping (1=syntax, 2=semantic, 3=I/O) and detailed error formatting with source position tracking for human-readable output.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-diagrams/.artifacts/plan/architecture.md` Section "Component 2: Foundation - Error Module" (lines 188-298) for:
- Complete type definitions (DiagramError, SyntaxError, SemanticError, IoError)
- exit_code() and format_detailed() method implementations
- Display and Error trait implementations
- From<io::Error> conversion logic

## Interface Contracts
```rust
// Implements (signature only, see architecture for implementation):
pub enum DiagramError { Syntax(SyntaxError), Semantic(SemanticError), Io(IoError) }
impl DiagramError {
    pub fn exit_code(&self) -> i32 { /* 1, 2, or 3 */ }
    pub fn format_detailed(&self) -> String { /* line/column info */ }
}
pub type Result<T> = std::result::Result<T, DiagramError>;
```

- **Exports**: Complete error type hierarchy, Result<T> alias, exit code mapping
- **Consumes**: SourcePosition from types-module
- **Consumed by**: lexer-module, parser-module, validator-module, app-module

## Isolation Context
- **Available**: types-module (issue-02, provides SourcePosition)
- **NOT available**: lexer, parser, validator (same-level siblings)
- **Source of truth**: architecture.md lines 188-298

## Files
- **Create**: `src/error.rs`
- **Modify**: `src/main.rs` (add `mod error;`)

## Dependencies
- issue-02 (provides: SourcePosition type)

## Provides
- Complete error type hierarchy (DiagramError, SyntaxError, SemanticError, IoError)
- Error formatting methods with source position tracking
- Exit code mapping (1=syntax, 2=semantic, 3=I/O)
- Result<T> type alias for error propagation

## Acceptance Criteria
- [ ] src/error.rs exists and compiles
- [ ] DiagramError enum has variants: Syntax(SyntaxError), Semantic(SemanticError), Io(IoError)
- [ ] SyntaxError contains message and position fields
- [ ] SemanticError enum has variants: UndefinedNode, DuplicateNode, SelfConnection with correct fields
- [ ] DiagramError::exit_code() returns correct codes: 1 for Syntax, 2 for Semantic, 3 for Io
- [ ] DiagramError implements std::error::Error and fmt::Display
- [ ] DiagramError::format_detailed() produces human-readable messages with line/column info
- [ ] From<io::Error> trait converts io::Error to DiagramError::Io
- [ ] Result<T> type alias defined as std::result::Result<T, DiagramError>

## Testing Strategy

### Test Files
- `src/error.rs` (inline #[cfg(test)] module)

### Test Categories
- **Unit tests**: exit_code() returns 1/2/3 for each variant; format_detailed() includes position info; Display trait formatting
- **Functional tests**: From<io::Error> conversion produces DiagramError::Io; SemanticError variants construct correctly
- **Edge cases**: format_detailed() handles all SemanticError variants with correct messages

### Run Command
`cargo test --lib error`

## Verification Commands
- **Build**: `cargo build`
- **Test**: `cargo test --lib error`
- **Check**: `cargo clippy -- -D warnings && cargo fmt -- --check`
