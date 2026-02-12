# issue-00-cpython-comparison-script: Create CPython speedup comparison script

## Description
Implement bash script that compares PyRust cold_start_simple vs CPython pure execution, calculates speedup ratio, and validates ≥50x. Uses jq to parse Criterion JSON output. Critical for AC6 validation.

## Architecture Reference
Read architecture.md Section 4.3.2 (Comparison Script Implementation) for:
- Complete bash script template with error handling
- Input file paths and JSON field extraction
- Speedup calculation formula: `speedup = cpython_time_ns / pyrust_time_ns`
- Exit code semantics (0 = PASS, 1 = FAIL)
- Output format specification

## Interface Contracts
- **Implements**: Bash script at `scripts/compare_pure_execution.sh`
- **Exports**: Speedup validation result written to `target/speedup_validation.txt`
- **Consumes**:
  - `target/criterion/cold_start_simple/base/estimates.json` (from startup_benchmarks)
  - `target/criterion/cpython_pure_simple/base/estimates.json` (from cpython-pure-execution-benchmark)
- **Consumed by**: AC6 validation test in performance-validation issue

## Files
- **Create**: `scripts/compare_pure_execution.sh` (executable, chmod +x)

## Dependencies
- issue-07-cpython-pure-execution-benchmark (provides CPython baseline JSON)

## Provides
- Automated CPython speedup validation for AC6
- Speedup validation result at `target/speedup_validation.txt`

## Acceptance Criteria
- [ ] Script exists at scripts/compare_pure_execution.sh with executable permissions
- [ ] Script reads both Criterion JSON files and extracts mean.point_estimate using jq
- [ ] Calculates speedup = cpython_time_ns / pyrust_time_ns using bc with scale=2
- [ ] Outputs 'PASS' if speedup ≥ 50.0, 'FAIL' otherwise
- [ ] Writes result to target/speedup_validation.txt
- [ ] Script exits with code 0 on PASS, code 1 on FAIL
- [ ] Script validates JSON files exist before attempting to parse

## Testing Strategy

### Test Files
- Script itself serves as validation tool for AC6

### Test Categories
- **Manual validation**: Run script after benchmarks and verify output format
- **Exit code verification**: Ensure `echo $?` returns 0 when speedup ≥50x
- **Error handling**: Run with missing JSON files and verify exit code 1

### Run Command
```bash
# Prerequisites: Run benchmarks first
cargo bench --bench startup_benchmarks
cargo bench --bench cpython_pure_execution
# Run comparison script
./scripts/compare_pure_execution.sh
# Verify result
grep 'PASS' target/speedup_validation.txt && echo $? -eq 0
```
