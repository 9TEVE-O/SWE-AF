# issue-03-cpython-comparison-benchmark: CPython Baseline Comparison

## Description
Create benchmarks comparing PyRust performance against CPython 3.x for identical code to validate AC1.3 (≥50x speedup). Measures both library-level comparison (fair) and CLI comparison (includes startup overhead).

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section "Testing Strategy" (comparative benchmark) for:
- Subprocess-based CPython measurement approach
- Statistical analysis methodology
- Speedup ratio calculation from criterion JSON outputs

## Interface Contracts
- Implements: Criterion benchmarks using `std::process::Command` for subprocess execution
- Exports: `cpython_subprocess_baseline` benchmark measuring `python3 -c "2 + 3"`
- Consumes: Working benchmark infrastructure from issue-01
- Consumed by: issue-04 (PERFORMANCE.md documentation)

## Files
- **Create**: `benches/cpython_baseline.rs` (Criterion benchmark for CPython comparison)
- **Create**: `scripts/compare_cpython.sh` (Optional: Automates ratio calculation from JSON)

## Dependencies
- issue-01-benchmark-infrastructure-setup (provides: Working Criterion setup)

## Provides
- AC1.3 validation: ≥50x speedup vs CPython documented with statistical confidence
- Reproducible comparison methodology
- Automated speedup ratio calculation

## Acceptance Criteria
- [ ] `cargo bench --bench cpython_baseline` runs successfully
- [ ] Benchmark verifies `python3` is available on system (fails gracefully if missing)
- [ ] Speedup ratio ≥50x between PyRust and CPython subprocess execution
- [ ] Results include statistical confidence intervals (criterion default: 95%)
- [ ] Both warm execution (VM-only) and total time (cold start) comparisons implemented

## Testing Strategy

### Test Files
- `benches/cpython_baseline.rs`: Measures CPython subprocess execution vs PyRust execution

### Test Categories
- **Subprocess benchmarks**: `python3 -c "2 + 3"` execution time via Command::spawn
- **PyRust benchmarks**: `execute_python("2 + 3")` execution time for comparison
- **Speedup calculation**: Parse criterion JSON, compute ratio ≥ 50

### Run Command
`cargo bench --bench cpython_baseline`

### Verification
`jq '.mean.point_estimate' < target/criterion/cpython_subprocess_baseline/base/estimates.json`
