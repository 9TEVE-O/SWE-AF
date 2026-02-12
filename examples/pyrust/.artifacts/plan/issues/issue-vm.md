# Issue: Virtual Machine Implementation

## Summary
Implement register-based bytecode execution engine. Maintains register file, variable environment, and stdout capture. Returns Option<Value> to support output format specification.

## Context
The VM is the final execution stage. It must achieve ~5μs performance for typical 20-instruction programs. The execute() signature returns Option<Value> (BLOCKER 2 resolution) to distinguish "no result" from "result is 0".

## Architecture Reference
See architecture.md lines 989-1135 for complete VM specification.

## Implementation Requirements

### 1. Create `src/vm.rs` with Exact Implementation

```rust
use crate::bytecode::*;
use crate::value::Value;
use crate::error::RuntimeError;
use std::collections::HashMap;

/// Virtual machine state
pub struct VM {
    registers: Vec<Value>,                // Register file (preallocated)
    variables: HashMap<String, Value>,    // Global variable environment
    stdout: String,                       // Captured print output
    result: Option<Value>,                // Final expression result (None unless SetResult executed)
}

impl VM {
    /// Create new VM with empty state
    pub fn new() -> Self {
        VM {
            registers: vec![Value::Integer(0); 256], // Preallocate 256 registers
            variables: HashMap::new(),
            stdout: String::new(),
            result: None,
        }
    }

    /// Execute bytecode and return final result
    ///
    /// # Returns
    /// - `Ok(Some(value))` if an expression statement was executed (SetResult was called)
    /// - `Ok(None)` if no expression statements were executed (only assignments/prints)
    /// - `Err(RuntimeError)` if execution failed
    ///
    /// # Performance
    /// Target: ~5μs for 20-instruction program
    pub fn execute(&mut self, bytecode: &Bytecode) -> Result<Option<Value>, RuntimeError> {
        let mut pc = 0; // Program counter (index into instructions Vec)

        loop {
            if pc >= bytecode.instructions.len() {
                break;
            }

            let instruction = bytecode.instructions[pc];

            match instruction {
                Instruction::LoadConst { dest, value_index } => {
                    self.registers[dest as usize] = Value::Integer(
                        bytecode.constants[value_index as usize]
                    );
                }

                Instruction::LoadVar { dest, var_index } => {
                    let var_name = &bytecode.var_names[var_index as usize];
                    let value = self.variables.get(var_name)
                        .cloned()
                        .ok_or_else(|| RuntimeError {
                            message: format!("Undefined variable: {}", var_name),
                            instruction_index: pc,
                        })?;
                    self.registers[dest as usize] = value;
                }

                Instruction::StoreVar { var_index, src } => {
                    let var_name = bytecode.var_names[var_index as usize].clone();
                    let value = self.registers[src as usize].clone();
                    self.variables.insert(var_name, value);
                }

                Instruction::BinaryOp { dest, op, left, right } => {
                    let left_val = &self.registers[left as usize];
                    let right_val = &self.registers[right as usize];
                    let result = left_val.binary_op(op, right_val)
                        .map_err(|mut e| {
                            e.instruction_index = pc; // Set correct instruction index
                            e
                        })?;
                    self.registers[dest as usize] = result;
                }

                Instruction::UnaryOp { dest, op, operand } => {
                    let operand_val = &self.registers[operand as usize];
                    let result = operand_val.unary_op(op)
                        .map_err(|mut e| {
                            e.instruction_index = pc;
                            e
                        })?;
                    self.registers[dest as usize] = result;
                }

                Instruction::Print { src } => {
                    let value = &self.registers[src as usize];
                    self.stdout.push_str(&format!("{}\n", value));
                }

                Instruction::SetResult { src } => {
                    // Expression statement: set the final result value
                    self.result = Some(self.registers[src as usize].clone());
                }

                Instruction::Halt => break,
            }

            pc += 1;
        }

        // Return final result (None if no expression statements executed)
        Ok(self.result.clone())
    }

    /// Format output according to specification:
    /// - stdout content (from print statements, each with \n)
    /// - final expression value (if any, WITHOUT trailing \n)
    ///
    /// # Arguments
    /// * `result` - The value returned by execute() (None if no expression statements)
    ///
    /// # Returns
    /// Formatted string following the Output Format Specification
    pub fn format_output(&self, result: Option<Value>) -> String {
        let mut output = self.stdout.clone();
        if let Some(val) = result {
            output.push_str(&format!("{}", val));
        }
        output
    }
}
```

