# issue-19-daemon-mode-benchmark: Create daemon mode latency benchmark

## Description
Implement comprehensive Criterion benchmark measuring per-request latency when daemon is running. Validates 100x speedup target (≤190μs mean) with statistical confidence (CV < 10%, 1000 samples).

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section 6.2 (Daemon Mode Benchmark) for:
- Complete benchmark structure with start_daemon(), stop_daemon(), send_daemon_request()
- Binary protocol wire format: request=[u32 len][code], response=[u8 status][u32 len][output]
- Criterion configuration: sample_size=1000, measurement_time=10s
- Validation commands for extracting mean latency from output

## Interface Contracts
- Implements: Criterion benchmark group measuring daemon request latency
- Exports: `daemon_request_2_plus_3` benchmark validating AC6.2 (≤190μs mean)
- Consumes: Daemon server at /tmp/pyrust.sock (from issue-12-daemon-server)
- Consumed by: issue-20-speedup-validation-scripts (for automated M2 validation)

## Files
- **Create**: `benches/daemon_mode.rs` (~150 LOC)
- **Modify**: `Cargo.toml` (add `[[bench]]` entry with `name = "daemon_mode"`, `harness = false`)

## Dependencies
- issue-12-daemon-server (provides: Unix socket daemon at /tmp/pyrust.sock)
- issue-14-daemon-concurrency-testing (ensures daemon stability under load)

## Provides
- Daemon mode latency benchmark validating AC6.2
- Statistical validation of 100x speedup target (M2)
- Per-request latency measurement with 1000 samples

## Acceptance Criteria
- [ ] AC6.2: Daemon mode benchmark mean ≤190μs verified in Criterion output
- [ ] M2: Per-request latency ≤190μs mean measured via 1000 requests
- [ ] Benchmark starts daemon before test, stops after completion for isolation
- [ ] AC6.4: Coefficient of variation < 10% for statistical stability
- [ ] Benchmark output includes mean, std_dev, and percentiles (p50, p95, p99)

## Testing Strategy

### Test Files
- `benches/daemon_mode.rs`: Criterion benchmark measuring daemon request latency

### Test Categories
- **Functional tests**: Daemon starts successfully, accepts 1000 requests, returns correct results
- **Performance tests**: Mean latency ≤190μs validated via Criterion statistics
- **Edge cases**: Daemon isolation (starts clean, stops completely), warmup excludes startup time

### Run Command
```bash
cargo bench --bench daemon_mode 2>&1 | tee daemon_bench.txt
grep "daemon_request_2_plus_3" daemon_bench.txt | grep "time:"
```
