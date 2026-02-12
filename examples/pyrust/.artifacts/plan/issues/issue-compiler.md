# Issue: Compiler Implementation

## Summary
Implement AST to bytecode compiler with register allocation. Single-pass walk with SetResult emission rules for correct output format handling.

## Context
The compiler transforms parsed AST into compact bytecode. It must emit SetResult ONLY for expression statements (not assignments or prints) to match the output format specification. This is critical for AC compliance.

## Architecture Reference
See architecture.md lines 614-730 for complete compiler specification.

## Implementation Requirements

### 1. Create `src/compiler.rs` with Exact Implementation

```rust
use crate::ast::*;
use crate::bytecode::*;
use crate::error::CompileError;

/// Compile AST to bytecode
///
/// # Performance
/// Target: ~15μs for 10-node AST
///
/// # Example
/// ```
/// let ast = parser::parse(tokens)?;
/// let bytecode = compiler::compile(&ast)?;
/// ```
pub fn compile(program: &Program) -> Result<Bytecode, CompileError> {
    let mut compiler = Compiler::new();
    compiler.compile_program(program)
}

// Internal implementation
struct Compiler {
    bytecode: BytecodeBuilder,
    register_counter: u8, // Next available register
}

impl Compiler {
    fn new() -> Self {
        Compiler {
            bytecode: BytecodeBuilder::new(),
            register_counter: 0,
        }
    }

    fn compile_program(&mut self, program: &Program) -> Result<Bytecode, CompileError> {
        for stmt in &program.statements {
            self.compile_statement(stmt)?;
        }
        Ok(self.bytecode.build())
    }

    /// Compile statement according to SetResult rules:
    /// - Assignment: NO SetResult
    /// - Print: NO SetResult
    /// - Expression: YES SetResult
    fn compile_statement(&mut self, stmt: &Statement) -> Result<(), CompileError> {
        match stmt {
            Statement::Assignment { target, value } => {
                let reg = self.compile_expression(value)?;
                self.bytecode.emit_store_var(target, reg);
                // NO emit_set_result() - assignments don't set result
                Ok(())
            }
            Statement::Print { value } => {
                let reg = self.compile_expression(value)?;
                self.bytecode.emit_print(reg);
                // NO emit_set_result() - prints don't set result
                Ok(())
            }
            Statement::Expression { value } => {
                let reg = self.compile_expression(value)?;
                self.bytecode.emit_set_result(reg);
                // YES emit_set_result() - expression statements set result
                Ok(())
            }
        }
    }

    /// Compile expression and return register holding result
    fn compile_expression(&mut self, expr: &Expression) -> Result<u8, CompileError> {
        match expr {
            Expression::Integer { value } => {
                let reg = self.allocate_register()?;
                self.bytecode.emit_load_const(reg, *value);
                Ok(reg)
            }
            Expression::Variable { name } => {
                let reg = self.allocate_register()?;
                self.bytecode.emit_load_var(reg, name);
                Ok(reg)
            }
            Expression::BinaryOp { op, left, right } => {
                let left_reg = self.compile_expression(left)?;
                let right_reg = self.compile_expression(right)?;
                let result_reg = self.allocate_register()?;
                self.bytecode.emit_binary_op(result_reg, *op, left_reg, right_reg);
                Ok(result_reg)
            }
            Expression::UnaryOp { op, operand } => {
                let operand_reg = self.compile_expression(operand)?;
                let result_reg = self.allocate_register()?;
                self.bytecode.emit_unary_op(result_reg, *op, operand_reg);
                Ok(result_reg)
            }
        }
    }