### 2. Unit Tests

Add tests at the bottom of `src/vm.rs`:

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::BinaryOperator;
    use crate::bytecode::BytecodeBuilder;

    fn build_simple_bytecode() -> Bytecode {
        // Build bytecode for: 2 + 3
        let mut builder = BytecodeBuilder::new();
        builder.emit_load_const(0, 2);
        builder.emit_load_const(1, 3);
        builder.emit_binary_op(2, BinaryOperator::Add, 0, 1);
        builder.emit_set_result(2);
        builder.build()
    }

    #[test]
    fn test_vm_new() {
        let vm = VM::new();
        assert_eq!(vm.registers.len(), 256);
        assert_eq!(vm.variables.len(), 0);
        assert_eq!(vm.stdout, "");
        assert_eq!(vm.result, None);
    }

    #[test]
    fn test_execute_simple_addition() {
        let bytecode = build_simple_bytecode();
        let mut vm = VM::new();

        let result = vm.execute(&bytecode).unwrap();

        assert_eq!(result, Some(Value::Integer(5)));
    }

    #[test]
    fn test_load_const() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_load_const(0, 42);
        builder.emit_set_result(0);
        let bytecode = builder.build();

        let mut vm = VM::new();
        let result = vm.execute(&bytecode).unwrap();

        assert_eq!(result, Some(Value::Integer(42)));
    }

    #[test]
    fn test_store_and_load_var() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_load_const(0, 10);
        builder.emit_store_var("x", 0);
        builder.emit_load_var(1, "x");
        builder.emit_set_result(1);
        let bytecode = builder.build();

        let mut vm = VM::new();
        let result = vm.execute(&bytecode).unwrap();

        assert_eq!(result, Some(Value::Integer(10)));
        assert_eq!(vm.variables.get("x"), Some(&Value::Integer(10)));
    }

    #[test]
    fn test_undefined_variable_error() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_load_var(0, "undefined");
        let bytecode = builder.build();

        let mut vm = VM::new();
        let result = vm.execute(&bytecode);

        assert!(result.is_err());
        let err = result.unwrap_err();
        assert!(err.message.contains("Undefined variable: undefined"));
    }

    #[test]
    fn test_binary_operations() {
        let test_cases = vec![
            (BinaryOperator::Add, 2, 3, 5),
            (BinaryOperator::Subtract, 10, 3, 7),
            (BinaryOperator::Multiply, 3, 4, 12),
            (BinaryOperator::Divide, 20, 4, 5),
            (BinaryOperator::FloorDiv, 17, 5, 3),
            (BinaryOperator::Modulo, 17, 5, 2),
        ];

        for (op, left, right, expected) in test_cases {
            let mut builder = BytecodeBuilder::new();
            builder.emit_load_const(0, left);
            builder.emit_load_const(1, right);
            builder.emit_binary_op(2, op, 0, 1);
            builder.emit_set_result(2);
            let bytecode = builder.build();

            let mut vm = VM::new();
            let result = vm.execute(&bytecode).unwrap();

            assert_eq!(result, Some(Value::Integer(expected)),
                "Failed for {:?} {} {}", op, left, right);
        }
    }

    #[test]
    fn test_division_by_zero_error() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_load_const(0, 10);
        builder.emit_load_const(1, 0);
        builder.emit_binary_op(2, BinaryOperator::Divide, 0, 1);
        let bytecode = builder.build();

        let mut vm = VM::new();
        let result = vm.execute(&bytecode);

        assert!(result.is_err());
        let err = result.unwrap_err();
        assert!(err.message.contains("Division by zero"));
    }

    #[test]
    fn test_print_instruction() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_load_const(0, 42);
        builder.emit_print(0);
        let bytecode = builder.build();

        let mut vm = VM::new();
        vm.execute(&bytecode).unwrap();

        assert_eq!(vm.stdout, "42\n");
    }

    #[test]
    fn test_multiple_print_statements() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_load_const(0, 10);
        builder.emit_print(0);
        builder.emit_load_const(1, 20);
        builder.emit_print(1);
        let bytecode = builder.build();

        let mut vm = VM::new();
        vm.execute(&bytecode).unwrap();

        assert_eq!(vm.stdout, "10\n20\n");
    }

    #[test]
    fn test_setresult_instruction() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_load_const(0, 42);
        builder.emit_set_result(0);
        let bytecode = builder.build();

        let mut vm = VM::new();
        let result = vm.execute(&bytecode).unwrap();

        assert_eq!(vm.result, Some(Value::Integer(42)));
        assert_eq!(result, Some(Value::Integer(42)));
    }

    #[test]
    fn test_no_setresult_returns_none() {
        // Bytecode with no SetResult instruction
        let mut builder = BytecodeBuilder::new();
        builder.emit_load_const(0, 42);
        builder.emit_store_var("x", 0);
        let bytecode = builder.build();

        let mut vm = VM::new();
        let result = vm.execute(&bytecode).unwrap();

        assert_eq!(result, None, "Should return None when no SetResult");
    }

    #[test]
    fn test_multiple_setresult_last_wins() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_load_const(0, 10);
        builder.emit_set_result(0);
        builder.emit_load_const(1, 20);
        builder.emit_set_result(1);
        builder.emit_load_const(2, 30);
        builder.emit_set_result(2);
        let bytecode = builder.build();

        let mut vm = VM::new();
        let result = vm.execute(&bytecode).unwrap();

        assert_eq!(result, Some(Value::Integer(30)), "Last SetResult should win");
    }

    #[test]
    fn test_format_output_with_result() {
        let vm = VM {
            registers: vec![Value::Integer(0); 256],
            variables: HashMap::new(),
            stdout: String::new(),
            result: Some(Value::Integer(42)),
        };

        let output = vm.format_output(Some(Value::Integer(42)));
        assert_eq!(output, "42");
    }

    #[test]
    fn test_format_output_with_stdout_and_result() {
        let vm = VM {
            registers: vec![Value::Integer(0); 256],
            variables: HashMap::new(),
            stdout: "10\n".to_string(),
            result: Some(Value::Integer(20)),
        };

        let output = vm.format_output(Some(Value::Integer(20)));
        assert_eq!(output, "10\n20");
    }

    #[test]
    fn test_format_output_no_result() {
        let vm = VM {
            registers: vec![Value::Integer(0); 256],
            variables: HashMap::new(),
            stdout: "10\n".to_string(),
            result: None,
        };

        let output = vm.format_output(None);
        assert_eq!(output, "10\n");
    }

    #[test]
    fn test_format_output_empty() {
        let vm = VM {
            registers: vec![Value::Integer(0); 256],
            variables: HashMap::new(),
            stdout: String::new(),
            result: None,
        };

        let output = vm.format_output(None);
        assert_eq!(output, "");
    }

    #[test]
    fn test_runtime_error_instruction_index() {
        let mut builder = BytecodeBuilder::new();
        builder.emit_load_const(0, 10);
        builder.emit_load_const(1, 0);
        builder.emit_binary_op(2, BinaryOperator::Divide, 0, 1); // This is instruction 2
        let bytecode = builder.build();

        let mut vm = VM::new();
        let result = vm.execute(&bytecode);

        assert!(result.is_err());
        let err = result.unwrap_err();
        assert_eq!(err.instruction_index, 2, "Should report correct instruction index");
    }

    #[test]
    fn test_complex_program() {
        // Program: x = 10; y = 20; print(x + y); x * y
        let mut builder = BytecodeBuilder::new();

        // x = 10
        builder.emit_load_const(0, 10);
        builder.emit_store_var("x", 0);

        // y = 20
        builder.emit_load_const(1, 20);
        builder.emit_store_var("y", 1);

        // print(x + y)
        builder.emit_load_var(2, "x");
        builder.emit_load_var(3, "y");
        builder.emit_binary_op(4, BinaryOperator::Add, 2, 3);
        builder.emit_print(4);

        // x * y
        builder.emit_load_var(5, "x");
        builder.emit_load_var(6, "y");
        builder.emit_binary_op(7, BinaryOperator::Multiply, 5, 6);
        builder.emit_set_result(7);

        let bytecode = builder.build();

        let mut vm = VM::new();
        let result = vm.execute(&bytecode).unwrap();

        assert_eq!(vm.stdout, "30\n");
        assert_eq!(result, Some(Value::Integer(200)));
        assert_eq!(vm.variables.get("x"), Some(&Value::Integer(10)));
        assert_eq!(vm.variables.get("y"), Some(&Value::Integer(20)));
    }

    #[test]
    fn test_register_file_size() {
        let vm = VM::new();
        assert_eq!(vm.registers.len(), 256, "Should have 256 preallocated registers");
    }
}
```

## Acceptance Criteria

1. ✅ `src/vm.rs` exists with VM struct matching architecture
2. ✅ `execute()` returns `Result<Option<Value>, RuntimeError>` (BLOCKER 2 compliance)
3. ✅ All 8 instruction types handled correctly
4. ✅ SetResult instruction sets self.result to Some(value)
5. ✅ Print instruction appends "{value}\n" to stdout
6. ✅ Division by zero returns RuntimeError with instruction_index
7. ✅ Undefined variable returns RuntimeError with variable name
8. ✅ format_output() implements output format specification exactly
9. ✅ Unit tests pass: `cargo test --lib vm::tests`
10. ✅ Code compiles: `cargo check`

## Testing Instructions

```bash
# Run VM module tests
cargo test --lib vm::tests

