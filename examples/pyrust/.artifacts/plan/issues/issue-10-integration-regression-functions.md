# issue-10-integration-regression-functions: End-to-end function tests and regression gate

## Description
Create comprehensive integration tests for the complete function pipeline (lex → parse → compile → execute) using the execute_python() API. Validate that all 199 existing tests still pass after function implementation. Add performance benchmarks measuring function call overhead. This is the validation gate ensuring we haven't broken existing functionality while adding functions.

## Architecture Reference
Read architecture.md Phase 2 Function Support implementation for:
- Complete pipeline integration: lexer → parser → compiler → VM
- execute_python() API contract and return value semantics
- Call stack structure and local scope management
- Function call execution flow through VM

## Interface Contracts
- Consumes: All Phase 2 implementations (parser, compiler, VM extensions)
- Implements:
  - `tests/test_functions.rs`: Integration tests using execute_python()
  - `benches/function_call_overhead.rs`: Criterion benchmark suite
- Exports: Test validation confirming all features work end-to-end

## Files
- **Create**: `tests/test_functions.rs` (integration tests for function features)
- **Create**: `benches/function_call_overhead.rs` (Criterion benchmark comparing function vs direct arithmetic)
- **Modify**: `src/lib.rs` (ensure tests are discoverable by cargo test)

## Dependencies
- issue-07-parser-extensions-functions (provides: function syntax parsing)
- issue-08-compiler-extensions-functions (provides: bytecode generation for functions)
- issue-09-vm-extensions-functions (provides: call stack and execution)

## Provides
- End-to-end validation: Full function pipeline works via execute_python()
- Regression gate: All 199 existing tests pass (AC2.6)
- Performance validation: Function call overhead < 5μs (AC2.8)
- Test coverage: 20+ function integration tests (AC2.7)

## Acceptance Criteria
- [ ] AC2.1: execute_python("def name(): return 42") returns Ok("")
- [ ] AC2.2: execute_python("def foo(): return 42\nfoo()") returns Ok("42")
- [ ] AC2.3: execute_python("def add(a, b): return a + b\nadd(10, 20)") returns Ok("30")
- [ ] AC2.4: Local scope isolation verified (function variables don't leak)
- [ ] AC2.5: execute_python("def foo(): return\nfoo()") returns Ok("")
- [ ] AC2.6: cargo test --lib shows 199 passed (CRITICAL regression gate)
- [ ] AC2.7: At least 20 new function tests pass
- [ ] AC2.8: Criterion benchmark: add(10, 20) - (10 + 20) < 5μs overhead

## Testing Strategy

### Test Files
- `tests/test_functions.rs`: All integration tests using execute_python() API
- `benches/function_call_overhead.rs`: Criterion benchmark comparing function call vs direct arithmetic

### Test Categories
- **Basic functions** (AC2.1, AC2.2): Zero-parameter function definition and call, function with return value
- **Functions with parameters** (AC2.3): Single param, multiple params, parameter binding correctness
- **Scope isolation** (AC2.4): Local variables don't affect global scope, global variables accessible in functions
- **Return statements** (AC2.5): Return without value, return with value, implicit return
- **Complex scenarios**: Nested function calls, functions calling functions, arithmetic in functions
- **Error scenarios**: Undefined function, wrong argument count, runtime errors in function body
- **Regression validation** (AC2.6): Run cargo test --lib, verify all existing tests pass
- **Performance** (AC2.8): Criterion benchmark function_call_overhead measuring overhead < 5μs

### Run Commands
- Integration tests: `cargo test --test test_functions`
- Regression tests: `cargo test --lib` (must show 199 passed)
- Performance benchmark: `cargo bench --bench function_call_overhead`
