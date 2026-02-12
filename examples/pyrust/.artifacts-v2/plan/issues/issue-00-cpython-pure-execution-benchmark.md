# issue-00-cpython-pure-execution-benchmark: Create CPython pure execution baseline benchmark

## Description
Implement CPython pure execution benchmark using pyo3 Python C API to measure execution time excluding interpreter startup overhead. This benchmark is critical for AC6 validation (50x speedup comparison) and provides the baseline against which PyRust's performance is measured.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts-v2/plan/architecture.md` Section 4.3 (CPython Pure Execution Baseline) for:
- `pyo3::prepare_freethreaded_python()` initialization pattern
- `Python::with_gil()` measurement loop structure
- `py.eval()` usage for pure execution measurement
- Criterion configuration (1000 samples, 10s measurement time)

## Interface Contracts
- Implements: Criterion benchmark function `cpython_pure_simple(c: &mut Criterion)`
- Exports: JSON output at `target/criterion/cpython_pure_simple/base/estimates.json`
- Consumes: pyo3 crate for Python C API access
- Consumed by: `cpython-comparison-script` (reads estimates.json for speedup calculation)

## Files
- **Create**: `benches/cpython_pure_execution.rs`
- **Modify**: `Cargo.toml` (add pyo3 dev-dependency with auto-initialize feature, add benchmark harness entry)

## Dependencies
None (this is the first benchmark issue)

## Provides
- CPython pure execution baseline without subprocess overhead
- Criterion JSON output at target/criterion/cpython_pure_simple/base/estimates.json

## Acceptance Criteria
- [ ] Benchmark file created at benches/cpython_pure_execution.rs
- [ ] Uses pyo3::prepare_freethreaded_python() once outside measurement loop
- [ ] Benchmark measures py.eval('2 + 3') within Python::with_gil block
- [ ] Criterion generates estimates.json at target/criterion/cpython_pure_simple/base/estimates.json
- [ ] pyo3 dev-dependency added to Cargo.toml with auto-initialize feature

## Testing Strategy

### Test Files
- `benches/cpython_pure_execution.rs`: Criterion benchmark measuring CPython py.eval() execution time

### Test Categories
- **Functional test**: Run `cargo bench --bench cpython_pure_execution` and verify successful execution
- **Output validation**: Check that `target/criterion/cpython_pure_simple/base/estimates.json` exists
- **Data validation**: Verify JSON contains `mean.point_estimate` field with numeric value

### Run Command
`cargo bench --bench cpython_pure_execution && test -f target/criterion/cpython_pure_simple/base/estimates.json`
