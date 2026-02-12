# issue-08-benchmark-stability: Fix benchmark coefficient of variation

## Description
Update all Criterion benchmarks to achieve CV < 10% by configuring sample_size(1000) and measurement_time(10s). Fixes 7 benchmark stability test failures and ensures statistical reliability of performance measurements.

## Architecture Reference
Read `architecture.md` Section 4.3 (Benchmark Stability) for:
- Exact Criterion configuration parameters (sample_size, measurement_time, warm_up_time, noise_threshold)
- criterion_group! macro replacement pattern
- std::time::Duration import requirement

## Interface Contracts
- Implements: Criterion configuration in all benchmark files
```rust
criterion_group! {
    name = benches;
    config = Criterion::default()
        .sample_size(1000)
        .measurement_time(Duration::from_secs(10))
        .warm_up_time(Duration::from_secs(3))
        .noise_threshold(0.05);
    targets = /* existing targets unchanged */
}
```
- Exports: Stable benchmarks with CV < 10%
- Consumes: Existing benchmark functions (unchanged)
- Consumed by: speedup-validation-scripts (validates CV via JSON)

## Files
- **Modify**: `benches/compiler_benchmarks.rs` (add Duration import, update criterion_group!)
- **Modify**: `benches/execution_benchmarks.rs` (add Duration import, update criterion_group!)
- **Modify**: `benches/function_call_overhead.rs` (add Duration import, update criterion_group!)
- **Modify**: `benches/lexer_benchmarks.rs` (add Duration import, update criterion_group!)
- **Modify**: `benches/parser_benchmarks.rs` (add Duration import, update criterion_group!)
- **Modify**: `benches/vm_benchmarks.rs` (add Duration import, update criterion_group!)
- **Modify**: `benches/startup_benchmarks.rs` (add Duration import, update criterion_group!)
- **Create**: `scripts/validate_benchmark_stability.sh` (CV validation script)

## Dependencies
None (independent bug fix)

## Provides
- Stable benchmarks with CV < 10%
- Fixed 7 benchmark stability test failures
- Validation script for automated CV checking

## Acceptance Criteria
- [ ] All 7 benchmark files have Duration import added
- [ ] All 7 criterion_group! macros updated with new config
- [ ] `cargo bench` completes successfully without errors
- [ ] AC4.4: All benchmarks have CV < 10% verified by parsing Criterion JSON
- [ ] M5: `scripts/validate_benchmark_stability.sh` exits 0
- [ ] AC4.2: All 664 currently passing tests still pass

## Testing Strategy

### Test Files
- `scripts/validate_benchmark_stability.sh`: Parses `target/criterion/**/estimates.json` and validates max(std_dev/mean) < 0.10

### Test Categories
- **Benchmark execution**: Run `cargo bench` to generate Criterion output and JSON estimates
- **CV validation**: Parse estimates.json files for all benchmarks, compute CV = std_dev/mean, verify < 10%
- **Regression check**: Run `cargo test --release` to ensure no test breakage

### Run Command
```bash
cargo bench 2>&1 | tee bench_output.txt
./scripts/validate_benchmark_stability.sh
cargo test --release
```
