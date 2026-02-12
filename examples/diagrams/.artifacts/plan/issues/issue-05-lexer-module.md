# issue-05-lexer-module: Implement DSL tokenizer with position tracking and comment handling

## Description
Create the lexer module that tokenizes DSL input into a stream of positioned tokens. The lexer must handle all token types (keywords, identifiers, strings, operators), skip comments starting with #, and track line/column positions for error reporting. This provides the foundation for the parser to build the AST.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-diagrams/.artifacts/plan/architecture.md` Section 3 (Component 3: Parser - Lexer Module) for:
- Token and PositionedToken type definitions
- Lexer struct with complete method signatures
- Helper method patterns (peek, advance, skip_whitespace, etc.)
- Keyword matching logic
- String parsing with escape sequence handling
- Error case handling for unterminated strings

## Interface Contracts
```rust
// Implements from architecture Section 3:
pub fn new(input: &str) -> Self
pub fn tokenize(&mut self) -> Result<Vec<PositionedToken>, DiagramError>
fn match_keyword(&self, s: &str) -> Token  // returns Node/As/Type or Identifier
```

- **Exports**: Token enum (all variants), PositionedToken struct, Lexer struct
- **Consumes**: DiagramError, SyntaxError, SourcePosition from dependencies
- **Consumed by**: Parser module (issue-06) which needs positioned token stream

## Isolation Context
- **Available**: types module (SourcePosition), error module (DiagramError, SyntaxError)
- **NOT available**: parser, validator, layout, or rendering modules
- **Source of truth**: Architecture document Section 3 for lexer design

## Files
- **Create**: `src/lexer.rs`
- **Modify**: `src/main.rs` (add `mod lexer;` declaration)

## Dependencies
- issue-02-types-module (provides: SourcePosition)
- issue-03-error-module (provides: DiagramError, SyntaxError)

## Provides
- Token enum with all DSL token types
- PositionedToken struct for parser consumption
- Lexer struct with tokenize() method
- Comment skipping (lines starting with #)
- Position tracking for error reporting

## Acceptance Criteria
- [ ] src/lexer.rs exists and compiles
- [ ] Token enum defines: Node, As, Type, Identifier(String), String(String), Arrow, Colon, LeftBracket, RightBracket, Newline, Eof
- [ ] PositionedToken struct contains token and position fields
- [ ] Lexer::new(input: &str) creates lexer from string
- [ ] Lexer::tokenize() returns Result<Vec<PositionedToken>, DiagramError>
- [ ] Lexer correctly tokenizes keywords: node, as, type
- [ ] Lexer correctly tokenizes operators: ->, :, [, ]
- [ ] Lexer correctly parses quoted strings with escape sequences
- [ ] Lexer skips lines starting with # (comments)
- [ ] Lexer tracks line and column positions accurately
- [ ] Lexer returns SyntaxError for unterminated strings
- [ ] At least 5 unit tests pass

## Testing Strategy

### Test Files
- `src/lexer.rs` (inline `#[cfg(test)] mod tests`)

### Test Categories
- **Unit tests**: test_tokenize_empty, test_tokenize_node_decl, test_tokenize_connection, test_tokenize_string_escape, test_tokenize_comment, test_error_unterminated_string
- **Functional tests**: Full tokenization of node declaration, connection with arrow/colon/label, multi-line input with comments
- **Edge cases**: Empty input produces [Eof], unterminated string error, position tracking on newlines, escape sequences (\", \\)

### Run Command
```bash
cargo test --lib lexer
```

## Verification Commands
- Build: `cargo build --lib`
- Test: `cargo test --lib lexer`
- Check: `cargo test --lib lexer -- --nocapture | grep "test result: ok"`