    fn allocate_register(&mut self) -> Result<u8, CompileError> {
        if self.register_counter >= 255 {
            return Err(CompileError {
                message: "Register overflow: expression too complex (max 255 registers)".to_string(),
            });
        }
        let reg = self.register_counter;
        self.register_counter += 1;
        Ok(reg)
    }
}
```

### 2. Unit Tests

Add tests at the bottom of `src/compiler.rs`:

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use crate::lexer;
    use crate::parser;

    fn compile_code(code: &str) -> Result<Bytecode, CompileError> {
        let tokens = lexer::lex(code).unwrap();
        let ast = parser::parse(tokens).unwrap();
        compile(&ast)
    }

    #[test]
    fn test_compile_simple_integer() {
        let bytecode = compile_code("42").unwrap();

        // Should have: LoadConst + SetResult + Halt
        assert_eq!(bytecode.instructions.len(), 3);

        assert!(matches!(bytecode.instructions[0], Instruction::LoadConst { dest: 0, value_index: 0 }));
        assert!(matches!(bytecode.instructions[1], Instruction::SetResult { src: 0 }));
        assert_eq!(bytecode.instructions[2], Instruction::Halt);

        assert_eq!(bytecode.constants.len(), 1);
        assert_eq!(bytecode.constants[0], 42);
    }

    #[test]
    fn test_compile_addition() {
        let bytecode = compile_code("2 + 3").unwrap();

        // Should have: LoadConst(R0, 2), LoadConst(R1, 3), BinaryOp(R2, Add, R0, R1), SetResult(R2), Halt
        assert_eq!(bytecode.instructions.len(), 5);

        assert!(matches!(bytecode.instructions[0], Instruction::LoadConst { dest: 0, .. }));
        assert!(matches!(bytecode.instructions[1], Instruction::LoadConst { dest: 1, .. }));
        assert!(matches!(bytecode.instructions[2], Instruction::BinaryOp { dest: 2, op: BinaryOperator::Add, left: 0, right: 1 }));
        assert!(matches!(bytecode.instructions[3], Instruction::SetResult { src: 2 }));

        assert_eq!(bytecode.constants[0], 2);
        assert_eq!(bytecode.constants[1], 3);
    }

    #[test]
    fn test_compile_assignment_no_setresult() {
        let bytecode = compile_code("x = 10").unwrap();

        // Should have: LoadConst(R0, 10), StoreVar(x, R0), Halt
        // NO SetResult instruction
        assert_eq!(bytecode.instructions.len(), 3);

        assert!(matches!(bytecode.instructions[0], Instruction::LoadConst { .. }));
        assert!(matches!(bytecode.instructions[1], Instruction::StoreVar { .. }));
        assert_eq!(bytecode.instructions[2], Instruction::Halt);

        // Verify no SetResult
        for instr in &bytecode.instructions {
            assert!(!matches!(instr, Instruction::SetResult { .. }));
        }
    }

    #[test]
    fn test_compile_print_no_setresult() {
        let bytecode = compile_code("print(42)").unwrap();

        // Should have: LoadConst(R0, 42), Print(R0), Halt
        // NO SetResult instruction
        assert_eq!(bytecode.instructions.len(), 3);

        assert!(matches!(bytecode.instructions[0], Instruction::LoadConst { .. }));
        assert!(matches!(bytecode.instructions[1], Instruction::Print { src: 0 }));
        assert_eq!(bytecode.instructions[2], Instruction::Halt);

        // Verify no SetResult
        for instr in &bytecode.instructions {
            assert!(!matches!(instr, Instruction::SetResult { .. }));
        }
    }

    #[test]
    fn test_compile_expression_statement_has_setresult() {
        let bytecode = compile_code("x = 10\nx").unwrap();

        // First statement: x = 10 (NO SetResult)
        // Second statement: x (YES SetResult)

        let setresult_count = bytecode.instructions.iter()
            .filter(|i| matches!(i, Instruction::SetResult { .. }))
            .count();

        assert_eq!(setresult_count, 1, "Should have exactly 1 SetResult for expression statement");
    }

    #[test]
    fn test_compile_variable_load() {
        let bytecode = compile_code("x = 10\nx + 5").unwrap();

        assert_eq!(bytecode.var_names.len(), 1);
        assert_eq!(bytecode.var_names[0], "x");

        // Should contain LoadVar instruction
        let has_loadvar = bytecode.instructions.iter()
            .any(|i| matches!(i, Instruction::LoadVar { .. }));
        assert!(has_loadvar);
    }

    #[test]
    fn test_compile_all_operators() {
        let test_cases = vec![
            ("2 + 3", BinaryOperator::Add),
            ("2 - 3", BinaryOperator::Subtract),
            ("2 * 3", BinaryOperator::Multiply),
            ("2 / 3", BinaryOperator::Divide),
            ("2 // 3", BinaryOperator::FloorDiv),
            ("2 % 3", BinaryOperator::Modulo),
        ];

        for (code, expected_op) in test_cases {
            let bytecode = compile_code(code).unwrap();

            let has_op = bytecode.instructions.iter().any(|i| {
                if let Instruction::BinaryOp { op, .. } = i {
                    *op == expected_op
                } else {
                    false
                }
            });

            assert!(has_op, "Failed to find {:?} in bytecode for: {}", expected_op, code);
        }
    }

    #[test]
    fn test_register_allocation() {
        let bytecode = compile_code("2 + 3 * 4").unwrap();

        // Expression: 2 + (3 * 4)
        // Should allocate: R0=2, R1=3, R2=4, R3=(R1*R2), R4=(R0+R3)
        // Total 5 registers used

        // Count unique destination registers
        let mut max_reg = 0;
        for instr in &bytecode.instructions {
            match instr {
                Instruction::LoadConst { dest, .. } |
                Instruction::LoadVar { dest, .. } |
                Instruction::BinaryOp { dest, .. } |
                Instruction::UnaryOp { dest, .. } => {
                    max_reg = max_reg.max(*dest);
                }
                _ => {}
            }
        }

        assert!(max_reg >= 4, "Should allocate at least 5 registers (0-4)");
    }

    #[test]
    fn test_constant_pool() {
        let bytecode = compile_code("1 + 2 + 3").unwrap();

        assert_eq!(bytecode.constants.len(), 3);
        assert_eq!(bytecode.constants[0], 1);
        assert_eq!(bytecode.constants[1], 2);
        assert_eq!(bytecode.constants[2], 3);
    }

    #[test]
    fn test_multiple_statements() {
        let bytecode = compile_code("x = 10\nprint(x)\nx + 5").unwrap();

        // Should have instructions for all three statements + Halt
        assert!(bytecode.instructions.len() > 4);

        // Should have exactly 1 SetResult (from "x + 5")
        let setresult_count = bytecode.instructions.iter()
            .filter(|i| matches!(i, Instruction::SetResult { .. }))
            .count();
        assert_eq!(setresult_count, 1);

        // Should have 1 Print instruction
        let print_count = bytecode.instructions.iter()
            .filter(|i| matches!(i, Instruction::Print { .. }))
            .count();
        assert_eq!(print_count, 1);

        // Should have 1 StoreVar instruction
        let storevar_count = bytecode.instructions.iter()
            .filter(|i| matches!(i, Instruction::StoreVar { .. }))
            .count();
        assert_eq!(storevar_count, 1);
    }

    #[test]
    fn test_nested_expressions() {
        let bytecode = compile_code("(2 + 3) * (4 + 5)").unwrap();

        // Should compile without error
        assert!(bytecode.instructions.len() > 0);

        // Should have multiple BinaryOp instructions
        let binop_count = bytecode.instructions.iter()
            .filter(|i| matches!(i, Instruction::BinaryOp { .. }))
            .count();
        assert_eq!(binop_count, 3, "Should have 3 binary ops: 2+3, 4+5, result1*result2");
    }

    #[test]
    fn test_empty_program() {
        let bytecode = compile_code("").unwrap();

        // Should only have Halt
        assert_eq!(bytecode.instructions.len(), 1);
        assert_eq!(bytecode.instructions[0], Instruction::Halt);
    }

    #[test]
    fn test_complex_expression() {
        let bytecode = compile_code("x = 2 + 3 * 4 - 5 / 2").unwrap();

        // Should compile without error
        assert!(bytecode.instructions.len() > 0);

        // Should have multiple operations
        let binop_count = bytecode.instructions.iter()
            .filter(|i| matches!(i, Instruction::BinaryOp { .. }))
            .count();
        assert!(binop_count >= 4, "Should have at least 4 binary operations");
    }

    #[test]
    fn test_setresult_only_on_expression_statements() {
        // Test various statement types
        let test_cases = vec![
            ("x = 10", 0),           // Assignment: 0 SetResult
            ("print(10)", 0),        // Print: 0 SetResult
            ("10", 1),               // Expression: 1 SetResult
            ("x = 10\n20", 1),       // Assignment + Expression: 1 SetResult
            ("10\n20\n30", 3),       // Three expressions: 3 SetResult
        ];

        for (code, expected_count) in test_cases {
            let bytecode = compile_code(code).unwrap();

            let setresult_count = bytecode.instructions.iter()
                .filter(|i| matches!(i, Instruction::SetResult { .. }))
                .count();

            assert_eq!(setresult_count, expected_count,
                "SetResult count mismatch for code: {}", code);
        }
    }
}
```

