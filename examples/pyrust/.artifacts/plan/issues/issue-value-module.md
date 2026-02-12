# Issue: Value Module Implementation

## Summary
Implement runtime value representation with arithmetic operations. Phase 1 supports only integers, but designed for extensibility to floats, strings, booleans in Phase 2.

## Context
The Value module defines the runtime representation of Python values and implements all arithmetic operations with proper error handling (overflow, division by zero). It's used by the VM during bytecode execution.

## Architecture Reference
See architecture.md lines 881-987 for complete Value definitions.

## Implementation Requirements

### 1. Create `src/value.rs` with Exact Types

```rust
use std::fmt;
use crate::ast::{BinaryOperator, UnaryOperator};
use crate::error::RuntimeError;

/// Runtime value type
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Value {
    Integer(i64),
    // Future: Float(f64), String(Rc<str>), Bool(bool), None, ...
}

impl Value {
    /// Extract integer or panic (safe in Phase 1 due to type system)
    pub fn as_integer(&self) -> i64 {
        match self {
            Value::Integer(n) => *n,
            // Phase 2: return Err(TypeError)
        }
    }

    /// Perform binary operation
    ///
    /// IMPORTANT: In Phase 1, both / and // perform integer division because
    /// we only have i64 type. Phase 2 will distinguish:
    /// - / returns Float (true division: 5 / 2 = 2.5)
    /// - // returns Integer (floor division: 5 // 2 = 2)
    pub fn binary_op(&self, op: BinaryOperator, other: &Value) -> Result<Value, RuntimeError> {
        let left = self.as_integer();
        let right = other.as_integer();

        let result = match op {
            BinaryOperator::Add => left.checked_add(right),
            BinaryOperator::Subtract => left.checked_sub(right),
            BinaryOperator::Multiply => left.checked_mul(right),
            // Both / and // perform integer division in Phase 1
            BinaryOperator::Divide | BinaryOperator::FloorDiv => {
                if right == 0 {
                    return Err(RuntimeError {
                        message: "Division by zero".to_string(),
                        instruction_index: 0, // Will be overwritten by VM with actual index
                    });
                }
                left.checked_div(right)
            }
            BinaryOperator::Modulo => {
                if right == 0 {
                    return Err(RuntimeError {
                        message: "Modulo by zero".to_string(),
                        instruction_index: 0,
                    });
                }
                left.checked_rem(right)
            }
        };

        match result {
            Some(n) => Ok(Value::Integer(n)),
            None => Err(RuntimeError {
                message: format!("Integer overflow in operation: {} {:?} {}", left, op, right),
                instruction_index: 0,
            }),
        }
    }

    /// Perform unary operation (reserved for future use)
    pub fn unary_op(&self, op: UnaryOperator) -> Result<Value, RuntimeError> {
        let n = self.as_integer();
        match op {
            UnaryOperator::Plus => Ok(Value::Integer(n)),
            UnaryOperator::Minus => n.checked_neg()
                .map(Value::Integer)
                .ok_or_else(|| RuntimeError {
                    message: format!("Integer overflow in negation: {}", n),
                    instruction_index: 0,
                }),
            UnaryOperator::Not => {
                // Phase 2: convert to bool and negate
                Err(RuntimeError {
                    message: "Logical not is not supported in Phase 1".to_string(),
                    instruction_index: 0,
                })
            }
        }
    }
}

impl fmt::Display for Value {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Value::Integer(n) => write!(f, "{}", n),
        }
    }
}
```

### 2. Unit Tests

