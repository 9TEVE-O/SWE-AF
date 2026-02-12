# Issue: Parser Implementation

## Summary
Implement recursive descent parser with Pratt parsing for expressions. Transforms token stream into AST, enforcing Python operator precedence and handling all Phase 1 statement types.

## Context
The parser is the second stage of compilation. It must achieve ~10μs performance for typical 10-token inputs. Uses Pratt parsing algorithm for clean precedence handling.

## Architecture Reference
See architecture.md lines 514-612 for complete parser specification.

## Implementation Requirements

### 1. Create `src/parser.rs` with Exact Implementation

```rust
use crate::ast::*;
use crate::lexer::{Token, TokenKind};
use crate::error::ParseError;

/// Parse token stream into AST
///
/// # Performance
/// Target: ~10μs for 10-token input
///
/// # Example
/// ```
/// let tokens = lexer::lex("x = 10\nx + 5")?;
/// let ast = parser::parse(tokens)?;
/// assert_eq!(ast.statements.len(), 2);
/// ```
pub fn parse(tokens: Vec<Token>) -> Result<Program, ParseError> {
    let mut parser = Parser::new(tokens);
    parser.parse_program()
}

// Internal implementation
struct Parser<'src> {
    tokens: Vec<Token<'src>>,
    current: usize,
}

impl<'src> Parser<'src> {
    fn new(tokens: Vec<Token<'src>>) -> Self {
        Parser {
            tokens,
            current: 0,
        }
    }

    /// Parse entire program
    fn parse_program(&mut self) -> Result<Program, ParseError> {
        let mut statements = Vec::new();

        while !self.is_at_end() {
            // Skip newlines at top level
            if self.peek().kind == TokenKind::Newline {
                self.advance();
                continue;
            }

            if self.peek().kind == TokenKind::Eof {
                break;
            }

            statements.push(self.parse_statement()?);
        }

        Ok(Program { statements })
    }

    /// Parse single statement
    fn parse_statement(&mut self) -> Result<Statement, ParseError> {
        // Check for print statement
        if self.peek().kind == TokenKind::Print {
            return self.parse_print_statement();
        }

        // Check for assignment (lookahead for =)
        if self.peek().kind == TokenKind::Identifier {
            // Lookahead for assignment
            if self.current + 1 < self.tokens.len() && self.tokens[self.current + 1].kind == TokenKind::Equals {
                return self.parse_assignment();
            }
        }

        // Otherwise, it's an expression statement
        self.parse_expression_statement()
    }

    /// Parse assignment: x = expr
    fn parse_assignment(&mut self) -> Result<Statement, ParseError> {
        let target_token = self.expect(TokenKind::Identifier)?;
        let target = target_token.text.to_string();

        self.expect(TokenKind::Equals)?;

        let value = self.parse_expression(0)?;

        // Consume optional newline
        if self.peek().kind == TokenKind::Newline {
            self.advance();
        }

        Ok(Statement::Assignment { target, value })
    }

    /// Parse print statement: print(expr)
    fn parse_print_statement(&mut self) -> Result<Statement, ParseError> {
        self.expect(TokenKind::Print)?;
        self.expect(TokenKind::LeftParen)?;

        let value = self.parse_expression(0)?;

        self.expect(TokenKind::RightParen)?;

        // Consume optional newline
        if self.peek().kind == TokenKind::Newline {
            self.advance();
        }

        Ok(Statement::Print { value })
    }

    /// Parse expression statement
    fn parse_expression_statement(&mut self) -> Result<Statement, ParseError> {
        let value = self.parse_expression(0)?;

        // Consume optional newline
        if self.peek().kind == TokenKind::Newline {
            self.advance();
        }

        Ok(Statement::Expression { value })
    }

