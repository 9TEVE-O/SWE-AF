# issue-09-parser-module: Implement recursive descent parser for DSL grammar

## Description
Create src/parser.rs with Parser struct that builds Diagram AST from token stream using recursive descent. Parse node declarations (with optional type annotations) and connection declarations. Implement grammar per architecture specification: diagram → statement*, statement → node_decl | connection_decl.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-diagrams/.artifacts/plan/architecture.md` Section 4 (Parser Module) for:
- Complete grammar specification (lines 459-464)
- Parser struct definition and method signatures
- Helper methods for token manipulation (peek, advance, expect, skip_newlines)
- Error handling patterns (syntax_error helper)
- Node type parsing logic (defaults to Service when omitted)

## Interface Contracts
```rust
pub struct Parser { tokens: Vec<PositionedToken>, position: usize }
impl Parser {
    pub fn new(tokens: Vec<PositionedToken>) -> Self
    pub fn parse(&mut self) -> Result<Diagram, DiagramError>
}
```

- **Implements**: Recursive descent parser for DSL grammar
- **Exports**: Parser struct with parse() method
- **Consumes**: Vec<PositionedToken> from lexer, DiagramError/SyntaxError from error module, Diagram/Node/Connection/NodeType from types
- **Consumed by**: app module (parse_source function)

## Isolation Context
- **Available**: types module (AST definitions), error module (DiagramError), lexer module (Token, PositionedToken)
- **NOT available**: validator, layout, renderers (same-level or higher-level components)
- **Source of truth**: architecture document at path above

## Files
- **Create**: `src/parser.rs`
- **Modify**: `src/main.rs` (add `mod parser;`)

## Dependencies
- issue-01-types-module (provides: Diagram, Node, Connection, NodeType, SourcePosition)
- issue-02-error-module (provides: DiagramError, SyntaxError)
- issue-03-lexer-module (provides: Token, PositionedToken)

## Provides
- Parser::new(tokens) constructor
- Parser::parse() → Result<Diagram, DiagramError>
- Complete recursive descent parser for DSL grammar
- Syntax error detection with position tracking

## Acceptance Criteria
- [ ] src/parser.rs exists and compiles
- [ ] Parser::new(tokens: Vec<PositionedToken>) creates parser
- [ ] Parser::parse() returns Result<Diagram, DiagramError>
- [ ] Parser correctly parses node declarations: node "Display Name" as identifier
- [ ] Parser correctly parses node type annotations: [type: service|database|external|queue]
- [ ] Parser defaults to NodeType::Service when type annotation omitted
- [ ] Parser correctly parses connections: identifier -> identifier : "label"
- [ ] Parser handles optional connection labels (label may be omitted)
- [ ] Parser returns SyntaxError on malformed statements with correct position
- [ ] Parser returns SyntaxError on invalid node type strings
- [ ] At least 5 unit tests pass covering: single node, node with type, connection with/without label, syntax errors

## Testing Strategy

### Test Files
- `src/parser.rs`: #[cfg(test)] module with unit tests

### Test Categories
- **Unit tests**: parse_single_node, parse_node_with_type, parse_connection_with_label, parse_connection_without_label, parse_multiple_statements
- **Error tests**: error_missing_as_keyword, error_invalid_node_type, error_malformed_connection
- **Edge cases**: empty token stream (just Eof), newline handling, whitespace-only input

### Run Command
`cargo test --lib parser`

## Verification Commands
- Build: `cargo build`
- Test: `cargo test --lib parser`
- Check: `cargo test --lib parser -- --list | grep -c 'test' | awk '{exit !($1 >= 5)}'`
