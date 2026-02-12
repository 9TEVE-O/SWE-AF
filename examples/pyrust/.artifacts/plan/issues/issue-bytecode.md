# Issue: Bytecode Module Implementation

## Summary
Implement compact bytecode instruction format and builder. Register-based VM instructions optimized for cache locality with constant pool and variable name table.

## Context
The bytecode module defines the instruction format executed by the VM. It uses a register-based architecture (not stack-based) for 30-40% fewer instructions. The builder manages constant pools and variable name deduplication.

## Architecture Reference
See architecture.md lines 732-878 for complete bytecode definitions.

## Implementation Requirements

### 1. Create `src/bytecode.rs` with Exact Types

```rust
use crate::ast::{BinaryOperator, UnaryOperator};

/// Bytecode instruction
///
/// Note: Rust enum with discriminant + largest variant determines size.
/// Typical size: 8-16 bytes per instruction (cache-friendly for small programs).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Instruction {
    /// Load constant integer into register
    /// Args: dest_reg, value_index
    LoadConst { dest: u8, value_index: u16 },

    /// Load variable into register
    /// Args: dest_reg, var_name_index
    LoadVar { dest: u8, var_index: u16 },

    /// Store register value to variable
    /// Args: var_name_index, src_reg
    StoreVar { var_index: u16, src: u8 },

    /// Binary operation
    /// Args: dest_reg, op, left_reg, right_reg
    BinaryOp { dest: u8, op: BinaryOperator, left: u8, right: u8 },

    /// Unary operation
    /// Args: dest_reg, op, operand_reg
    UnaryOp { dest: u8, op: UnaryOperator, operand: u8 },

    /// Print register value
    /// Args: src_reg
    Print { src: u8 },

    /// Set final result value (only emitted for expression statements)
    /// Args: src_reg
    SetResult { src: u8 },

    /// Halt execution
    Halt,
}

/// Compiled bytecode with constant pool and variable table
#[derive(Debug, Clone)]
pub struct Bytecode {
    pub instructions: Vec<Instruction>,
    pub constants: Vec<i64>,           // Constant pool for integers
    pub var_names: Vec<String>,        // Variable name string pool
}

impl Bytecode {
    pub fn new() -> Self {
        Bytecode {
            instructions: Vec::new(),
            constants: Vec::new(),
            var_names: Vec::new(),
        }
    }
}

/// Builder for constructing bytecode
pub struct BytecodeBuilder {
    bytecode: Bytecode,
    var_name_indices: std::collections::HashMap<String, u16>,
}

impl BytecodeBuilder {
    pub fn new() -> Self {
        BytecodeBuilder {
            bytecode: Bytecode::new(),
            var_name_indices: std::collections::HashMap::new(),
        }
    }

    pub fn emit_load_const(&mut self, dest: u8, value: i64) {
        let index = self.add_constant(value);
        self.bytecode.instructions.push(Instruction::LoadConst { dest, value_index: index });
    }

    pub fn emit_load_var(&mut self, dest: u8, name: &str) {
        let index = self.get_or_add_var_name(name);
        self.bytecode.instructions.push(Instruction::LoadVar { dest, var_index: index });
    }

    pub fn emit_store_var(&mut self, name: &str, src: u8) {
        let index = self.get_or_add_var_name(name);
        self.bytecode.instructions.push(Instruction::StoreVar { var_index: index, src });
    }

    pub fn emit_binary_op(&mut self, dest: u8, op: BinaryOperator, left: u8, right: u8) {
        self.bytecode.instructions.push(Instruction::BinaryOp { dest, op, left, right });
    }

    pub fn emit_unary_op(&mut self, dest: u8, op: UnaryOperator, operand: u8) {
        self.bytecode.instructions.push(Instruction::UnaryOp { dest, op, operand });
    }

    pub fn emit_print(&mut self, src: u8) {
        self.bytecode.instructions.push(Instruction::Print { src });
    }

    pub fn emit_set_result(&mut self, src: u8) {
        self.bytecode.instructions.push(Instruction::SetResult { src });
    }

    pub fn build(mut self) -> Bytecode {
        self.bytecode.instructions.push(Instruction::Halt);
        self.bytecode
    }

    fn add_constant(&mut self, value: i64) -> u16 {
        let index = self.bytecode.constants.len();
        self.bytecode.constants.push(value);
        index as u16
    }

    fn get_or_add_var_name(&mut self, name: &str) -> u16 {
        if let Some(&index) = self.var_name_indices.get(name) {
            return index;
        }
        let index = self.bytecode.var_names.len() as u16;
        self.bytecode.var_names.push(name.to_string());
        self.var_name_indices.insert(name.to_string(), index);
        index
    }
}
```

