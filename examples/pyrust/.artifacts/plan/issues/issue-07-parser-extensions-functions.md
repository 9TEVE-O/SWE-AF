# issue-07-parser-extensions-functions: Parse function definition and call syntax

## Description
Extend the parser to recognize and parse function definition syntax (`def name(params): blocks`) and function call syntax (`func(args)`). This transforms function tokens into the AST nodes defined in issue-05 (ast-extensions-functions). Includes parsing parameter lists, function bodies, and call arguments.

## Architecture Reference
Read architecture.md Section 5 (Parser Module) and Section 3 (Lexer Module) for:
- `Parser::parse_statement()` extension pattern for new statement types
- `Parser::parse_primary()` extension pattern for new expression types
- Pratt parsing automatically handles function calls as postfix expressions
- `TokenKind` enum extension for new keywords and delimiters

## Interface Contracts
- Implements:
  - `parse_function_def() -> Result<Statement, ParseError>` (parses `def name(params): body`)
  - `parse_return_statement() -> Result<Statement, ParseError>` (parses `return [expr]`)
  - `parse_call(name: String) -> Result<Expression, ParseError>` (parses `(args)`)
- Extends: `TokenKind` with `Def`, `Return`, `Colon`, `Comma`
- Consumes: Token stream from lexer with new function keywords
- Consumed by: Compiler (issue-08) transforms parsed AST into bytecode

## Files
- **Modify**: `src/lexer.rs` (add Def, Return, Colon, Comma to TokenKind enum and lexer logic)
- **Modify**: `src/parser.rs` (add function parsing methods in `parse_statement()` and `parse_primary()`)

## Dependencies
- issue-05 (ast-extensions-functions): Provides AST node definitions

## Provides
- Parsing of `def name(params): body` syntax into Statement::FunctionDef
- Parsing of `return` and `return expr` syntax into Statement::Return
- Parsing of `func(arg1, arg2)` syntax into Expression::Call
- Parameter list parsing (comma-separated identifiers)
- Argument list parsing (comma-separated expressions)

## Acceptance Criteria
- [ ] `def foo():` syntax parses successfully into Statement::FunctionDef
- [ ] Zero-parameter function definitions parse correctly
- [ ] Functions with parameters parse correctly (comma-separated param names)
- [ ] `return` without value parses into Statement::Return with None
- [ ] `return expr` parses into Statement::Return with Some(Expression)
- [ ] Function calls with 0+ arguments parse into Expression::Call
- [ ] Parser errors are clear for malformed function syntax (missing colons, mismatched parens)
- [ ] All existing parser tests continue to pass (regression check)
- [ ] At least 15 new parser tests for function syntax variations

## Testing Strategy

### Test Files
- `src/parser.rs` #[cfg(test)] mod tests: Add function-specific tests following existing test pattern

### Test Categories
- **Function definition parsing**: Zero params, one param, multiple params; nested statements in body
- **Return statement parsing**: With value, without value, inside function definitions
- **Function call parsing**: Zero args, one arg, multiple args, nested calls in arguments
- **Error cases**: Missing colons, mismatched parens, invalid syntax, empty param lists
- **Edge cases**: Empty function bodies, nested function calls, functions with expressions as arguments
- **Regression**: All existing parser tests pass (199 existing tests must remain green)

### Run Command
`cargo test --lib parser::tests`