Add tests at the bottom of `src/value.rs`:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_integer_addition() {
        let left = Value::Integer(2);
        let right = Value::Integer(3);
        let result = left.binary_op(BinaryOperator::Add, &right).unwrap();
        assert_eq!(result, Value::Integer(5));
    }

    #[test]
    fn test_integer_subtraction() {
        let left = Value::Integer(10);
        let right = Value::Integer(3);
        let result = left.binary_op(BinaryOperator::Subtract, &right).unwrap();
        assert_eq!(result, Value::Integer(7));
    }

    #[test]
    fn test_integer_multiplication() {
        let left = Value::Integer(3);
        let right = Value::Integer(4);
        let result = left.binary_op(BinaryOperator::Multiply, &right).unwrap();
        assert_eq!(result, Value::Integer(12));
    }

    #[test]
    fn test_integer_division() {
        let left = Value::Integer(20);
        let right = Value::Integer(4);
        let result = left.binary_op(BinaryOperator::Divide, &right).unwrap();
        assert_eq!(result, Value::Integer(5));
    }

    #[test]
    fn test_integer_floor_division() {
        let left = Value::Integer(17);
        let right = Value::Integer(5);
        let result = left.binary_op(BinaryOperator::FloorDiv, &right).unwrap();
        assert_eq!(result, Value::Integer(3));
    }

    #[test]
    fn test_integer_modulo() {
        let left = Value::Integer(17);
        let right = Value::Integer(5);
        let result = left.binary_op(BinaryOperator::Modulo, &right).unwrap();
        assert_eq!(result, Value::Integer(2));
    }

    #[test]
    fn test_division_by_zero() {
        let left = Value::Integer(10);
        let right = Value::Integer(0);
        let result = left.binary_op(BinaryOperator::Divide, &right);
        assert!(result.is_err());
        let err = result.unwrap_err();
        assert_eq!(err.message, "Division by zero");
    }

    #[test]
    fn test_modulo_by_zero() {
        let left = Value::Integer(10);
        let right = Value::Integer(0);
        let result = left.binary_op(BinaryOperator::Modulo, &right);
        assert!(result.is_err());
        let err = result.unwrap_err();
        assert_eq!(err.message, "Modulo by zero");
    }

    #[test]
    fn test_integer_overflow_add() {
        let left = Value::Integer(i64::MAX);
        let right = Value::Integer(1);
        let result = left.binary_op(BinaryOperator::Add, &right);
        assert!(result.is_err());
        let err = result.unwrap_err();
        assert!(err.message.contains("Integer overflow"));
    }

    #[test]
    fn test_integer_overflow_multiply() {
        let left = Value::Integer(i64::MAX);
        let right = Value::Integer(2);
        let result = left.binary_op(BinaryOperator::Multiply, &right);
        assert!(result.is_err());
    }

    #[test]
    fn test_unary_plus() {
        let val = Value::Integer(42);
        let result = val.unary_op(UnaryOperator::Plus).unwrap();
        assert_eq!(result, Value::Integer(42));
    }

    #[test]
    fn test_unary_minus() {
        let val = Value::Integer(42);
        let result = val.unary_op(UnaryOperator::Minus).unwrap();
        assert_eq!(result, Value::Integer(-42));
    }

    #[test]
    fn test_unary_minus_overflow() {
        let val = Value::Integer(i64::MIN);
        let result = val.unary_op(UnaryOperator::Minus);
        assert!(result.is_err());
        let err = result.unwrap_err();
        assert!(err.message.contains("Integer overflow in negation"));
    }

    #[test]
    fn test_unary_not_unsupported() {
        let val = Value::Integer(1);
        let result = val.unary_op(UnaryOperator::Not);
        assert!(result.is_err());
        let err = result.unwrap_err();
        assert!(err.message.contains("not supported in Phase 1"));
    }

    #[test]
    fn test_display_integer() {
        let val = Value::Integer(42);
        assert_eq!(format!("{}", val), "42");

        let val = Value::Integer(-123);
        assert_eq!(format!("{}", val), "-123");

        let val = Value::Integer(0);
        assert_eq!(format!("{}", val), "0");
    }

    #[test]
    fn test_as_integer() {
        let val = Value::Integer(42);
        assert_eq!(val.as_integer(), 42);
    }

    #[test]
    fn test_negative_division() {
        // Test negative number division (should match Python semantics)
        let left = Value::Integer(-17);
        let right = Value::Integer(5);
        let result = left.binary_op(BinaryOperator::FloorDiv, &right).unwrap();
        assert_eq!(result, Value::Integer(-4)); // -17 / 5 = -3.4, floor = -4
    }

    #[test]
    fn test_negative_modulo() {
        // Test negative number modulo
        let left = Value::Integer(-17);
        let right = Value::Integer(5);
        let result = left.binary_op(BinaryOperator::Modulo, &right).unwrap();
        // Rust's rem matches Python's modulo for negative numbers
        assert_eq!(result, Value::Integer(-2));
    }
}
```

### 3. Module Declaration

Add to `src/lib.rs` (will be created by another issue):
```rust
pub mod value;
```

## Acceptance Criteria

1. ✅ `src/value.rs` exists with Value enum matching architecture exactly
2. ✅ `binary_op()` implements all 6 operators (Add, Subtract, Multiply, Divide, FloorDiv, Modulo)
3. ✅ Division by zero returns `RuntimeError` with message "Division by zero"
4. ✅ Integer overflow returns `RuntimeError` with descriptive message
5. ✅ `unary_op()` implements Plus and Minus, Not returns error in Phase 1
6. ✅ `Display` trait formats integers correctly (no trailing decimals)
7. ✅ All unit tests pass: `cargo test --lib value::tests`
8. ✅ Code compiles: `cargo check`

## Testing Instructions

```bash
# Run value module tests
cargo test --lib value::tests

# Run specific overflow tests
cargo test --lib value::tests::test_integer_overflow

# Run division tests
cargo test --lib value::tests::test_division

# Check compilation
cargo check
```

## Dependencies

- `src/error.rs` (RuntimeError)
- `src/ast.rs` (BinaryOperator, UnaryOperator)

## Provides

- `Value` enum with Integer variant
- `Value::binary_op()` method for arithmetic operations
- `Value::unary_op()` method for unary operations
- `Value::as_integer()` helper for extracting i64
- `Display` implementation for value formatting

## Interface Contract with VM

The VM will call `binary_op()` and `unary_op()` during bytecode execution. These methods:
- Return `Result<Value, RuntimeError>` for proper error propagation
- Set `instruction_index: 0` in errors (VM will overwrite with actual PC)
- Use `checked_*` operations to detect overflow

## Interface Contract with Compiler

The Compiler doesn't interact with Value directly - it only generates bytecode that references BinaryOperator and UnaryOperator enums.

## Notes

- Phase 1: Both `/` and `//` perform integer division (we only have i64)
- Phase 2: `/` will return Float, `//` will return Integer
- All arithmetic uses `checked_*` methods to prevent silent overflow
- Error messages include operator and operands for debugging
- `instruction_index: 0` is a placeholder - VM sets the real value
