# issue-01-benchmark-infrastructure-setup: Set up Criterion benchmark infrastructure and verify it runs

## Description
Create the benches/ directory structure and a minimal Criterion benchmark that compiles and runs with `cargo bench`. This validates that the benchmark infrastructure is configured correctly before implementing specific performance tests in subsequent issues.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section "Testing Strategy" (Performance Tests subsection) for:
- Criterion configuration (sample size, significance level, measurement time)
- Benchmark structure pattern
- Use of `black_box()` for preventing optimization

## Interface Contracts
- **Implements**: Minimal benchmark harness calling `execute_python()`
- **Exports**: Working benchmark infrastructure for subsequent benchmark issues
- **Consumes**:
  - Public API: `pyrust::execute_python(&str) -> Result<String, PyRustError>`
  - Criterion crate (already in dev-dependencies)
- **Consumed by**:
  - issue-02-startup-execution-benchmarks (uses same benches/ directory)
  - issue-03-cpython-comparison-benchmark (uses same Criterion config)

## Files
- **Create**: `benches/startup_benchmarks.rs` (minimal scaffold with one benchmark)
- **Modify**: `Cargo.toml` (add `[[bench]]` configuration)

## Dependencies
None (foundational infrastructure issue)

## Provides
- Working benchmark infrastructure
- Verified `cargo bench` execution path
- Template pattern for other benchmark files

## Acceptance Criteria
- [ ] `cargo bench --bench startup_benchmarks` exits with code 0
- [ ] Benchmark compiles without errors
- [ ] Can successfully call `execute_python()` from benchmark code
- [ ] Criterion outputs basic timing results to stdout
- [ ] `target/criterion/` directory is created after benchmark run

## Testing Strategy

### Test Files
- `benches/startup_benchmarks.rs`: Contains minimal scaffold benchmark

### Test Categories
- **Manual verification**: Run `cargo bench --bench startup_benchmarks` and verify:
  - Exit code 0
  - Criterion timing output appears
  - No compilation errors

### Run Command
```bash
cargo bench --bench startup_benchmarks
```

### Success Evidence
- Command exits with code 0
- Output contains "time:" measurement from Criterion
- Directory `target/criterion/` exists with subdirectories