### 2. Unit Tests

Add tests at the bottom of `src/bytecode.rs`:

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{BinaryOperator, UnaryOperator};

    #[test]
    fn test_bytecode_builder_new() {
        let builder = BytecodeBuilder::new();
        assert_eq!(builder.bytecode.instructions.len(), 0);
        assert_eq!(builder.bytecode.constants.len(), 0);
        assert_eq!(builder.bytecode.var_names.len(), 0);
    }

    #[test]
    fn test_emit_load_const() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_load_const(0, 42);

        assert_eq!(builder.bytecode.constants.len(), 1);
        assert_eq!(builder.bytecode.constants[0], 42);
        assert_eq!(builder.bytecode.instructions.len(), 1);

        if let Instruction::LoadConst { dest, value_index } = builder.bytecode.instructions[0] {
            assert_eq!(dest, 0);
            assert_eq!(value_index, 0);
        } else {
            panic!("Expected LoadConst instruction");
        }
    }

    #[test]
    fn test_emit_load_var() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_load_var(0, "x");

        assert_eq!(builder.bytecode.var_names.len(), 1);
        assert_eq!(builder.bytecode.var_names[0], "x");

        if let Instruction::LoadVar { dest, var_index } = builder.bytecode.instructions[0] {
            assert_eq!(dest, 0);
            assert_eq!(var_index, 0);
        } else {
            panic!("Expected LoadVar instruction");
        }
    }

    #[test]
    fn test_emit_store_var() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_store_var("x", 0);

        assert_eq!(builder.bytecode.var_names.len(), 1);
        assert_eq!(builder.bytecode.var_names[0], "x");

        if let Instruction::StoreVar { var_index, src } = builder.bytecode.instructions[0] {
            assert_eq!(var_index, 0);
            assert_eq!(src, 0);
        } else {
            panic!("Expected StoreVar instruction");
        }
    }

    #[test]
    fn test_variable_name_deduplication() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_load_var(0, "x");
        builder.emit_load_var(1, "x");
        builder.emit_load_var(2, "y");

        // Should only have 2 unique variable names
        assert_eq!(builder.bytecode.var_names.len(), 2);
        assert_eq!(builder.bytecode.var_names[0], "x");
        assert_eq!(builder.bytecode.var_names[1], "y");

        // First two loads should reference index 0, third should reference index 1
        if let Instruction::LoadVar { var_index, .. } = builder.bytecode.instructions[0] {
            assert_eq!(var_index, 0);
        }
        if let Instruction::LoadVar { var_index, .. } = builder.bytecode.instructions[1] {
            assert_eq!(var_index, 0);
        }
        if let Instruction::LoadVar { var_index, .. } = builder.bytecode.instructions[2] {
            assert_eq!(var_index, 1);
        }
    }

    #[test]
    fn test_emit_binary_op() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_binary_op(2, BinaryOperator::Add, 0, 1);

        if let Instruction::BinaryOp { dest, op, left, right } = builder.bytecode.instructions[0] {
            assert_eq!(dest, 2);
            assert_eq!(op, BinaryOperator::Add);
            assert_eq!(left, 0);
            assert_eq!(right, 1);
        } else {
            panic!("Expected BinaryOp instruction");
        }
    }

    #[test]
    fn test_emit_unary_op() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_unary_op(1, UnaryOperator::Minus, 0);

        if let Instruction::UnaryOp { dest, op, operand } = builder.bytecode.instructions[0] {
            assert_eq!(dest, 1);
            assert_eq!(op, UnaryOperator::Minus);
            assert_eq!(operand, 0);
        } else {
            panic!("Expected UnaryOp instruction");
        }
    }

    #[test]
    fn test_emit_print() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_print(0);

        if let Instruction::Print { src } = builder.bytecode.instructions[0] {
            assert_eq!(src, 0);
        } else {
            panic!("Expected Print instruction");
        }
    }

    #[test]
    fn test_emit_set_result() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_set_result(0);

        if let Instruction::SetResult { src } = builder.bytecode.instructions[0] {
            assert_eq!(src, 0);
        } else {
            panic!("Expected SetResult instruction");
        }
    }

    #[test]
    fn test_build_adds_halt() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_load_const(0, 42);

        let bytecode = builder.build();

        assert_eq!(bytecode.instructions.len(), 2);
        assert_eq!(bytecode.instructions[1], Instruction::Halt);
    }

    #[test]
    fn test_constant_pool() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_load_const(0, 10);
        builder.emit_load_const(1, 20);
        builder.emit_load_const(2, 10); // Duplicate value

        // Duplicates are NOT deduplicated (each gets own pool entry)
        assert_eq!(builder.bytecode.constants.len(), 3);
        assert_eq!(builder.bytecode.constants[0], 10);
        assert_eq!(builder.bytecode.constants[1], 20);
        assert_eq!(builder.bytecode.constants[2], 10);
    }

    #[test]
    fn test_instruction_equality() {
        let instr1 = Instruction::LoadConst { dest: 0, value_index: 1 };
        let instr2 = Instruction::LoadConst { dest: 0, value_index: 1 };
        let instr3 = Instruction::LoadConst { dest: 1, value_index: 1 };

        assert_eq!(instr1, instr2);
        assert_ne!(instr1, instr3);
    }

    #[test]
    fn test_complex_bytecode_sequence() {
        // Build bytecode for: x = 2 + 3
        let mut builder = BytecodeBuilder::new();

        builder.emit_load_const(0, 2);              // R0 = 2
        builder.emit_load_const(1, 3);              // R1 = 3
        builder.emit_binary_op(2, BinaryOperator::Add, 0, 1);  // R2 = R0 + R1
        builder.emit_store_var("x", 2);             // x = R2

        let bytecode = builder.build();

        assert_eq!(bytecode.instructions.len(), 5); // 4 instructions + Halt
        assert_eq!(bytecode.constants.len(), 2);
        assert_eq!(bytecode.var_names.len(), 1);
        assert_eq!(bytecode.var_names[0], "x");
    }
}
```

## Acceptance Criteria

1. ✅ `src/bytecode.rs` exists with all instruction types matching architecture
2. ✅ `Instruction` enum has 8 variants: LoadConst, LoadVar, StoreVar, BinaryOp, UnaryOp, Print, SetResult, Halt
3. ✅ `Bytecode` struct contains instructions, constants, and var_names vectors
4. ✅ `BytecodeBuilder` provides emit methods for all instruction types
5. ✅ `build()` automatically appends Halt instruction
6. ✅ Variable names are deduplicated in var_names pool
7. ✅ Constant pool stores all integer literals
8. ✅ All instructions are Debug + Clone + Copy + PartialEq + Eq
9. ✅ Unit tests pass: `cargo test --lib bytecode::tests`
10. ✅ Code compiles: `cargo check`

## Testing Instructions

```bash
# Run bytecode module tests
cargo test --lib bytecode::tests

