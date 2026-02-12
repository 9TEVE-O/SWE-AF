# issue-17-compiler-benchmarks: Compiler Performance Benchmarks

## Description
Implement standalone compiler benchmarks that measure compilation time for pre-parsed ASTs (simple/complex/variable expressions). This isolates compiler performance from lexer and parser, providing granular per-stage benchmark data as part of AC3 infrastructure.

## Architecture Reference
Read architecture.md Section 4.1.4 (Implementation: Compiler Benchmarks) for:
- Pre-parsing strategy (tokens → AST outside benchmark loop)
- Three test cases: simple (`2 + 3`), complex (`(10 + 20) * 3 / 2`), variables (`x = 10\ny = 20\nx + y`)
- Criterion configuration (significance_level 0.05, sample_size 1000, measurement_time 10s)
- Expected CV values (architecture predicts 42% CV for compiler_simple due to sub-500ns scale)

## Interface Contracts
- Implements: `benches/compiler_benchmarks.rs` with three benchmark functions:
  ```rust
  fn compiler_simple(c: &mut Criterion)  // Pre-parsed "2 + 3"
  fn compiler_complex(c: &mut Criterion) // Pre-parsed "(10 + 20) * 3 / 2"
  fn compiler_variables(c: &mut Criterion) // Pre-parsed "x = 10\ny = 20\nx + y"
  ```
- Exports: Criterion JSON at `target/criterion/compiler_*/base/estimates.json`
- Consumes: `lexer::lex()`, `parser::parse()`, `compiler::compile()` from PyRust crate
- Consumed by: AC3 validation script, performance tracking infrastructure

## Files
- **Verify exists**: `benches/compiler_benchmarks.rs` (may already exist)

## Dependencies
- None (standalone benchmark, does not depend on other issues)

## Provides
- Compiler-only performance baseline measurements
- Criterion JSON output at `target/criterion/compiler_simple/base/estimates.json`

## Acceptance Criteria
- [ ] `benches/compiler_benchmarks.rs` exists with 3 benchmark functions
- [ ] Pre-parsing happens outside benchmark loop using `lex()` and `parse()`
- [ ] Criterion generates `estimates.json` for each benchmark
- [ ] CV values documented in output (no hard <5% threshold enforcement)

## Testing Strategy

### Test Files
- `benches/compiler_benchmarks.rs`: Compiler benchmark suite with three test cases

### Test Categories
- **Functional tests**: Run `cargo bench --bench compiler_benchmarks` and verify all 3 benchmarks execute successfully
- **Output verification**: Check that `target/criterion/compiler_simple/base/estimates.json`, `target/criterion/compiler_complex/base/estimates.json`, and `target/criterion/compiler_variables/base/estimates.json` exist after benchmark run
- **Variance documentation**: Record CV values for tracking but do not enforce <5% threshold (architecture notes sub-500ns measurements may show higher variance)

### Run Command
```bash
cargo bench --bench compiler_benchmarks && \
test -f target/criterion/compiler_simple/base/estimates.json && \
test -f target/criterion/compiler_complex/base/estimates.json && \
test -f target/criterion/compiler_variables/base/estimates.json
```