# Run SetResult tests (critical)
cargo test --lib vm::tests::test_setresult

# Run format_output tests
cargo test --lib vm::tests::test_format_output

# Run error handling tests
cargo test --lib vm::tests::test_error

# Check compilation
cargo check
```

## Dependencies

- `src/bytecode.rs` (Bytecode, Instruction)
- `src/value.rs` (Value)
- `src/error.rs` (RuntimeError)

## Provides

- `VM` struct with new() and execute() methods
- `format_output()` method for output formatting

## Interface Contract with Compiler

Receives Bytecode from compiler:
- Executes instructions sequentially from index 0
- Stops at Halt instruction
- Returns Option<Value> based on SetResult executions

## Interface Contract with API

API calls:
1. `VM::new()` to create VM instance
2. `vm.execute(&bytecode)?` to run bytecode
3. `vm.format_output(result)` to format final output

## Critical Implementation Notes

**Option<Value> Return Type** (BLOCKER 2 Resolution):

The return type `Result<Option<Value>, RuntimeError>` is CRITICAL:

- `Ok(None)` → no expression statements executed (only assignments/prints)
- `Ok(Some(value))` → at least one expression statement executed
- `Err(error)` → execution failed

**Why this matters:**
```rust
// Without Option<Value>, these cases are indistinguishable:
execute("x = 10")  // Should return None → format as ""
execute("0")       // Should return Some(0) → format as "0"

// With Option<Value>:
execute("x = 10")  // Returns Ok(None) → format_output(None) = ""
execute("0")       // Returns Ok(Some(0)) → format_output(Some(0)) = "0"
```

**SetResult Behavior:**
- VM starts with `self.result = None`
- Each SetResult instruction overwrites: `self.result = Some(register_value)`
- Multiple SetResult → last one wins
- No SetResult → returns None

**format_output Contract:**
```rust
// Output = {stdout}{result_if_some}
vm.stdout = "10\n"; result = Some(20) → "10\n20"
vm.stdout = "10\n"; result = None → "10\n"
vm.stdout = ""; result = Some(5) → "5"
vm.stdout = ""; result = None → ""
```

## Performance Notes

- Preallocated 256-register file: No reallocation during execution
- Linear instruction dispatch: ~1μs per instruction
- Computed goto via match: Rust optimizer handles this well
- Target: ~5μs for 20-instruction program

## Notes

- Phase 1: Single global scope (HashMap<String, Value>)
- Phase 2: Add scope stack for functions
- Register file size: 256 is sufficient (Phase 1 uses < 20 registers)
- Instruction index in errors: Useful for debugging, can map to source line in Phase 2
