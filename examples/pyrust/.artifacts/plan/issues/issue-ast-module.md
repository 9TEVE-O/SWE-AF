# Issue: AST Module Implementation

## Summary
Implement Abstract Syntax Tree node definitions for Phase 1 (arithmetic expressions, variable assignment, print statements). Pure data structures with no logic - optimized for arena allocation.

## Context
The AST module defines the intermediate representation between parsing and compilation. It's a leaf module with no dependencies, containing only data structure definitions.

## Architecture Reference
See architecture.md lines 414-512 for complete AST definitions.

## Implementation Requirements

### 1. Create `src/ast.rs` with Exact Types

```rust
/// Top-level program: sequence of statements
#[derive(Debug, Clone, PartialEq)]
pub struct Program {
    pub statements: Vec<Statement>,
}

/// Statement types in Phase 1
#[derive(Debug, Clone, PartialEq)]
pub enum Statement {
    /// Assignment: x = expr
    Assignment {
        target: String,  // Variable name
        value: Expression
    },

    /// Print statement: print(expr)
    Print {
        value: Expression
    },

    /// Expression statement: bare expression (last one becomes return value)
    Expression {
        value: Expression
    },
}

/// Expression types with precedence embedded in structure
#[derive(Debug, Clone, PartialEq)]
pub enum Expression {
    /// Integer literal
    Integer {
        value: i64
    },

    /// Variable reference
    Variable {
        name: String
    },

    /// Binary operation
    BinaryOp {
        op: BinaryOperator,
        left: Box<Expression>,
        right: Box<Expression>,
    },

    /// Unary operation (reserved for future use)
    UnaryOp {
        op: UnaryOperator,
        operand: Box<Expression>,
    },
}

/// Binary operators with defined precedence (enforced during parsing)
///
/// IMPORTANT: In Phase 1, both / and // perform INTEGER DIVISION because
/// we only support i64 type. Phase 2 will distinguish: / returns Float, // returns Integer.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BinaryOperator {
    Add,        // +  (precedence 1)
    Subtract,   // -  (precedence 1)
    Multiply,   // *  (precedence 2)
    Divide,     // /  (precedence 2, INTEGER division in Phase 1, float division in Phase 2)
    FloorDiv,   // // (precedence 2, INTEGER division always)
    Modulo,     // %  (precedence 2)
}

impl BinaryOperator {
    /// Get precedence level (higher = tighter binding)
    pub fn precedence(self) -> u8 {
        match self {
            BinaryOperator::Add | BinaryOperator::Subtract => 1,
            BinaryOperator::Multiply | BinaryOperator::Divide |
            BinaryOperator::FloorDiv | BinaryOperator::Modulo => 2,
        }
    }
}

/// Unary operators (reserved for future extensions, NOT used in Phase 1 parser)
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum UnaryOperator {
    Plus,   // +x
    Minus,  // -x
    Not,    // not x (Phase 2)
}
```

### 2. Unit Tests

