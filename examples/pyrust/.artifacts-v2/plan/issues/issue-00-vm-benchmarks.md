# issue-00-vm-benchmarks: Create granular VM-only benchmarks

## Description
Implement standalone VM benchmarks that measure pure VM execution time for pre-compiled bytecode (simple/complex/variable expressions). Isolates VM performance from lexer, parser, and compiler stages. Critical for validating AC1 (VM overhead <150ns) and establishing baseline for VM optimizations.

## Architecture Reference
Read `architecture.md` Section 4.1.5 (Implementation: VM Benchmarks) for:
- Pre-compilation strategy (compile once outside benchmark loop)
- Benchmark function signatures (vm_simple, vm_complex, vm_variables)
- Criterion configuration (sample_size: 1000, measurement_time: 10s)
- Black-box pattern for VM::new() and vm.execute()

## Interface Contracts
- Implements: Criterion benchmark suite with 3 benchmark functions
- Exports:
  - `target/criterion/vm_simple/base/estimates.json` with `mean.point_estimate` field
  - `target/criterion/vm_complex/base/estimates.json` with performance data
  - `target/criterion/vm_variables/base/estimates.json` with performance data
- Consumes: Bytecode from `compile()` function (pre-compiled outside loop)
- Consumed by: performance-validation (extracts vm_simple timing for AC1 validation)

## Files
- **Create**: `benches/vm_benchmarks.rs`
- **Modify**: `Cargo.toml` (add [[bench]] entry for vm_benchmarks)

## Dependencies
- None (foundation issue)

## Provides
- VM-only performance baseline measurements
- Criterion JSON output at target/criterion/vm_simple/base/estimates.json for AC1 validation

## Acceptance Criteria
- [ ] Create benches/vm_benchmarks.rs with vm_simple, vm_complex, vm_variables benchmarks
- [ ] Pre-compile bytecode outside benchmark loop to isolate VM performance
- [ ] Criterion generates estimates.json for each benchmark with mean.point_estimate field
- [ ] vm_simple benchmark measures pure VM execution for 2+3 expression

## Testing Strategy

### Test Files
- `benches/vm_benchmarks.rs`: Contains all 3 VM-only benchmark functions

### Test Categories
- **Functional tests**: Run `cargo bench --bench vm_benchmarks` to verify all 3 benchmarks execute
- **Output validation**: Verify `target/criterion/vm_simple/base/estimates.json` exists after benchmark run
- **Data extraction**: Use `jq '.mean.point_estimate' < target/criterion/vm_simple/base/estimates.json` to extract VM timing

### Run Command
```bash
cargo bench --bench vm_benchmarks && test -f target/criterion/vm_simple/base/estimates.json
```
