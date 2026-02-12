# issue-05-ast-extensions-functions: Extend AST with function definition, return, and call nodes

## Description
Add function-related AST node types to support function definitions, return statements, and function call expressions. This extends the existing AST structure (Program, Statement, Expression) to represent function syntax without implementing any execution logic.

## Architecture Reference
Read architecture.md Section 4 (AST Module) and Section 11.2 (Extension Point 2: Adding Function Call Support) for:
- Existing AST enum extension patterns (Statement, Expression)
- Function AST node structure: FunctionDef with name, params, body
- Return statement structure: Return with optional value
- Call expression structure: Call with function name and arguments
- Design rationale for Box<Expression> and Vec usage

## Interface Contracts

Implements (signatures only - do NOT copy implementation code):
```rust
// Statement enum - add these variants:
Statement::FunctionDef { name: String, params: Vec<String>, body: Vec<Statement> }
Statement::Return { value: Option<Expression> }

// Expression enum - add this variant:
Expression::Call { name: String, args: Vec<Expression> }
```

Exports: Statement::FunctionDef, Statement::Return, Expression::Call variants for use by parser and compiler

Consumes: Existing AST infrastructure (Debug, Clone, PartialEq traits)

Consumed by: issue-06-parser-extensions-functions, issue-07-compiler-extensions-functions

## Files
- **Modify**: `src/ast.rs` (add new enum variants, extend existing tests)

## Dependencies
- None (pure data structure extension)

## Provides
- Statement::FunctionDef AST variant
- Statement::Return AST variant
- Expression::Call AST variant
- AST validation ensuring function nodes are well-formed

## Acceptance Criteria
- [ ] AC2.1 (partial): AST can represent function definition syntax
- [ ] Statement::FunctionDef variant exists with name, params, body fields
- [ ] Statement::Return variant exists with optional value field
- [ ] Expression::Call variant exists with name and args fields
- [ ] All existing AST tests continue to pass (199 test regression check)
- [ ] At least 10 new unit tests for function AST nodes pass

## Testing Strategy

### Test Files
- `src/ast.rs` (in #[cfg(test)] mod tests): Add function node tests to existing test module

### Test Categories
- **Construction tests**: Create FunctionDef, Return, Call nodes and verify fields
- **Equality tests**: Verify PartialEq works correctly for function nodes
- **Clone tests**: Verify Clone trait works correctly for all function nodes
- **Nesting tests**: Test function bodies with nested statements (loops, other functions)
- **Regression tests**: All existing AST tests (lines 98-327) must continue to pass

### Run Command
`cargo test --lib ast::tests`
