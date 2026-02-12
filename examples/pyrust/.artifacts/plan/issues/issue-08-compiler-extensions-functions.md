# issue-08-compiler-extensions-functions: Compile function definitions and calls to bytecode

## Description
Extend the compiler to transform function AST nodes into bytecode instructions. This includes compiling function definitions (storing function metadata), function calls (setting up arguments in registers), and return statements (with or without values). The compiler must track function definitions separately from main program code.

## Architecture Reference
Read architecture.md Section 6 (Compiler Module) for:
- `compile_statement()` pattern for handling Statement variants
- `compile_expression()` pattern for handling Expression variants
- Register allocation with `alloc_register()`
- Extension point: add match arms for new AST nodes

## Interface Contracts
- **Implements**:
  ```rust
  // In compile_statement():
  Statement::FunctionDef { name, params, body } => compile function body to bytecode
  Statement::Return { value } => emit Return instruction with optional value register

  // In compile_expression():
  Expression::Call { func_name, args } => emit Call instruction with arg registers
  ```
- **Exports**: Function metadata HashMap<String, bytecode_offset>
- **Consumes**: `Statement::FunctionDef`, `Statement::Return`, `Expression::Call` from issue-05
- **Consumed by**: issue-09 (VM executes compiled function bytecode)

## Files
- **Modify**: `src/compiler.rs` (add match arms in compile_statement/compile_expression)

## Dependencies
- issue-05 (provides: AST nodes for functions)
- issue-06 (provides: bytecode instructions DefineFunction, Call, Return)

## Provides
- Compilation of Statement::FunctionDef to bytecode
- Compilation of Expression::Call to bytecode with argument setup
- Compilation of Statement::Return to bytecode
- Function metadata tracking (name to bytecode offset)

## Acceptance Criteria
- [ ] FunctionDef statements compile to DefineFunction instructions
- [ ] Call expressions compile to Call instruction with argument registers
- [ ] Return statements compile to Return instruction (with/without value)
- [ ] Compiler tracks function definitions separately from main code
- [ ] Argument compilation allocates registers correctly
- [ ] All existing compiler tests pass (regression check)
- [ ] At least 10 new compiler tests for function compilation

## Testing Strategy

### Test Files
- `src/compiler.rs`: Add `#[cfg(test)] mod function_compilation_tests`

### Test Categories
- **Function definition**: Compile `def foo():` with 0, 1, N params
- **Function calls**: Compile `foo()` with 0, 1, N args
- **Return statements**: Compile `return`, `return expr`
- **Scope isolation**: Ensure function local variables compile separately
- **Nested calls**: Function calling another function
- **Regression**: All existing 28 compiler tests pass

### Run Command
`cargo test --lib compiler::function_compilation_tests`
