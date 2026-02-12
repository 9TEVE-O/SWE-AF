# issue-00-parser-benchmarks: Create granular parser-only benchmarks

## Description
Implement standalone parser benchmarks measuring parsing time for pre-tokenized input (simple/complex/variable expressions). Isolates parser performance from lexer to enable independent validation of parser optimizations. Part of AC3 per-stage benchmark infrastructure.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts-v2/plan/architecture.md` Section 4.1.3 (Parser Benchmarks) for:
- Pre-tokenization strategy (lex outside benchmark loop)
- Criterion configuration (sample_size: 1000, measurement_time: 10s)
- black_box usage pattern to prevent compiler optimizations
- Token cloning pattern for benchmark isolation

## Interface Contracts
Implements three benchmark functions matching architecture specification:
```rust
fn parser_simple(c: &mut Criterion);   // Benchmarks: parse(lex("2 + 3"))
fn parser_complex(c: &mut Criterion);  // Benchmarks: parse(lex("(10 + 20) * 3 / 2"))
fn parser_variables(c: &mut Criterion); // Benchmarks: parse(lex("x = 10\ny = 20\nx + y"))
```

Exports: Criterion JSON output at `target/criterion/parser_simple/base/estimates.json`

Consumes:
- `pyrust::lexer::lex` (tokenizes Python source)
- `pyrust::parser::parse` (parses token stream to AST)

Consumed by: **performance-validation** (AC3 validation)

## Files
- **Create**: `benches/parser_benchmarks.rs`
- **Modify**: `Cargo.toml` (add `[[bench]]` entry: `name = "parser_benchmarks"`, `harness = false`)

## Dependencies
None (baseline infrastructure)

## Provides
- Parser-only performance baseline measurements
- Criterion JSON output at `target/criterion/parser_simple/base/estimates.json`

## Acceptance Criteria
- [ ] `cargo bench --bench parser_benchmarks` executes all 3 benchmarks successfully
- [ ] Pre-tokenization occurs outside benchmark loop (isolates parser performance)
- [ ] Criterion generates `estimates.json` for each benchmark (parser_simple, parser_complex, parser_variables)
- [ ] CV < 5% for all benchmarks (stable measurements)

## Testing Strategy

### Test Files
- N/A (benchmark validation via Criterion output)

### Test Categories
- **Functional validation**: Run `cargo bench --bench parser_benchmarks` and verify exit code 0
- **Output validation**: Verify JSON files exist at `target/criterion/parser_{simple,complex,variables}/base/estimates.json`
- **Stability validation**: Check CV in estimates.json (std_dev/mean < 0.05)

### Run Command
```bash
cargo bench --bench parser_benchmarks && \
test -f target/criterion/parser_simple/base/estimates.json && \
test -f target/criterion/parser_complex/base/estimates.json && \
test -f target/criterion/parser_variables/base/estimates.json
```