## Acceptance Criteria

1. ✅ `src/compiler.rs` exists with compile() function matching architecture
2. ✅ Implements single-pass AST to bytecode compilation
3. ✅ Assignment statements emit StoreVar WITHOUT SetResult
4. ✅ Print statements emit Print WITHOUT SetResult
5. ✅ Expression statements emit SetResult
6. ✅ Register allocation works correctly (sequential allocation)
7. ✅ All operators compile to correct BinaryOp instructions
8. ✅ Variable names deduplicated in bytecode var_names pool
9. ✅ Unit tests pass: `cargo test --lib compiler::tests`
10. ✅ Code compiles: `cargo check`

## Testing Instructions

```bash
# Run compiler module tests
cargo test --lib compiler::tests

# Run SetResult tests (critical for output format)
cargo test --lib compiler::tests::test_setresult

# Run register allocation tests
cargo test --lib compiler::tests::test_register_allocation

# Check compilation
cargo check
```

## Dependencies

- `src/ast.rs` (Program, Statement, Expression, BinaryOperator, UnaryOperator)
- `src/bytecode.rs` (Bytecode, BytecodeBuilder, Instruction)
- `src/error.rs` (CompileError)

## Provides

- `compile(program: &Program) -> Result<Bytecode, CompileError>` function

