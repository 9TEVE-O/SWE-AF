# issue-07-negative-number-parsing: Add negative number literal support to parser

## Description
Add unary minus operator handling to the parser's `parse_primary()` function to support negative number literals like `-42` and `-30`. This fixes two failing tests that expect negative numbers to parse and evaluate correctly.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section 4.2 (Negative Number Parsing) for:
- Exact location in `parse_primary()` to add the `TokenKind::Minus` match case
- Precedence value (100) for unary operators to ensure correct parsing of `-2 + 3`
- `Expression::UnaryOp` structure with `UnaryOperator::Neg` variant
- Error handling for invalid unary operator operands

## Interface Contracts
- Implements: `TokenKind::Minus` case in `parse_primary()` match statement
- Returns: `Expression::UnaryOp { op: UnaryOperator::Neg, operand: Box<Expression> }`
- Exports: Negative number parsing capability for literals and expressions
- Consumes: `TokenKind::Minus` from lexer, `UnaryOperator::Neg` from AST
- Consumed by: Compiler for bytecode generation, VM for execution

## Files
- **Modify**: `src/parser.rs` (add `TokenKind::Minus` case in `parse_primary()` at line ~304)

## Dependencies
- None (lexer already produces `TokenKind::Minus` tokens)

## Provides
- Negative number literal parsing support (`-42`, `-30`)
- Fixed `test_function_with_negative_numbers`
- Fixed `test_function_with_negative_parameters`

## Acceptance Criteria
- [ ] AC4.3: `test_function_with_negative_numbers` returns -42
- [ ] AC4.3: `test_function_with_negative_parameters` returns -30
- [ ] AC4.2: All 664 currently passing tests still pass (no regressions)

## Testing Strategy

### Test Files
- `tests/test_functions.rs`: Contains `test_function_with_negative_numbers` and `test_function_with_negative_parameters`

### Test Categories
- **Unit tests**: Verify `parse_primary()` correctly parses unary minus tokens
- **Functional tests**: End-to-end execution of functions with negative number literals and parameters
- **Edge cases**: Nested unary operators (`--5`), unary in expressions (`-2 + 3`), precedence validation

### Run Command
```bash
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 cargo test test_function_with_negative_numbers test_function_with_negative_parameters --release
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 cargo test --release
```
