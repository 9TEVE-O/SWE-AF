# issue-01-binary-optimization: Implement binary optimization via LTO and static linking

## Description
Reduce binary startup overhead from 1.3ms to <500μs through aggressive compiler optimizations (LTO, symbol stripping, single codegen unit, panic=abort) and static linking configuration. This eliminates the 14x speedup bottleneck and establishes the foundation for achieving 50-100x end-to-end performance vs CPython.

## Architecture Reference
Read architecture.md Section "Phase 1: Binary Optimization" for:
- Component 1.1: Cargo Profile Configuration (opt-level, lto, codegen-units, strip, panic settings)
- Component 1.2: Static Linking Configuration (target-cpu=native, prefer-dynamic=no, platform-specific rustflags)
- Performance budget breakdown (577KB → ≤500KB binary size, 1.3ms → ≤500μs startup)
- Validation commands using hyperfine and stat
- Rollback strategy if targets not met

## Interface Contracts
No new API contracts - pure build configuration changes. Existing library API must remain unchanged:
```rust
pub fn execute_python(code: &str) -> Result<String, PyRustError>  // 293ns ±10% maintained
```

## Files
- **Modify**: `Cargo.toml` (add `[profile.release]` section after `[dev-dependencies]`)
- **Create**: `.cargo/config.toml` (static linking flags with platform-specific targets)

## Dependencies
None - independent phase, foundation for issue-10 (daemon-server).

## Provides
- Optimized release build configuration with LTO and static linking
- Reduced binary startup overhead to <500μs
- Binary size reduced to <500KB

## Acceptance Criteria
- [ ] AC1.1: `cargo build --release` completes successfully with new [profile.release] configuration
- [ ] AC1.2: Binary size ≤500KB measured via `stat -f%z target/release/pyrust` (macOS) or `stat -c%s` (Linux)
- [ ] AC1.3: Binary startup overhead ≤500μs mean measured via hyperfine 100 runs with 95% CI upper bound
- [ ] AC1.4: All 664 currently passing tests still pass after optimization (`cargo test --release`)
- [ ] AC1.5: Library API performance unchanged at 293ns ±10% verified via existing Criterion benchmarks

## Testing Strategy

### Test Files
- `scripts/measure_binary_startup.sh`: Hyperfine-based startup measurement with JSON export and automated validation
- Existing test suite: `cargo test --release` for regression detection
- Existing benchmarks: `benches/execution_benchmarks.rs` for library API performance validation

### Test Categories
- **Build validation**: Verify release build succeeds with new profile settings
- **Binary size checks**: Automated stat command validation against 500KB threshold
- **Startup latency**: Hyperfine 100 runs with statistical confidence interval analysis
- **Regression tests**: Full test suite execution ensuring no failures from optimization changes
- **Performance benchmarks**: Criterion benchmark suite verifying 293ns library API unchanged

### Run Command
```bash
cargo build --release
scripts/measure_binary_startup.sh  # Creates and validates with hyperfine
cargo test --release               # Verify 664 tests pass
cargo bench                        # Verify library performance unchanged
```