# Run builder tests
cargo test --lib bytecode::tests::test_bytecode_builder

# Run deduplication test
cargo test --lib bytecode::tests::test_variable_name_deduplication

# Check compilation
cargo check
```

## Dependencies

- `src/ast.rs` (BinaryOperator, UnaryOperator)

## Provides

- `Instruction` enum (8 variants for VM execution)
- `Bytecode` struct (instructions + constant pool + variable names)
- `BytecodeBuilder` with emit methods for all instruction types

## Interface Contract with Compiler

Compiler creates a BytecodeBuilder and calls:
- `emit_load_const(dest_reg, value)` for integer literals
- `emit_load_var(dest_reg, name)` for variable reads
- `emit_store_var(name, src_reg)` for assignments
- `emit_binary_op(dest, op, left, right)` for binary operations
- `emit_print(src_reg)` for print statements
- `emit_set_result(src_reg)` for expression statements
- `build()` to finalize and get Bytecode

## Interface Contract with VM

VM receives Bytecode and:
- Iterates through `instructions` vector
- Looks up constants via `constants[value_index]`
- Looks up variable names via `var_names[var_index]`
- Executes until Halt instruction

## Performance Notes

- Register-based: 30-40% fewer instructions than stack VM
- Instruction size: 8-16 bytes depending on variant (acceptable for Phase 1)
- Constant pool: Avoids embedding large integers in instruction stream
- Variable name deduplication: Reduces memory for repeated variable access

## Notes

- Phase 1: No instruction deduplication or constant folding (simplicity first)
- Phase 2: Can add optimization passes (constant folding, dead code elimination)
- SetResult instruction is critical for output format specification compliance
- Halt instruction always appears last (added by build())
