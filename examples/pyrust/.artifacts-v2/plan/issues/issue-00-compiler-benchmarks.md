# issue-00-compiler-benchmarks: Create granular compiler-only benchmarks

## Description
Implement standalone compiler benchmarks measuring compilation time for pre-parsed AST (simple/complex/variable expressions). Isolates compiler performance from lexer and parser to enable per-stage optimization tracking. Part of AC3 per-stage benchmark infrastructure.

## Architecture Reference
Read architecture.md Section 4.1.4 (Implementation: Compiler Benchmarks) for:
- Benchmark structure using Criterion with black_box
- Pre-parsing strategy to isolate compiler from lexer/parser
- Configuration: significance_level(0.05), sample_size(1000), measurement_time(10s)
- Three test cases: compiler_simple ("2 + 3"), compiler_complex ("(10 + 20) * 3 / 2"), compiler_variables ("x = 10\ny = 20\nx + y")

## Interface Contracts
- Implements: `fn compiler_simple(c: &mut Criterion)`, `fn compiler_complex(c: &mut Criterion)`, `fn compiler_variables(c: &mut Criterion)`
- Exports: Criterion JSON output at target/criterion/compiler_simple/base/estimates.json (and _complex, _variables)
- Consumes: `use pyrust::{lexer::lex, parser::parse, compiler::compile}`
- Consumed by: issue-13-performance-validation (for AC3 validation)

## Files
- **Create**: `benches/compiler_benchmarks.rs`
- **Modify**: `Cargo.toml` (add [[bench]] entry with name = "compiler_benchmarks", harness = false)

## Dependencies
None (standalone benchmark infrastructure)

## Provides
- Compiler-only performance baseline measurements
- Criterion JSON output at target/criterion/compiler_simple/base/estimates.json

## Acceptance Criteria
- [ ] benches/compiler_benchmarks.rs exists with compiler_simple, compiler_complex, compiler_variables benchmarks
- [ ] Pre-parse input outside benchmark loop using lex() and parse() to isolate compiler performance
- [ ] Criterion generates estimates.json for each benchmark (compiler_simple, compiler_complex, compiler_variables)
- [ ] CV < 5% for all benchmarks

## Testing Strategy

### Test Files
- `benches/compiler_benchmarks.rs`: Compiler-only benchmarks (simple, complex, variables)

### Test Categories
- **Functional tests**: Run cargo bench --bench compiler_benchmarks and verify all 3 benchmarks execute successfully
- **Output verification**: Check that target/criterion/compiler_simple/base/estimates.json, compiler_complex/base/estimates.json, and compiler_variables/base/estimates.json exist
- **Variance check**: Verify CV < 5% in Criterion output for each benchmark

### Run Command
`cargo bench --bench compiler_benchmarks && test -f target/criterion/compiler_simple/base/estimates.json && test -f target/criterion/compiler_complex/base/estimates.json && test -f target/criterion/compiler_variables/base/estimates.json`