Add tests at the bottom of `src/ast.rs`:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_operator_precedence() {
        assert_eq!(BinaryOperator::Add.precedence(), 1);
        assert_eq!(BinaryOperator::Subtract.precedence(), 1);
        assert_eq!(BinaryOperator::Multiply.precedence(), 2);
        assert_eq!(BinaryOperator::Divide.precedence(), 2);
        assert_eq!(BinaryOperator::FloorDiv.precedence(), 2);
        assert_eq!(BinaryOperator::Modulo.precedence(), 2);
    }

    #[test]
    fn test_precedence_ordering() {
        assert!(BinaryOperator::Multiply.precedence() > BinaryOperator::Add.precedence());
        assert!(BinaryOperator::Divide.precedence() > BinaryOperator::Subtract.precedence());
    }

    #[test]
    fn test_ast_construction() {
        // Test that we can construct a simple AST: 2 + 3
        let ast = Program {
            statements: vec![
                Statement::Expression {
                    value: Expression::BinaryOp {
                        op: BinaryOperator::Add,
                        left: Box::new(Expression::Integer { value: 2 }),
                        right: Box::new(Expression::Integer { value: 3 }),
                    }
                }
            ]
        };
        assert_eq!(ast.statements.len(), 1);
    }

    #[test]
    fn test_nested_expression() {
        // Test: 2 + 3 * 4 (parsed with correct precedence)
        let expr = Expression::BinaryOp {
            op: BinaryOperator::Add,
            left: Box::new(Expression::Integer { value: 2 }),
            right: Box::new(Expression::BinaryOp {
                op: BinaryOperator::Multiply,
                left: Box::new(Expression::Integer { value: 3 }),
                right: Box::new(Expression::Integer { value: 4 }),
            }),
        };

        // Verify structure
        if let Expression::BinaryOp { op, left, right } = expr {
            assert_eq!(op, BinaryOperator::Add);
            assert_eq!(*left, Expression::Integer { value: 2 });
            if let Expression::BinaryOp { op: inner_op, .. } = *right {
                assert_eq!(inner_op, BinaryOperator::Multiply);
            } else {
                panic!("Expected nested BinaryOp");
            }
        } else {
            panic!("Expected BinaryOp");
        }
    }

    #[test]
    fn test_assignment_statement() {
        let stmt = Statement::Assignment {
            target: "x".to_string(),
            value: Expression::Integer { value: 10 },
        };

        if let Statement::Assignment { target, value } = stmt {
            assert_eq!(target, "x");
            assert_eq!(value, Expression::Integer { value: 10 });
        } else {
            panic!("Expected Assignment");
        }
    }

    #[test]
    fn test_print_statement() {
        let stmt = Statement::Print {
            value: Expression::Variable { name: "x".to_string() },
        };

        if let Statement::Print { value } = stmt {
            assert_eq!(value, Expression::Variable { name: "x".to_string() });
        } else {
            panic!("Expected Print");
        }
    }

    #[test]
    fn test_clone_and_equality() {
        let expr1 = Expression::Integer { value: 42 };
        let expr2 = expr1.clone();
        assert_eq!(expr1, expr2);

        let stmt1 = Statement::Expression { value: expr1 };
        let stmt2 = stmt1.clone();
        assert_eq!(stmt1, stmt2);
    }
}
```

### 3. Update Cargo.toml

Ensure `src/ast.rs` is declared as a module (will be done in lib.rs by another issue).

## Acceptance Criteria

1. ✅ `src/ast.rs` exists with all types matching architecture exactly
2. ✅ `Program`, `Statement`, `Expression` enums are `Debug + Clone + PartialEq`
3. ✅ `BinaryOperator` and `UnaryOperator` are `Debug + Clone + Copy + PartialEq + Eq`
4. ✅ `BinaryOperator::precedence()` returns correct values (1 for Add/Sub, 2 for Mul/Div/FloorDiv/Mod)
5. ✅ All operators documented with precedence comments
6. ✅ Unit tests pass: `cargo test --lib ast::tests`
7. ✅ Code compiles: `cargo check`

## Testing Instructions

```bash
# Run AST module tests
cargo test --lib ast::tests

# Verify structure
cargo test --lib ast::tests::test_ast_construction -- --nocapture

# Check compilation
cargo check
```

## Dependencies

None - this is a leaf module (pure data structures).

## Provides

- `Program` struct
- `Statement` enum (Assignment, Print, Expression)
- `Expression` enum (Integer, Variable, BinaryOp, UnaryOp)
- `BinaryOperator` enum with `precedence()` method
- `UnaryOperator` enum

## Interface Contract with Parser

The Parser will construct these AST nodes exactly as defined. The structure encodes operator precedence:
- `2 + 3 * 4` → `BinaryOp(Add, 2, BinaryOp(Multiply, 3, 4))`
- `(2 + 3) * 4` → `BinaryOp(Multiply, BinaryOp(Add, 2, 3), 4)`

## Interface Contract with Compiler

The Compiler will pattern-match on these enum variants. Adding new variants in Phase 2 (e.g., `Expression::Call`) will not break existing match arms if they use `_` as fallback.

## Notes

- Phase 1 note: Both `/` and `//` perform integer division (we only have i64 type)
- Phase 2 distinction: `/` will return Float, `//` will return Integer
- `UnaryOp` is defined but not used in Phase 1 parser (reserved for future)
- All expressions use `Box` for recursion (required by Rust)