## Interface Contract with Parser

Receives AST (Program) from parser:
- Walks through statements sequentially
- Recursively compiles expressions
- No modification to AST (read-only)

## Interface Contract with VM

Produces Bytecode for VM:
- Instructions vector with Halt at end
- Constants pool with all integer literals
- Variable names pool with deduplicated names
- SetResult appears ONLY after expression statements

## Critical Implementation Notes

**SetResult Emission Rules** (BLOCKER 2 Resolution):

This is the MOST CRITICAL part of the compiler. The output format specification depends on correct SetResult emission:

- `Statement::Assignment { .. }` → compile expression, emit StoreVar, **NO SetResult**
- `Statement::Print { .. }` → compile expression, emit Print, **NO SetResult**
- `Statement::Expression { .. }` → compile expression, emit SetResult, **YES SetResult**

**Why this matters:**
- VM tracks `result: Option<Value>`
- SetResult instruction sets `self.result = Some(register_value)`
- API formats output as `{stdout}{result_if_some}`
- Without correct SetResult emission, output format edge cases will fail

**Test this thoroughly:**
```rust
// These are CRITICAL test cases:
"x = 10"           → NO SetResult → output ""
"print(10)"        → NO SetResult → output "10\n"
"10"               → YES SetResult → output "10"
"x = 10\nx"        → SetResult for x only → output "10"
"print(10)\n20"    → SetResult for 20 only → output "10\n20"
```

## Performance Notes

- Single-pass compilation: O(n) in AST node count
- Sequential register allocation: No liveness analysis (Phase 1)
- Target: ~15μs for 10-node AST
- No optimization passes (constant folding deferred to Phase 2)

## Notes

- Phase 1: Naive sequential register allocation (R0, R1, R2, ...)
- Phase 2: Can add register reuse with liveness analysis
- Register overflow error at 255 registers (sufficient for Phase 1)
- Bytecode builder handles constant and variable name deduplication
