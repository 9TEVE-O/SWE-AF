# issue-00-performance-validation: Validate All Performance Acceptance Criteria

## Description
Execute comprehensive validation of all performance acceptance criteria (AC1-AC4, AC6) by running benchmarks and validation scripts. Confirms VM overhead <150ns, allocations ≤5, per-stage benchmarks exist, cold start <500ns with CV <10%, and speedup ≥50x vs CPython. Final validation gate for performance optimization sprint.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts-v2/plan/architecture.md` Section 4 (Benchmarking Infrastructure) for:
- Section 4.1: Per-stage benchmark validation methodology
- Section 4.2: dhat-based allocation profiling strategy
- Section 4.3: CPython pure execution baseline comparison approach

Read PRD Section 3 (Acceptance Criteria) for pass/fail conditions.

## Interface Contracts
- Validates: All benchmark suites produce valid Criterion JSON output
- Validates: VM execution time from `target/criterion/vm_simple/base/estimates.json`
- Validates: Allocation count via `cargo test --features dhat-heap test_allocation_count`
- Validates: Speedup calculation from `./scripts/compare_pure_execution.sh`
- Produces: Updated `PERFORMANCE.md` with before/after comparison table

## Files
- **Modify**: `PERFORMANCE.md` (add validation results section with actual measured values)

## Dependencies
- issue-01-value-copy-trait (provides: Copy semantics for Value)
- issue-02-lexer-benchmarks (provides: lexer_simple benchmark JSON)
- issue-03-parser-benchmarks (provides: parser_simple benchmark JSON)
- issue-04-compiler-benchmarks (provides: compiler_simple benchmark JSON)
- issue-05-vm-benchmarks (provides: vm_simple benchmark JSON for AC1)
- issue-06-cpython-pure-execution-benchmark (provides: CPython baseline)
- issue-07-cpython-comparison-script (provides: speedup validation script)
- issue-08-allocation-profiling-test (provides: AC2 allocation test)
- issue-09-vm-register-bitmap (provides: VM optimization for AC1)
- issue-10-variable-name-interning (provides: allocation reduction)
- issue-11-register-state-optimization (provides: function call optimization)
- issue-12-smallstring-stdout-optimization (provides: stdout allocation reduction)
- issue-13-integration-verification (provides: AC5 test suite validation)

## Provides
- Full validation of AC1 (VM <150ns)
- Full validation of AC2 (≤5 allocations)
- Full validation of AC3 (per-stage benchmarks exist)
- Full validation of AC4 (no regression: cold start <500ns, CV <10%)
- Full validation of AC6 (≥50x speedup vs CPython)
- Updated PERFORMANCE.md documentation with measured results

## Acceptance Criteria
- [ ] AC1 validation: `cargo bench --bench vm_benchmarks && jq '.mean.point_estimate' < target/criterion/vm_simple/base/estimates.json` shows <150000 (150ns)
- [ ] AC2 validation: `cargo test --features dhat-heap test_allocation_count -- --ignored --nocapture` shows ≤5 allocations
- [ ] AC3 validation: All 4 per-stage benchmarks execute and produce JSON output files
- [ ] AC4 validation: `cargo bench --bench startup_benchmarks` shows cold_start_simple <500000ns and CV <0.10
- [ ] AC6 validation: `./scripts/compare_pure_execution.sh | grep 'PASS'` outputs PASS
- [ ] PERFORMANCE.md updated with table showing before/after metrics for all ACs

## Testing Strategy

### Test Files
No new test files - uses existing benchmark infrastructure and validation scripts from dependency issues.

### Test Categories
- **AC1 Validation**: Run `cargo bench --bench vm_benchmarks`, extract vm_simple mean from JSON, verify <150000
- **AC2 Validation**: Run allocation profiling test with dhat feature, verify stderr output shows ≤5
- **AC3 Validation**: Execute all 4 per-stage benchmarks sequentially, verify JSON files exist in target/criterion/
- **AC4 Validation**: Run startup_benchmarks, extract cold_start_simple mean and std_dev, calculate CV, verify both conditions
- **AC6 Validation**: Execute CPython comparison script, verify exit code 0 and grep for PASS
- **Documentation**: Update PERFORMANCE.md with actual measured values in table format

### Run Command
```bash
# Execute validation in sequence
cargo bench --bench vm_benchmarks
cargo test --features dhat-heap test_allocation_count -- --ignored --nocapture
cargo bench --bench lexer_benchmarks && cargo bench --bench parser_benchmarks && cargo bench --bench compiler_benchmarks
cargo bench --bench startup_benchmarks
./scripts/compare_pure_execution.sh | grep 'PASS'
```
