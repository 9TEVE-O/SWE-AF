# issue-16-parser-benchmarks: Parser-Only Performance Benchmarks

## Description
Implement standalone parser benchmarks measuring parsing time for pre-tokenized input (simple/complex/variable expressions). Isolates parser performance from lexer by tokenizing outside the benchmark loop. Part of AC3 per-stage benchmark infrastructure.

## Architecture Reference
Read architecture.md Section 4.1.3 (Implementation: Parser Benchmarks) for:
- Benchmark architecture with pre-tokenization pattern
- Three test cases: parser_simple, parser_complex, parser_variables
- Criterion configuration for low measurement overhead (<1%)
- Pre-tokenization strategy to isolate parser from lexer

## Interface Contracts
- Implements: Three benchmark functions using Criterion framework
  ```rust
  fn parser_simple(c: &mut Criterion)
  fn parser_complex(c: &mut Criterion)
  fn parser_variables(c: &mut Criterion)
  ```
- Exports: Criterion JSON output at `target/criterion/{parser_simple,parser_complex,parser_variables}/base/estimates.json`
- Consumes: Tokenized input from `pyrust::lexer::lex()`, `pyrust::parser::parse()`
- Consumed by: AC3 validation command for per-stage benchmark infrastructure

## Files
- **Create**: `benches/parser_benchmarks.rs`
- **Modify**: `Cargo.toml` (add bench target if not present)

## Dependencies
- None (standalone benchmark, no cross-issue dependencies)

## Provides
- Parser-only performance baseline measurements
- Criterion JSON output for AC3 validation
- Isolated parser timing (excludes lexer overhead)

## Acceptance Criteria
- [ ] cargo bench --bench parser_benchmarks executes all 3 benchmarks successfully
- [ ] Pre-tokenization occurs outside benchmark loop (isolates parser performance)
- [ ] Criterion generates estimates.json for each benchmark (parser_simple, parser_complex, parser_variables)
- [ ] CV values are documented in benchmark output (no hard threshold - batched nanosecond measurements have inherent variance)

## Testing Strategy

### Test Files
- `benches/parser_benchmarks.rs`: All three parser benchmark functions

### Test Categories
- **Functional validation**: Run cargo bench --bench parser_benchmarks and verify exit code 0
- **Output validation**: Verify JSON files exist at target/criterion/parser_{simple,complex,variables}/base/estimates.json
- **Variance documentation**: Record CV values for tracking but do not enforce <5% threshold

### Run Command
```bash
cargo bench --bench parser_benchmarks && \
test -f target/criterion/parser_simple/base/estimates.json && \
test -f target/criterion/parser_complex/base/estimates.json && \
test -f target/criterion/parser_variables/base/estimates.json
```
