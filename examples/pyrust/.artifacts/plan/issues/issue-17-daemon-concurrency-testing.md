# issue-17-daemon-concurrency-testing: Test daemon concurrent and stress scenarios

## Description
Create comprehensive test suite validating daemon stability under concurrent access (10 parallel clients) and stress conditions (10,000 sequential requests). Ensures correct results without corruption, stable performance, and proper error handling under load.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section 2.4 (CLI Integration) and Section 6.2 (Daemon Mode Benchmark) for:
- `DaemonClient::execute_or_fallback()` signature and fallback behavior
- Daemon startup/shutdown patterns for test setup/teardown
- Performance measurement techniques with Criterion and hyperfine
- Socket path constant (`SOCKET_PATH = "/tmp/pyrust.sock"`)

## Interface Contracts
- Implements:
  - `test_concurrent_clients()`: Spawns 10 threads calling `execute_or_fallback()` in parallel
  - `test_stress_sequential()`: Validates 10,000 sequential requests via shell script
  - Latency measurement: `hyperfine --runs 1000 "./target/release/pyrust -c '2+3'"`
- Exports: Test suite results confirming daemon stability
- Consumes: `daemon_client::DaemonClient::execute_or_fallback()` from issue-16
- Consumed by: issue-22 (final-integration-validation)

## Files
- **Create**: `tests/test_daemon_concurrency.rs`
- **Create**: `scripts/daemon_stress_test.sh`

## Dependencies
- issue-16 (daemon-cli-integration): Provides daemon server, client, and CLI commands

## Provides
- Daemon concurrency validation (AC2.6)
- Daemon stress test validation (AC2.7)
- Performance stability confirmation (M2)

## Acceptance Criteria
- [ ] AC2.6: 10 parallel threads execute `execute_or_fallback()` simultaneously, all return correct results without corruption
- [ ] AC2.7: Shell script executes 10,000 sequential daemon requests with <1% failure rate
- [ ] M2: `hyperfine --runs 1000` reports mean latency ≤190μs for daemon requests
- [ ] No memory leaks: RSS before/after stress test differs by <1MB
- [ ] Performance stability: Latency variance (CV) <10% throughout stress test

## Testing Strategy

### Test Files
- `tests/test_daemon_concurrency.rs`: Rust integration tests for parallel client access
- `scripts/daemon_stress_test.sh`: Bash script for sequential stress testing

### Test Categories
- **Concurrency tests**: Spawn 10 threads using `std::thread::spawn`, each calling `execute_or_fallback("2+3")`, join all threads and assert all results equal "5"
- **Stress tests**: Loop 10,000 iterations calling `pyrust -c '2+3'`, count failures, assert failure_count / 10000 < 0.01
- **Performance tests**: Use `hyperfine --warmup 100 --runs 1000` to measure mean/stddev, assert mean ≤190μs and CV <10%
- **Memory leak tests**: Capture RSS before/after stress test via `/proc/self/status` or `ps`, assert delta <1MB

### Run Command
```bash
# Concurrency test
cargo test --test test_daemon_concurrency --release

# Stress test (requires daemon running)
./scripts/daemon_stress_test.sh

# Performance validation
hyperfine --warmup 100 --runs 1000 --show-output './target/release/pyrust -c "2+3"'
```