    /// Parse expression using Pratt parsing
    fn parse_expression(&mut self, min_precedence: u8) -> Result<Expression, ParseError> {
        let mut left = self.parse_primary()?;

        while !self.is_at_end() {
            let op_token = self.peek();
            let op = match op_token.kind {
                TokenKind::Plus => BinaryOperator::Add,
                TokenKind::Minus => BinaryOperator::Subtract,
                TokenKind::Star => BinaryOperator::Multiply,
                TokenKind::Slash => BinaryOperator::Divide,
                TokenKind::DoubleSlash => BinaryOperator::FloorDiv,
                TokenKind::Percent => BinaryOperator::Modulo,
                _ => break, // Not a binary operator
            };

            if op.precedence() < min_precedence {
                break; // Precedence too low, return to caller
            }

            self.advance(); // Consume operator
            let right = self.parse_expression(op.precedence() + 1)?; // Right-associative: use +1

            left = Expression::BinaryOp {
                op,
                left: Box::new(left),
                right: Box::new(right),
            };
        }

        Ok(left)
    }

    /// Parse primary expression (leaf nodes)
    fn parse_primary(&mut self) -> Result<Expression, ParseError> {
        let token = self.peek();

        match token.kind {
            TokenKind::Integer => {
                let text = token.text;
                self.advance();

                let value = text.parse::<i64>().map_err(|_| ParseError {
                    message: format!("Integer literal out of range: {}", text),
                    line: token.line,
                    column: token.column,
                    found_token: text.to_string(),
                    expected_tokens: vec!["valid i64 integer".to_string()],
                })?;

                Ok(Expression::Integer { value })
            }

            TokenKind::Identifier => {
                let name = token.text.to_string();
                self.advance();
                Ok(Expression::Variable { name })
            }

            TokenKind::LeftParen => {
                self.advance(); // Consume '('
                let expr = self.parse_expression(0)?;
                self.expect(TokenKind::RightParen)?;
                Ok(expr)
            }

            _ => {
                Err(ParseError {
                    message: "Expected primary expression (integer, variable, or parenthesized expression)".to_string(),
                    line: token.line,
                    column: token.column,
                    found_token: token.text.to_string(),
                    expected_tokens: vec!["integer".to_string(), "identifier".to_string(), "(".to_string()],
                })
            }
        }
    }

