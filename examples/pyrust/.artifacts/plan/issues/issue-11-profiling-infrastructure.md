# issue-11-profiling-infrastructure: Add pipeline profiling with per-stage timing

## Description
Create profiling infrastructure to track execution time for each pipeline stage (lex, parse, compile, vm_execute, format). Provides human-readable table and JSON output for optimization guidance. Essential for identifying bottlenecks in the 50-100x speedup effort.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section "Phase 5: Profiling Infrastructure" (Component 5.1 and 5.2) for:
- `PipelineProfile` struct with 6 timing fields (lex_ns, parse_ns, compile_ns, vm_execute_ns, format_ns, total_ns)
- `execute_python_profiled()` function using `Instant::now()` for stage timing
- `format_table()` and `format_json()` output methods
- `validate_timing_sum()` method for 5% accuracy check
- CLI integration pattern with `--profile` and `--profile-json` flags
- Output routing: stdout for results, stderr for profiling data

## Interface Contracts
```rust
// src/profiling.rs
pub struct PipelineProfile { lex_ns: u64, parse_ns: u64, compile_ns: u64, vm_execute_ns: u64, format_ns: u64, total_ns: u64 }
pub fn execute_python_profiled(code: &str) -> Result<(String, PipelineProfile), PyRustError>
impl PipelineProfile { pub fn format_table(&self) -> String; pub fn format_json(&self) -> String; pub fn validate_timing_sum(&self) -> bool }
```

- **Exports**: `PipelineProfile` struct, `execute_python_profiled()` function
- **Consumes**: `lexer::lex()`, `parser::parse()`, `compiler::compile()`, `vm::VM`, `PyRustError` from existing modules
- **Consumed by**: `src/main.rs` for CLI profiling flags, benchmarks for overhead measurement, PERFORMANCE.md for stage analysis

## Files
- **Create**: `src/profiling.rs`
- **Modify**: `src/lib.rs` (add `pub mod profiling;`), `src/main.rs` (add profiling flag handling)

## Dependencies
None - uses existing pipeline components

## Provides
- PipelineProfile struct with per-stage nanosecond timings
- execute_python_profiled() function with instrumentation
- Human-readable table format and JSON output
- Timing validation within 5% accuracy

## Acceptance Criteria
- [ ] AC5.1: `pyrust -c '2+3' --profile` outputs table with 5 stage timings in nanoseconds
- [ ] AC5.2: Sum of stage timings within 5% of total measured time (verified by `validate_timing_sum()`)
- [ ] AC5.3: `--profile-json` outputs valid JSON matching PipelineProfile schema
- [ ] AC5.4: Profiling overhead ≤20% measured by comparing execute_python vs execute_python_profiled

## Testing Strategy

### Test Files
- `tests/test_profiling.rs`: Integration tests for profiling accuracy and output formats
- `benches/profiling_overhead.rs`: Benchmark comparing profiled vs non-profiled execution

### Test Categories
- **Integration tests**:
  - Run `pyrust -c '2+3' --profile` via Command::new() and parse stdout/stderr
  - Verify 5 stages present in table output
  - Sum individual stages and compare to total (within 5%)
  - Test `--profile-json` and validate JSON schema with serde_json
- **Functional tests**:
  - Test `validate_timing_sum()` returns true for valid profiles
  - Test output routing (stdout for code output, stderr for profile)
  - Test profile accuracy with known slow operations
- **Edge cases**:
  - Empty code execution profiling
  - Error handling (profiling on syntax errors, runtime errors)
  - Very fast operations (<100ns) timing accuracy

### Run Command
```bash
cargo test --release test_profiling
cargo bench profiling_overhead
```
