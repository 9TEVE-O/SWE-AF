# Issue: Lexer Implementation

## Summary
Implement zero-copy tokenization of Python source code into token stream. Single-pass O(n) lexer with tokens storing slices into source string for maximum performance.

## Context
The lexer is the first stage of the compilation pipeline. It must achieve ~5μs performance for typical 50-byte inputs. Uses lifetime parameters for zero-copy tokens.

## Architecture Reference
See architecture.md lines 317-411 for complete lexer specification.

## Implementation Requirements

### 1. Create `src/lexer.rs` with Exact Types

```rust
use crate::error::LexError;

/// Token type enum covering Phase 1 syntax
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TokenKind {
    // Literals
    Integer,        // 123, 0, -45

    // Identifiers
    Identifier,     // x, foo, bar_123

    // Operators (precedence defined in parser)
    Plus,           // +
    Minus,          // -
    Star,           // *
    Slash,          // /
    DoubleSlash,    // //
    Percent,        // %

    // Delimiters
    LeftParen,      // (
    RightParen,     // )

    // Assignment
    Equals,         // =

    // Keywords
    Print,          // print (special-cased for Phase 1)

    // Structural
    Newline,        // \n (statement separator)
    Eof,            // End of file
}

/// Token with source location and zero-copy text slice
#[derive(Debug, Clone, Copy)]
pub struct Token<'src> {
    pub kind: TokenKind,
    pub text: &'src str,  // Zero-copy slice into source
    pub line: usize,
    pub column: usize,
}

/// Lex source code into token vector
///
/// # Performance
/// Target: ~5μs for 50-byte input
///
/// # Example
/// ```
/// let tokens = lexer::lex("2 + 3 * 4")?;
/// assert_eq!(tokens[0].kind, TokenKind::Integer);
/// assert_eq!(tokens[0].text, "2");
/// ```
pub fn lex(source: &str) -> Result<Vec<Token>, LexError> {
    let mut lexer = Lexer::new(source);
    lexer.lex_all()
}

// Internal implementation
struct Lexer<'src> {
    source: &'src str,
    chars: std::iter::Peekable<std::str::CharIndices<'src>>,
    current_pos: usize,
    line: usize,
    column: usize,
}

impl<'src> Lexer<'src> {
    fn new(source: &'src str) -> Self {
        Lexer {
            source,
            chars: source.char_indices().peekable(),
            current_pos: 0,
            line: 1,
            column: 1,
        }
    }

    fn lex_all(&mut self) -> Result<Vec<Token<'src>>, LexError> {
        let mut tokens = Vec::with_capacity(self.source.len() / 4); // Heuristic: avg 4 chars/token

        loop {
            self.skip_whitespace_except_newline();

            let token = self.next_token()?;
            let is_eof = token.kind == TokenKind::Eof;
            tokens.push(token);

            if is_eof {
                break;
            }
        }

