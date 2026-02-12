# issue-15-lexer-benchmarks: Lexer Performance Benchmarks with Variance Documentation

## Description
Implement standalone lexer benchmarks measuring tokenization time for simple, complex, and variable expressions. Uses Criterion with 1000 samples and black_box to prevent compiler optimization. Part of AC3 per-stage benchmark infrastructure. CV values are documented for tracking but no hard threshold is enforced due to inherent variance in nanosecond-scale measurements.

## Architecture Reference
Read `.artifacts-v2/plan/architecture.md` Section 4.1.2 (Implementation: Lexer Benchmarks) for:
- Benchmark function signatures: `lexer_simple`, `lexer_complex`, `lexer_variables`
- Criterion configuration parameters (sample_size=1000, measurement_time=10s, significance_level=0.05)
- `black_box()` usage patterns to prevent optimization
- Expected lexer baseline: ~5-10ns (~2-3% of total execution time)

## Interface Contracts

**Implements**:
```rust
fn lexer_simple(c: &mut Criterion)    // lex("2 + 3")
fn lexer_complex(c: &mut Criterion)   // lex("(10 + 20) * 3 / 2")
fn lexer_variables(c: &mut Criterion) // lex("x = 10\ny = 20\nx + y")
```

**Exports**: Criterion JSON at `target/criterion/{lexer_simple,lexer_complex,lexer_variables}/base/estimates.json`

**Consumes**: `pyrust::lexer::lex(input: &str) -> Result<Vec<Token>, LexError>`

**Consumed by**: AC3 validation (issue-00-performance-validation), CPython comparison baseline

## Files
- **Create**: `benches/lexer_benchmarks.rs`
- **Modify**: `Cargo.toml` (add `[[bench]]` section if not present)

## Dependencies
None (uses existing `pyrust::lexer` module)

## Provides
- Lexer-only performance baseline measurements
- Criterion JSON output at `target/criterion/lexer_simple/base/estimates.json`

## Acceptance Criteria
- [ ] `benches/lexer_benchmarks.rs` exists with lexer_simple, lexer_complex, lexer_variables benchmarks
- [ ] Each benchmark uses `black_box()` around input and output
- [ ] Criterion config specifies sample_size >= 1000
- [ ] `cargo bench --bench lexer_benchmarks` executes successfully
- [ ] JSON output files exist: `target/criterion/lexer_simple/base/estimates.json`, lexer_complex, lexer_variables
- [ ] CV values are documented in benchmark output (no hard threshold - nanosecond measurements have inherent variance)

## Testing Strategy

### Test Files
- `benches/lexer_benchmarks.rs`: Lexer tokenization benchmarks

### Test Categories
- **Unit benchmarks**: lexer_simple (2+3), lexer_complex (complex expression), lexer_variables (multi-line with variables)
- **Functional tests**: Verify each benchmark produces valid Criterion output with estimates.json
- **Variance documentation**: Record CV values for tracking but do not enforce <5% threshold

### Run Command
```bash
cargo bench --bench lexer_benchmarks && \
test -f target/criterion/lexer_simple/base/estimates.json && \
test -f target/criterion/lexer_complex/base/estimates.json && \
test -f target/criterion/lexer_variables/base/estimates.json
```
