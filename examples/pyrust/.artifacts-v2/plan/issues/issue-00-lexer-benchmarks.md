# issue-00-lexer-benchmarks: Create granular lexer-only benchmarks

## Description
Implement standalone lexer benchmarks that measure tokenization time in isolation (excluding parser, compiler, VM). Uses Criterion with 1000 samples and black_box to prevent compiler optimization. Part of AC3 per-stage benchmark infrastructure for identifying performance bottlenecks.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts-v2/plan/architecture.md` Section 4.1.2 (Lexer Benchmarks) for:
- Benchmark function patterns (`lexer_simple`, `lexer_complex`, `lexer_variables`)
- Criterion configuration (sample_size=1000, measurement_time=10s, significance_level=0.05)
- Use of `black_box()` to prevent optimization
- Expected lexer performance baseline: ~5-10ns (~2-3% of total execution)

## Interface Contracts

**Implements**:
```rust
fn lexer_simple(c: &mut Criterion) // Benchmarks: lex("2 + 3")
fn lexer_complex(c: &mut Criterion) // Benchmarks: lex("(10 + 20) * 3 / 2")
fn lexer_variables(c: &mut Criterion) // Benchmarks: lex("x = 10\ny = 20\nx + y")
```

**Exports**: Criterion JSON output at `target/criterion/lexer_simple/base/estimates.json` (and lexer_complex, lexer_variables)

**Consumes**: `pyrust::lexer::lex` function (existing lexer interface)

**Consumed by**: AC3 validation script (checks JSON files exist), performance-validation issue

## Files
- **Create**: `benches/lexer_benchmarks.rs`
- **Modify**: `Cargo.toml` (add `[[bench]]` section for lexer_benchmarks)

## Dependencies
None (standalone benchmark, uses existing lexer module)

## Provides
- Lexer-only performance baseline measurements
- Criterion JSON output at `target/criterion/lexer_simple/base/estimates.json`

## Acceptance Criteria
- [ ] `benches/lexer_benchmarks.rs` exists with lexer_simple, lexer_complex, lexer_variables benchmarks
- [ ] Each benchmark uses `black_box()` around input and output
- [ ] Criterion config specifies sample_size ≥ 1000
- [ ] `cargo bench --bench lexer_benchmarks` executes successfully
- [ ] JSON output files exist: `target/criterion/lexer_simple/base/estimates.json`, `lexer_complex`, `lexer_variables`
- [ ] Coefficient of variation (CV) < 5% for all benchmarks

## Testing Strategy

### Test Files
- `benches/lexer_benchmarks.rs`: Benchmarks lexer tokenization in isolation

### Test Categories
- **Unit benchmarks**: lexer_simple (2+3), lexer_complex (complex expression), lexer_variables (multi-line with variables)
- **Functional tests**: Verify each benchmark produces valid Criterion output with estimates.json
- **Edge cases**: Empty input coverage if needed (optional)

### Run Command
```bash
cargo bench --bench lexer_benchmarks
test -f target/criterion/lexer_simple/base/estimates.json
test -f target/criterion/lexer_complex/base/estimates.json
test -f target/criterion/lexer_variables/base/estimates.json
```
