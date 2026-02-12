# issue-00-variable-name-interning: Implement variable name interning with u32 integer IDs

## Description
Replace `HashMap<String, Value>` variable storage with `HashMap<u32, Value>` using interned variable name IDs. This eliminates String allocations during variable lookups and speeds variable access by ~50%, contributing to the AC2 allocation budget (≤5 allocations) and AC1 VM performance target (<150ns).

## Architecture Reference
Read architecture.md Section 3.3 (Variable Name Interning System) for:
- VariableInterner struct with name_to_id, id_to_name, next_id fields (3.3.1)
- Pre-interning strategy for a-z and common names (result, value, temp, count, index, data)
- Variable scoping behavior with HashMap<u32, Value> (3.3.2)
- Compiler integration with intern() calls during compile_expression (3.3.3)
- Bytecode format changes adding var_ids: Vec<u32> field

## Interface Contracts
- Implements:
  ```rust
  struct VariableInterner { name_to_id: HashMap<String, u32>, id_to_name: Vec<String>, next_id: u32 }
  impl VariableInterner { fn new() -> Self; fn intern(&mut self, name: &str) -> u32; }
  struct Bytecode { var_ids: Vec<u32>, ... }
  enum Instruction { LoadVar { dest_reg: u8, var_id: u32 }, StoreVar { var_id: u32, src_reg: u8 } }
  ```
- Exports: VariableInterner for compiler use, u32 variable IDs in bytecode
- Consumes: vm-register-bitmap (provides HashMap<u32, Value> variable storage)
- Consumed by: compiler-benchmarks (uses intern() calls), integration-verification (tests variable scoping)

## Files
- **Modify**: `src/compiler.rs` (add VariableInterner struct, integrate in Compiler, call intern() in compile_expression/compile_statement)
- **Modify**: `src/bytecode.rs` (add var_ids: Vec<u32> field, change LoadVar/StoreVar to use u32 var_id)
- **Modify**: `src/vm.rs` (change variables and CallFrame.local_vars to HashMap<u32, Value>, update LoadVar/StoreVar handlers)

## Dependencies
- issue-09-vm-register-bitmap (provides bitmap-based register validity and HashMap<u32, Value> variable storage)

## Provides
- Variable name interning eliminating String allocations at runtime
- 50% faster variable access (architecture section 3.3.2)
- HashMap<u32, Value> variable storage with scoping semantics (local scope shadows global)

## Acceptance Criteria
- [ ] VariableInterner struct in compiler.rs with name_to_id, id_to_name, next_id fields
- [ ] VariableInterner::new() pre-interns a-z and common names (result, value, temp, count, index, data)
- [ ] Compiler integrates VariableInterner, calls intern() during compile_expression and compile_statement
- [ ] Bytecode struct has var_ids: Vec<u32> field parallel to var_names
- [ ] Instruction::LoadVar and StoreVar use u32 var_id instead of String var_name_index
- [ ] VM.variables and CallFrame.local_vars use HashMap<u32, Value> instead of HashMap<String, Value>
- [ ] Variable lookup checks local scope then global scope using u32 IDs (architecture section 3.3.2)
- [ ] All existing compiler and VM tests pass (850+ tests total)

## Testing Strategy

### Test Files
- `tests/compiler_tests.rs`: Variable compilation with interning
- `tests/vm_tests.rs`: Variable scoping tests (local shadows global)
- `tests/integration_tests.rs`: End-to-end variable name deduplication

### Test Categories
- **Unit tests**: VariableInterner::new(), intern(), get_id(), get_name()
- **Functional tests**: test_local_scope_isolation, test_local_variable_shadows_global, test_function_with_params
- **Edge cases**: Variable name deduplication (test_variable_name_deduplication), undefined variable error messages

### Run Command
`cargo test compiler && cargo test vm`
