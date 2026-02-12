# issue-15-binary-subprocess-benchmark: Create binary subprocess benchmark suite

## Description
Implement Criterion-based benchmark suite measuring end-to-end binary execution via `Command::new()`. Validates 50x speedup target (≤380μs mean) for optimized PyRust binary vs 19ms CPython baseline. Includes statistical analysis with CV < 10% for reproducible performance claims.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section 6.1 (Binary Subprocess Benchmark) for:
- Complete `benches/binary_subprocess.rs` implementation
- Criterion configuration with sample_size=100, measurement_time=10s
- Workload scenarios: simple, complex, variables, print
- Cargo.toml benchmark entry configuration

## Interface Contracts
- Implements: `criterion_group!` and `criterion_main!` macros with custom config
- Benchmarks:
  - `binary_subprocess_simple(c: &mut Criterion)` - single workload "2 + 3"
  - `binary_subprocess_workloads(c: &mut Criterion)` - 4 workload variants
- Command invocation: `Command::new("./target/release/pyrust").arg("-c").arg(code).output()`

## Files
- **Create**: `benches/binary_subprocess.rs`
- **Modify**: `Cargo.toml` (add `[[bench]]` entry with name="binary_subprocess", harness=false)

## Dependencies
- issue-01-binary-optimization (provides: Optimized release binary at ./target/release/pyrust)

## Provides
- Binary subprocess benchmark measuring full end-to-end execution time
- Statistical validation of 50x speedup target (mean ≤380μs)
- Workload-specific performance baselines for regression detection

## Acceptance Criteria
- [ ] AC6.1: Binary subprocess benchmark mean ≤380μs verified in Criterion output
- [ ] M1: Binary subprocess execution ≤380μs mean measured via hyperfine 100 runs
- [ ] Benchmark includes warmup (2s) and statistical analysis (10s measurement time)
- [ ] CV < 10% for statistical stability across all workload scenarios

## Testing Strategy

### Test Files
- `benches/binary_subprocess.rs`: Measures subprocess spawn + execution overhead

### Test Categories
- **Performance tests**: Verify mean execution time ≤380μs for simple workload
- **Workload variety**: Test 4 scenarios (simple, complex, variables, print) for regression detection
- **Statistical stability**: Ensure CV < 10% by inspecting Criterion estimates.json

### Run Command
```bash
cargo build --release
cargo bench --bench binary_subprocess
grep "binary_subprocess_2_plus_3" target/criterion/binary_subprocess_2_plus_3/*/estimates.json
```