    // Token consumption helpers
    fn peek(&self) -> &Token<'src> {
        &self.tokens[self.current]
    }

    fn advance(&mut self) -> &Token<'src> {
        let token = &self.tokens[self.current];
        if !self.is_at_end() {
            self.current += 1;
        }
        token
    }

    fn expect(&mut self, kind: TokenKind) -> Result<&Token<'src>, ParseError> {
        let token = self.peek();
        if token.kind == kind {
            Ok(self.advance())
        } else {
            Err(ParseError {
                message: format!("Expected {:?}", kind),
                line: token.line,
                column: token.column,
                found_token: token.text.to_string(),
                expected_tokens: vec![format!("{:?}", kind)],
            })
        }
    }

    fn is_at_end(&self) -> bool {
        self.peek().kind == TokenKind::Eof
    }
}
```

### 2. Unit Tests

Add tests at the bottom of `src/parser.rs`:

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use crate::lexer;

    #[test]
    fn test_parse_simple_integer() {
        let tokens = lexer::lex("42").unwrap();
        let ast = parse(tokens).unwrap();

        assert_eq!(ast.statements.len(), 1);
        match &ast.statements[0] {
            Statement::Expression { value } => {
                assert_eq!(*value, Expression::Integer { value: 42 });
            }
            _ => panic!("Expected expression statement"),
        }
    }

    #[test]
    fn test_parse_addition() {
        let tokens = lexer::lex("2 + 3").unwrap();
        let ast = parse(tokens).unwrap();

        assert_eq!(ast.statements.len(), 1);
        match &ast.statements[0] {
            Statement::Expression { value } => {
                if let Expression::BinaryOp { op, left, right } = value {
                    assert_eq!(*op, BinaryOperator::Add);
                    assert_eq!(**left, Expression::Integer { value: 2 });
                    assert_eq!(**right, Expression::Integer { value: 3 });
                } else {
                    panic!("Expected binary op");
                }
            }
            _ => panic!("Expected expression statement"),
        }
    }

    #[test]
    fn test_operator_precedence() {
        // 2 + 3 * 4 should parse as 2 + (3 * 4)
        let tokens = lexer::lex("2 + 3 * 4").unwrap();
        let ast = parse(tokens).unwrap();

        match &ast.statements[0] {
            Statement::Expression { value } => {
                if let Expression::BinaryOp { op, left, right } = value {
                    assert_eq!(*op, BinaryOperator::Add);
                    assert_eq!(**left, Expression::Integer { value: 2 });

                    // Right side should be 3 * 4
                    if let Expression::BinaryOp { op: mul_op, .. } = &**right {
                        assert_eq!(*mul_op, BinaryOperator::Multiply);
                    } else {
                        panic!("Expected multiply on right");
                    }
                } else {
                    panic!("Expected binary op");
                }
            }
            _ => panic!("Expected expression statement"),
        }
    }

    #[test]
    fn test_parentheses_override_precedence() {
        // (2 + 3) * 4 should parse as (2 + 3) * 4
        let tokens = lexer::lex("(2 + 3) * 4").unwrap();
        let ast = parse(tokens).unwrap();

        match &ast.statements[0] {
            Statement::Expression { value } => {
                if let Expression::BinaryOp { op, left, right } = value {
                    assert_eq!(*op, BinaryOperator::Multiply);
                    assert_eq!(**right, Expression::Integer { value: 4 });

                    // Left side should be 2 + 3
                    if let Expression::BinaryOp { op: add_op, .. } = &**left {
                        assert_eq!(*add_op, BinaryOperator::Add);
                    } else {
                        panic!("Expected add on left");
                    }
                } else {
                    panic!("Expected binary op");
                }
            }
            _ => panic!("Expected expression statement"),
        }
    }

    #[test]
    fn test_parse_variable() {
        let tokens = lexer::lex("x").unwrap();
        let ast = parse(tokens).unwrap();

        match &ast.statements[0] {
            Statement::Expression { value } => {
                assert_eq!(*value, Expression::Variable { name: "x".to_string() });
            }
            _ => panic!("Expected expression statement"),
        }
    }

    #[test]
    fn test_parse_assignment() {
        let tokens = lexer::lex("x = 10").unwrap();
        let ast = parse(tokens).unwrap();

        assert_eq!(ast.statements.len(), 1);
        match &ast.statements[0] {
            Statement::Assignment { target, value } => {
                assert_eq!(target, "x");
                assert_eq!(*value, Expression::Integer { value: 10 });
            }
            _ => panic!("Expected assignment statement"),
        }
    }

    #[test]
    fn test_parse_print() {
        let tokens = lexer::lex("print(42)").unwrap();
        let ast = parse(tokens).unwrap();

        match &ast.statements[0] {
            Statement::Print { value } => {
                assert_eq!(*value, Expression::Integer { value: 42 });
            }
            _ => panic!("Expected print statement"),
        }
    }

    #[test]
    fn test_multiple_statements() {
        let tokens = lexer::lex("x = 10\ny = 20\nx + y").unwrap();
        let ast = parse(tokens).unwrap();

        assert_eq!(ast.statements.len(), 3);

        // First: x = 10
        match &ast.statements[0] {
            Statement::Assignment { target, .. } => assert_eq!(target, "x"),
            _ => panic!("Expected assignment"),
        }

        // Second: y = 20
        match &ast.statements[1] {
            Statement::Assignment { target, .. } => assert_eq!(target, "y"),
            _ => panic!("Expected assignment"),
        }

        // Third: x + y
        match &ast.statements[2] {
            Statement::Expression { value } => {
                if let Expression::BinaryOp { op, .. } = value {
                    assert_eq!(*op, BinaryOperator::Add);
                }
            }
            _ => panic!("Expected expression"),
        }
    }

    #[test]
    fn test_all_operators() {
        let test_cases = vec![
            ("2 + 3", BinaryOperator::Add),
            ("2 - 3", BinaryOperator::Subtract),
            ("2 * 3", BinaryOperator::Multiply),
            ("2 / 3", BinaryOperator::Divide),
            ("2 // 3", BinaryOperator::FloorDiv),
            ("2 % 3", BinaryOperator::Modulo),
        ];

        for (input, expected_op) in test_cases {
            let tokens = lexer::lex(input).unwrap();
            let ast = parse(tokens).unwrap();

            match &ast.statements[0] {
                Statement::Expression { value } => {
                    if let Expression::BinaryOp { op, .. } = value {
                        assert_eq!(*op, expected_op, "Failed for input: {}", input);
                    } else {
                        panic!("Expected binary op for: {}", input);
                    }
                }
                _ => panic!("Expected expression for: {}", input),
            }
        }
    }

    #[test]
    fn test_error_unexpected_token() {
        let tokens = lexer::lex("2 + + 3").unwrap();
        let result = parse(tokens);

        assert!(result.is_err());
        let err = result.unwrap_err();
        assert!(err.message.contains("Expected primary expression"));
        assert_eq!(err.found_token, "+");
    }

    #[test]
    fn test_error_missing_closing_paren() {
        let tokens = lexer::lex("(2 + 3").unwrap();
        let result = parse(tokens);

        assert!(result.is_err());
        let err = result.unwrap_err();
        assert!(err.message.contains("Expected"));
        assert!(err.message.contains("RightParen") || err.expected_tokens.iter().any(|t| t.contains("RightParen")));
    }

    #[test]
    fn test_empty_input() {
        let tokens = lexer::lex("").unwrap();
        let ast = parse(tokens).unwrap();

        assert_eq!(ast.statements.len(), 0);
    }

    #[test]
    fn test_complex_expression() {
        // Test: x = 2 + 3 * 4 - 5 / 2
        let tokens = lexer::lex("x = 2 + 3 * 4 - 5 / 2").unwrap();
        let ast = parse(tokens).unwrap();

        assert_eq!(ast.statements.len(), 1);
        match &ast.statements[0] {
            Statement::Assignment { target, value } => {
                assert_eq!(target, "x");
                // Just verify it parses without error - structure is complex
                assert!(matches!(value, Expression::BinaryOp { .. }));
            }
            _ => panic!("Expected assignment"),
        }
    }

    #[test]
    fn test_newline_handling() {
        let tokens = lexer::lex("\n\nx = 10\n\ny = 20\n\n").unwrap();
        let ast = parse(tokens).unwrap();

        // Should skip leading/trailing newlines
        assert_eq!(ast.statements.len(), 2);
    }
}
```

