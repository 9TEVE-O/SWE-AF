# issue-21-speedup-validation-scripts: Create automated speedup validation scripts

## Description
Implement automated validation scripts using hyperfine to verify PyRust achieves ≥50x speedup vs CPython (19ms baseline). Provides CI-ready scripts for binary, daemon, and overall speedup validation with statistical analysis (CV < 10%).

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section 6.4 (Speedup Validation Script) for:
- Complete `scripts/validate_speedup.sh` implementation with hyperfine + jq parsing
- Exit code conventions (0 = pass ≥50x, 1 = fail <50x)
- JSON extraction patterns for mean times and speedup calculation
- Dependencies: hyperfine, jq, bc

## Interface Contracts
Scripts implement bash validation with structured output:
```bash
# Primary script validates overall speedup
./scripts/validate_speedup.sh → exit 0 if speedup ≥50x, exit 1 otherwise
# Binary-specific validation
./scripts/validate_binary_speedup.sh → exit 0 if mean ≤380μs
# Daemon-specific validation
./scripts/validate_daemon_speedup.sh → exit 0 if mean ≤190μs
# Benchmark stability validation
./scripts/validate_benchmark_stability.sh → exit 0 if all CV < 10%
```

## Files
- **Create**: `scripts/validate_speedup.sh` (main validation, AC6.5)
- **Create**: `scripts/validate_binary_speedup.sh` (binary-specific check)
- **Create**: `scripts/validate_daemon_speedup.sh` (daemon-specific check)
- **Create**: `scripts/validate_benchmark_stability.sh` (CV check for AC6.4)

## Dependencies
- issue-19 (binary-subprocess-benchmark): Provides binary benchmarks to validate
- issue-20 (daemon-mode-benchmark): Provides daemon benchmarks to validate

## Provides
- Automated speedup validation scripts for CI integration
- Statistical confidence in 50x+ speedup claims
- Benchmark stability validation (CV < 10%)

## Acceptance Criteria
- [ ] AC6.5: `scripts/validate_speedup.sh` exits 0 indicating ≥50x speedup vs CPython baseline
- [ ] AC6.4: `scripts/validate_benchmark_stability.sh` parses Criterion JSON and validates CV < 10% for all benchmarks
- [ ] Scripts use hyperfine with --runs 100 for statistical rigor
- [ ] Output includes mean, stddev, min, max, speedup ratio in human-readable format
- [ ] All scripts executable (chmod +x) and include error handling (set -e)

## Testing Strategy

### Test Files
- **Manual validation**: Run each script and verify exit codes and output format

### Test Categories
- **Functional tests**: Execute validate_speedup.sh, verify exit 0 when speedup met, exit 1 when not met
- **Integration tests**: Run validate_binary_speedup.sh and validate_daemon_speedup.sh, confirm correct threshold checks (380μs, 190μs)
- **Edge cases**: Test validate_benchmark_stability.sh with mock Criterion JSON showing high/low CV values
- **Cross-platform**: Verify scripts work on both macOS (using `stat -f%z`) and Linux (using `stat -c%s`) if available

### Run Command
```bash
# Validate speedup target achieved
./scripts/validate_speedup.sh

# Validate benchmark stability
./scripts/validate_benchmark_stability.sh

# Individual mode validation
./scripts/validate_binary_speedup.sh
./scripts/validate_daemon_speedup.sh
```