        Ok(tokens)
    }

    fn next_token(&mut self) -> Result<Token<'src>, LexError> {
        let start_line = self.line;
        let start_column = self.column;
        let start_pos = self.current_pos;

        let Some(&(pos, ch)) = self.chars.peek() else {
            return Ok(Token {
                kind: TokenKind::Eof,
                text: "",
                line: self.line,
                column: self.column,
            });
        };

        let kind = match ch {
            '\n' => {
                self.advance();
                self.line += 1;
                self.column = 1;
                TokenKind::Newline
            }
            '+' => { self.advance(); TokenKind::Plus }
            '-' => { self.advance(); TokenKind::Minus }
            '*' => { self.advance(); TokenKind::Star }
            '/' => {
                self.advance();
                // Check for //
                if self.peek_char() == Some('/') {
                    self.advance();
                    TokenKind::DoubleSlash
                } else {
                    TokenKind::Slash
                }
            }
            '%' => { self.advance(); TokenKind::Percent }
            '(' => { self.advance(); TokenKind::LeftParen }
            ')' => { self.advance(); TokenKind::RightParen }
            '=' => { self.advance(); TokenKind::Equals }
            '0'..='9' => return self.lex_number(start_line, start_column),
            'a'..='z' | 'A'..='Z' | '_' => return self.lex_identifier_or_keyword(start_line, start_column),
            _ => {
                return Err(LexError {
                    message: format!("Unexpected character: '{}'", ch),
                    line: start_line,
                    column: start_column,
                });
            }
        };

        let end_pos = self.current_pos;
        Ok(Token {
            kind,
            text: &self.source[start_pos..end_pos],
            line: start_line,
            column: start_column,
        })
    }

    fn lex_number(&mut self, start_line: usize, start_column: usize) -> Result<Token<'src>, LexError> {
        let start_pos = self.current_pos;

        while let Some(&(_, ch)) = self.chars.peek() {
            if ch.is_ascii_digit() {
                self.advance();
            } else {
                break;
            }
        }

        let end_pos = self.current_pos;
        let text = &self.source[start_pos..end_pos];

        // Validate that text is a valid integer
        if text.parse::<i64>().is_err() {
            return Err(LexError {
                message: format!("Invalid integer literal: {}", text),
                line: start_line,
                column: start_column,
            });
        }

        Ok(Token {
            kind: TokenKind::Integer,
            text,
            line: start_line,
            column: start_column,
        })
    }

    fn lex_identifier_or_keyword(&mut self, start_line: usize, start_column: usize) -> Result<Token<'src>, LexError> {
        let start_pos = self.current_pos;

        while let Some(&(_, ch)) = self.chars.peek() {
            if ch.is_alphanumeric() || ch == '_' {
                self.advance();
            } else {
                break;
            }
        }

        let end_pos = self.current_pos;
        let text = &self.source[start_pos..end_pos];

        let kind = match text {
            "print" => TokenKind::Print,
            _ => TokenKind::Identifier,
        };

        Ok(Token {
            kind,
            text,
            line: start_line,
            column: start_column,
        })
    }

    fn skip_whitespace_except_newline(&mut self) {
        while let Some(&(_, ch)) = self.chars.peek() {
            if ch == ' ' || ch == '\t' || ch == '\r' {
                self.advance();
            } else {
                break;
            }
        }
    }

    fn advance(&mut self) {
        if let Some((pos, ch)) = self.chars.next() {
            self.current_pos = pos + ch.len_utf8();
            if ch != '\n' {
                self.column += 1;
            }
        }
    }

    fn peek_char(&mut self) -> Option<char> {
        self.chars.peek().map(|&(_, ch)| ch)
    }
}
```

### 2. Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_single_integer() {
        let tokens = lex("42").unwrap();
        assert_eq!(tokens.len(), 2); // Integer + Eof
        assert_eq!(tokens[0].kind, TokenKind::Integer);
        assert_eq!(tokens[0].text, "42");
        assert_eq!(tokens[1].kind, TokenKind::Eof);
    }

    #[test]
    fn test_operators() {
        let tokens = lex("+ - * / // %").unwrap();
        assert_eq!(tokens[0].kind, TokenKind::Plus);
        assert_eq!(tokens[1].kind, TokenKind::Minus);
        assert_eq!(tokens[2].kind, TokenKind::Star);
        assert_eq!(tokens[3].kind, TokenKind::Slash);
        assert_eq!(tokens[4].kind, TokenKind::DoubleSlash);
        assert_eq!(tokens[5].kind, TokenKind::Percent);
    }

    #[test]
    fn test_simple_expression() {
        let tokens = lex("2 + 3").unwrap();
        assert_eq!(tokens[0].kind, TokenKind::Integer);
        assert_eq!(tokens[0].text, "2");
        assert_eq!(tokens[1].kind, TokenKind::Plus);
        assert_eq!(tokens[2].kind, TokenKind::Integer);
        assert_eq!(tokens[2].text, "3");
        assert_eq!(tokens[3].kind, TokenKind::Eof);
    }

    #[test]
    fn test_complex_expression() {
        let tokens = lex("2 + 3 * 4").unwrap();
        assert_eq!(tokens.len(), 6); // 2, +, 3, *, 4, Eof
        assert_eq!(tokens[0].text, "2");
        assert_eq!(tokens[2].text, "3");
        assert_eq!(tokens[4].text, "4");
    }

    #[test]
    fn test_parentheses() {
        let tokens = lex("(2 + 3) * 4").unwrap();
        assert_eq!(tokens[0].kind, TokenKind::LeftParen);
        assert_eq!(tokens[4].kind, TokenKind::RightParen);
    }

    #[test]
    fn test_identifier() {
        let tokens = lex("x").unwrap();
        assert_eq!(tokens[0].kind, TokenKind::Identifier);
        assert_eq!(tokens[0].text, "x");
    }

    #[test]
    fn test_assignment() {
        let tokens = lex("x = 10").unwrap();
        assert_eq!(tokens[0].kind, TokenKind::Identifier);
        assert_eq!(tokens[0].text, "x");
        assert_eq!(tokens[1].kind, TokenKind::Equals);
        assert_eq!(tokens[2].kind, TokenKind::Integer);
        assert_eq!(tokens[2].text, "10");
    }

    #[test]
    fn test_print_keyword() {
        let tokens = lex("print(42)").unwrap();
        assert_eq!(tokens[0].kind, TokenKind::Print);
        assert_eq!(tokens[0].text, "print");
    }

    #[test]
    fn test_newlines() {
        let tokens = lex("x = 10\ny = 20").unwrap();
        assert_eq!(tokens[0].kind, TokenKind::Identifier);
        assert_eq!(tokens[3].kind, TokenKind::Newline);
        assert_eq!(tokens[4].kind, TokenKind::Identifier);
    }

    #[test]
    fn test_location_tracking() {
        let tokens = lex("x + y").unwrap();
        assert_eq!(tokens[0].line, 1);
        assert_eq!(tokens[0].column, 1);
        assert_eq!(tokens[1].line, 1);
        assert_eq!(tokens[1].column, 3);
        assert_eq!(tokens[2].line, 1);
        assert_eq!(tokens[2].column, 5);
    }

    #[test]
    fn test_multiline_location() {
        let tokens = lex("x\n+\ny").unwrap();
        assert_eq!(tokens[0].line, 1);
        assert_eq!(tokens[1].line, 1); // Newline
        assert_eq!(tokens[2].line, 2);
        assert_eq!(tokens[3].line, 2); // Newline
        assert_eq!(tokens[4].line, 3);
    }

    #[test]
    fn test_unexpected_character() {
        let result = lex("2 @ 3");
        assert!(result.is_err());
        let err = result.unwrap_err();
        assert!(err.message.contains("Unexpected character"));
        assert_eq!(err.line, 1);
        assert_eq!(err.column, 3);
    }

    #[test]
    fn test_zero_copy_tokens() {
        let source = "42 + 100";
        let tokens = lex(source).unwrap();
        // Tokens should reference the original source
        assert!(std::ptr::eq(tokens[0].text.as_ptr(), &source.as_bytes()[0]));
        assert!(std::ptr::eq(tokens[2].text.as_ptr(), &source.as_bytes()[5]));
    }

    #[test]
    fn test_empty_input() {
        let tokens = lex("").unwrap();
        assert_eq!(tokens.len(), 1);
        assert_eq!(tokens[0].kind, TokenKind::Eof);
    }

    #[test]
    fn test_whitespace_handling() {
        let tokens = lex("  2   +   3  ").unwrap();
        assert_eq!(tokens.len(), 4); // 2, +, 3, Eof (whitespace stripped)
    }

    #[test]
    fn test_large_integer() {
        let tokens = lex("9223372036854775807").unwrap(); // i64::MAX
        assert_eq!(tokens[0].kind, TokenKind::Integer);
        assert_eq!(tokens[0].text, "9223372036854775807");
    }

    #[test]
    fn test_integer_overflow_detection() {
        let result = lex("99999999999999999999999999");
        assert!(result.is_err());
        let err = result.unwrap_err();
        assert!(err.message.contains("Invalid integer literal"));
    }
}
```

