# issue-02-startup-execution-benchmarks: Implement Startup and Execution Benchmarks

## Description
Implement comprehensive Criterion benchmarks for cold start (full pipeline) and warm execution (repeated calls) performance. Validate AC1.2 (< 100μs cold start) and AC1.5 (< 10% variance) with measurable evidence.

## Architecture Reference
Read `architecture.md` Section "Testing Strategy → Performance Tests (AC5-AC6)" for:
- Criterion configuration (significance level, sample size, measurement time)
- Benchmark function patterns using `black_box()` for optimizer prevention
- Performance budget breakdown table (target: ~40μs with 60μs margin)
- JSON output parsing methodology for validation

## Interface Contracts
- Benchmarks: `cold_start_simple`, `cold_start_complex`, `warm_execution`, `with_variables`, `with_print`
- Criterion output: `target/criterion/*/base/estimates.json` with fields: `mean.point_estimate`, `std_dev`
- Validation: `CV = std_dev / mean < 0.10`, `mean < 100000` ns

## Files
- **Create**: `benches/startup_benchmarks.rs` (cold start benchmarks)
- **Create**: `benches/execution_benchmarks.rs` (warm execution benchmarks)

## Dependencies
- issue-01-benchmark-infrastructure-setup (provides: Working Criterion setup)

## Provides
- AC1.2 validation: Cold start < 100μs
- AC1.5 validation: Variance < 10% CV
- Detailed performance breakdown by operation type

## Acceptance Criteria
- [ ] `cargo bench --bench startup_benchmarks` exits with code 0
- [ ] Mean of `cold_start_simple` < 100μs (parse JSON: `mean.point_estimate < 100000`)
- [ ] CV < 10% for all benchmarks (parse JSON: `std_dev / mean < 0.10`)
- [ ] Benchmarks cover: simple arithmetic (2+3), complex expressions, variables, print statements
- [ ] Criterion generates HTML reports in `target/criterion/`

## Testing Strategy

### Test Files
- `benches/startup_benchmarks.rs`: Cold start benchmarks (full pipeline from source string)
- `benches/execution_benchmarks.rs`: Warm execution benchmarks (pre-compiled bytecode)

### Test Categories
- **Cold start benchmarks**: `cold_start_simple` ("2 + 3"), `cold_start_complex` ("(10 + 20) * 3 / 2")
- **Warm execution benchmarks**: `warm_execution` (repeated VM execution of pre-compiled bytecode)
- **Feature benchmarks**: `with_variables` ("x = 10; y = 20; x + y"), `with_print` ("print(42)")
- **Validation**: Parse `target/criterion/*/base/estimates.json` to verify mean < 100000 ns and CV < 0.10

### Run Command
`cargo bench --bench startup_benchmarks && cargo bench --bench execution_benchmarks`