## Acceptance Criteria

1. ✅ `src/parser.rs` exists with parse() function matching architecture
2. ✅ Implements recursive descent parsing with Pratt algorithm for expressions
3. ✅ Correctly handles operator precedence (multiplication before addition)
4. ✅ Supports parentheses for precedence override
5. ✅ Parses all Phase 1 statements: Assignment, Print, Expression
6. ✅ Parses all Phase 1 operators: +, -, *, /, //, %
7. ✅ Returns ParseError with location information for invalid syntax
8. ✅ Handles multiple statements separated by newlines
9. ✅ Unit tests pass: `cargo test --lib parser::tests`
10. ✅ Code compiles: `cargo check`

## Testing Instructions

```bash
# Run parser module tests
cargo test --lib parser::tests

# Run precedence tests
cargo test --lib parser::tests::test_operator_precedence

# Run error tests
cargo test --lib parser::tests::test_error

# Check compilation
cargo check
```

## Dependencies

- `src/lexer.rs` (Token, TokenKind)
- `src/ast.rs` (Program, Statement, Expression, BinaryOperator)
- `src/error.rs` (ParseError)

## Provides

- `parse(tokens: Vec<Token>) -> Result<Program, ParseError>` function

## Interface Contract with Lexer

Receives `Vec<Token<'src>>` from lexer and:
- Expects tokens in sequential order ending with Eof
- Uses token.kind for pattern matching
- Uses token.text for extracting integer values and variable names
- Uses token.line and token.column for error reporting

## Interface Contract with Compiler

Returns AST (Program) to compiler:
- Program contains Vec<Statement>
- Each Statement is Assignment, Print, or Expression
- Expressions are fully constructed with correct precedence
- Compiler can pattern-match on AST nodes without re-parsing

## Performance Notes

- Pratt parsing: O(n) in token count with low constant factor
- Recursive descent: Minimal allocation (Box for nested expressions)
- Lookahead: Only 1 token needed (peek)
- Target: ~10μs for 10-token input

## Notes

- Pratt parsing automatically handles precedence - no special cases needed
- Parentheses are handled in parse_primary() by recursively calling parse_expression(0)
- Newlines are statement separators but optional (allows single-line multiple statements)
- Phase 1: No control flow, so no complex statement parsing