## Acceptance Criteria

1. ✅ `src/lexer.rs` exists with all token types matching architecture
2. ✅ `lex()` function returns `Vec<Token>` with zero-copy slices
3. ✅ All Phase 1 tokens supported: integers, operators, identifiers, keywords, delimiters
4. ✅ Location tracking: every token has correct line and column
5. ✅ `//` correctly lexed as `DoubleSlash` (not two `Slash` tokens)
6. ✅ `print` keyword recognized (not identifier)
7. ✅ Unexpected characters return `LexError` with location
8. ✅ Integer overflow detection during lexing
9. ✅ Unit tests pass: `cargo test --lib lexer::tests`
10. ✅ Code compiles: `cargo check`

## Testing Instructions

```bash
# Run lexer tests
cargo test --lib lexer::tests

# Run zero-copy verification
cargo test --lib lexer::tests::test_zero_copy_tokens

# Run error tests
cargo test --lib lexer::tests::test_unexpected_character

# Check compilation
cargo check
```

## Dependencies

- `src/error.rs` (LexError)

## Provides

- `TokenKind` enum (all Phase 1 tokens)
- `Token<'src>` struct with lifetime parameter
- `lex(source: &str) -> Result<Vec<Token>, LexError>` function

## Interface Contract with Parser

Parser receives `Vec<Token<'src>>` and can:
- Access `token.kind` for pattern matching
- Access `token.text` for extracting values (e.g., integer parsing, variable names)
- Access `token.line` and `token.column` for error messages
- Tokens are ordered sequentially, ending with `Eof`

## Performance Notes

- Preallocate token vector with `Vec::with_capacity(source.len() / 4)`
- Use `CharIndices` iterator for O(1) UTF-8 aware indexing
- Zero-copy: tokens store `&str` slices, not owned Strings
- Single-pass: O(n) in source length
- Target: ~5μs for 50-byte input

## Notes

- Lifetime parameter `'src` propagates to Parser (Parser<'src>)
- Whitespace (space, tab) is skipped except newlines
- Newlines are significant (statement separators)
- Phase 1: Only ASCII identifiers (UTF-8 strings in Phase 2)
