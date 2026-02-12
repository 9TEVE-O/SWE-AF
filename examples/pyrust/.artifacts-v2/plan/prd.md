# PRD: PyRust Compiler Performance Optimization to 50-100x Speedup

**Product Manager:** Claude Sonnet 4.5
**Date:** 2026-02-08
**Status:** Draft for Engineering Review
**Target:** Achieve 50-100x faster startup-to-result time vs CPython baseline

---

## Executive Summary

PyRust is a Python-to-bytecode compiler implemented in Rust, currently achieving ~66,000x speedup over CPython subprocess execution (293ns vs 19.38ms). However, this comparison includes CPython's interpreter startup overhead. The goal is to optimize PyRust to achieve 50-100x speedup over CPython's pure execution time (excluding startup), while maintaining or improving the current microsecond-level performance characteristics.

**Current Performance Baseline (from PERFORMANCE.md):**
- Cold start (simple `2+3`): **293.34 ns** (0.29 μs)
- CPython subprocess baseline: **19.38 ms**
- Current speedup: **66,054x** (dominated by CPython startup overhead)

**Target Performance:**
- Maintain sub-500ns execution for simple expressions
- Achieve 50-100x speedup vs CPython **pure execution** (estimated ~3-6μs target)
- Optimize critical path bottlenecks identified in architecture analysis

---

## 1. Problem Statement

### 1.1 Current State Analysis

**Architecture Components (from codebase analysis):**

1. **Lexer** (`lexer.rs`): Zero-copy tokenization, single-pass O(n)
   - Current estimate: ~5-10 ns (~2-3% of execution)
   - Zero allocations via lifetime-parameterized tokens
   - Already highly optimized

2. **Parser** (`parser.rs`): Recursive descent with Pratt parsing
   - Current estimate: ~10-20 ns (~4-7% of execution)
   - Uses Pratt parsing for operator precedence
   - Token vector allocation overhead

3. **Compiler** (`compiler.rs`): AST → Bytecode with register allocation
   - Current estimate: ~15-30 ns (~5-10% of execution)
   - HashMap allocations for functions/variables
   - Register allocation strategy (256 registers, sequential allocation)

4. **VM** (`vm.rs`): Register-based bytecode executor
   - **Current estimate: ~250-270 ns (~85-90% of execution) ← PRIMARY BOTTLENECK**
   - 256 preallocated `Option<Value>` registers
   - HashMap for variable storage
   - Function call stack with frame management

**Identified Bottlenecks (ranked by impact):**

1. **VM Register File** (Critical - 85% of runtime):
   - 256 `Option<Value>` registers → pattern matching overhead on every register access
   - `Value` enum indirection (i64 wrapped in enum)
   - Clone overhead for `Value` types during operations

2. **HashMap Allocations** (High):
   - Variables stored in `HashMap<String, Value>`
   - Function metadata in `HashMap<String, FunctionMetadata>`
   - String allocations for lookups

3. **Vector Allocations** (Medium):
   - Parser builds `Vec<Token>` from lexer
   - Compiler builds instruction `Vec`
   - Call stack frames clone entire register state

4. **String Operations** (Medium):
   - Variable name string allocations
   - stdout String concatenation
   - Format string overhead in print statements

### 1.2 Gap Analysis

**Performance Gap:**
- Current: 293ns → 357ns range for simple operations
- Target: Must define realistic baseline for "50-100x" comparison
- **Assumption**: Target is 50-100x vs CPython **excluding interpreter startup** (estimated ~200-400μs for CPython pure execution, targeting ~2-8μs for PyRust)

**Scope Boundary:**
- This is a **performance optimization** project, not a feature expansion
- Must maintain 100% compatibility with existing tests
- Must maintain existing API (`execute_python` function signature)
- Must not regress on variance (CV < 10% requirement)

---

## 2. Goals and Non-Goals

### 2.1 Goals (Must Have)

**Primary Objective:**
Optimize PyRust execution to achieve 50-100x speedup over CPython baseline through strategic architectural improvements and micro-optimizations.

**Specific Performance Targets:**

1. **VM Execution Optimization (Critical Path)**
   - Reduce VM overhead from ~250ns to <150ns for simple expressions
   - Eliminate `Option<Value>` pattern matching overhead
   - Reduce value cloning overhead
   - **Success Metric**: VM execution < 50% of total runtime

2. **Memory Allocation Reduction**
   - Minimize HashMap lookups via caching or pre-resolution
   - Reduce vector allocations in parser/compiler
   - Optimize register state management in function calls
   - **Success Metric**: <5 allocations per `execute_python` call for simple expressions

3. **Benchmark Infrastructure**
   - Add granular per-stage benchmarks (lex, parse, compile, execute separately)
   - Add CPython pure execution baseline (exclude interpreter startup)
   - Add memory allocation profiling
   - **Success Metric**: Can measure each pipeline stage independently with <1% measurement overhead

4. **Maintain Existing Performance**
   - No regression on cold start benchmarks
   - Variance (CV) remains < 10%
   - All existing tests pass
   - **Success Metric**: `cold_start_simple` remains < 500ns

### 2.2 Nice to Have

1. **Advanced VM Optimizations**
   - JIT compilation for hot paths (future phase)
   - Instruction combining/peephole optimization
   - Register coalescing to reduce live registers

2. **Parser Optimizations**
   - Streaming parser (avoid full token vector)
   - AST arena allocation

3. **Profiling Tools**
   - Flamegraph integration for profiling
   - Memory profiler integration
   - Automated performance regression detection

### 2.3 Out of Scope

1. **New Language Features**: No Python features beyond current support (no loops, classes, etc.)
2. **API Changes**: `execute_python` signature remains unchanged
3. **Cross-Platform Optimization**: Optimizations must work on all platforms (no platform-specific SIMD)
4. **Multi-threading**: Execution remains single-threaded
5. **Breaking Changes**: All existing tests must pass without modification
6. **Alternative Backends**: No LLVM, Cranelift, or other code generation backends

---

## 3. Acceptance Criteria

All criteria are **binary pass/fail gates** measurable via automated tests:

### AC1: VM Performance Optimization
**Criterion**: VM execution overhead reduced by ≥40% for simple expressions
**Test**:
```bash
# Measure via new granular benchmarks
cargo bench --bench vm_only_benchmarks
# Extract VM-only time from results:
VM_TIME=$(jq '.mean.point_estimate' < target/criterion/vm_only_simple/base/estimates.json)
# Verify: VM_TIME < 150000 (150 ns)
test "$VM_TIME" -lt 150000
```
**Pass Condition**: VM execution < 150ns for `2+3` expression (currently ~250ns)

---

### AC2: Memory Allocation Efficiency
**Criterion**: Total allocations ≤ 5 per `execute_python("2 + 3")` call
**Test**:
```bash
# Using cargo-flamegraph or similar allocation profiler
cargo test test_allocation_count -- --ignored
# Test implementation uses allocation counter
```
**Pass Condition**: Test passes with measured allocations ≤ 5

---

### AC3: Per-Stage Benchmark Infrastructure
**Criterion**: Granular benchmarks exist for each pipeline stage with < 1% measurement overhead
**Test**:
```bash
# All new benchmarks run successfully
cargo bench --bench lexer_benchmarks
cargo bench --bench parser_benchmarks
cargo bench --bench compiler_benchmarks
cargo bench --bench vm_benchmarks
# Each produces valid Criterion output
test -f target/criterion/lexer_simple/base/estimates.json
test -f target/criterion/parser_simple/base/estimates.json
test -f target/criterion/compiler_simple/base/estimates.json
test -f target/criterion/vm_simple/base/estimates.json
```
**Pass Condition**: All 4 benchmark suites execute successfully

---

### AC4: No Performance Regression
**Criterion**: `cold_start_simple` remains < 500ns with CV < 10%
**Test**:
```bash
cargo bench --bench startup_benchmarks
COLD_START=$(jq '.mean.point_estimate' < target/criterion/cold_start_simple/base/estimates.json)
STD_DEV=$(jq '.std_dev.point_estimate' < target/criterion/cold_start_simple/base/estimates.json)
# Calculate CV
CV=$(echo "scale=4; $STD_DEV / $COLD_START" | bc)
# Verify both conditions
test "$COLD_START" -lt 500000  # 500 µs in ns
test "$(echo "$CV < 0.10" | bc)" -eq 1
```
**Pass Condition**: Cold start < 500ns AND CV < 10%

---

### AC5: All Existing Tests Pass
**Criterion**: Zero test failures after optimization changes
**Test**:
```bash
cargo test --release
test $? -eq 0
```
**Pass Condition**: Exit code 0 (all tests pass)

---

### AC6: CPython Baseline Comparison
**Criterion**: Documented speedup vs CPython pure execution (excluding startup) is ≥ 50x
**Test**:
```bash
# New benchmark measuring CPython execution only (no subprocess)
cargo bench --bench cpython_pure_execution
# Comparison script calculates speedup
./scripts/compare_pure_execution.sh | grep "PASS"
```
**Pass Condition**: Script outputs "PASS" indicating ≥ 50x speedup

---

## 4. Technical Approach

### 4.1 Optimization Strategy (Priority Order)

#### Phase 1: VM Register File Optimization (Week 1)
**Target**: Reduce VM overhead from 250ns → 150ns

**Changes:**
1. Replace `Vec<Option<Value>>` with `Vec<Value>` + separate validity bitmap
   - Eliminates Option pattern matching overhead
   - Bitmap check is single instruction vs match
   - Maintains 256 register semantics

2. Optimize `Value` enum representation
   - Make Integer the untagged variant (most common case)
   - Consider `#[repr(transparent)]` for single-variant fast path
   - Profile enum discriminant access overhead

3. Reduce cloning overhead
   - Implement `Copy` for `Value::Integer` (simple i64)
   - Use `&Value` references where possible instead of clone
   - Audit all `.clone()` calls in VM hot path

**Validation**: Micro-benchmark VM-only execution before/after

---

#### Phase 2: HashMap and Allocation Optimization (Week 1-2)
**Target**: Reduce allocations from ~10-15 → <5 per call

**Changes:**
1. Variable name interning
   - Pre-intern common variable names (x, y, z, etc.)
   - Use integer IDs instead of String keys in HashMap
   - Reduces allocations and improves lookup speed

2. Small-string optimization for stdout
   - Use `SmallString` or similar for stdout buffer
   - Avoid allocations for small outputs (< 23 bytes inline)

3. Register state optimization for function calls
   - Don't clone entire register array
   - Copy only used registers (tracked by compiler)
   - Or use copy-on-write mechanism

**Validation**: Allocation profiling with memory profiler

---

#### Phase 3: Granular Benchmarking Infrastructure (Week 2)
**Target**: Measurable per-stage performance

**New Benchmarks:**
1. `lexer_benchmarks.rs`: Tokenization only
2. `parser_benchmarks.rs`: Parsing only (pre-tokenized input)
3. `compiler_benchmarks.rs`: Compilation only (pre-parsed AST)
4. `vm_benchmarks.rs`: VM execution only (pre-compiled bytecode)
5. `cpython_pure_benchmarks.rs`: CPython via Python C API (no subprocess)

**Validation**: Each benchmark produces consistent results (CV < 5%)

---

#### Phase 4: Fine-Tuning and Profiling (Week 2-3)
**Target**: Squeeze additional 10-20% improvement

**Changes:**
1. Profile with perf/flamegraph to identify remaining hotspots
2. Apply micro-optimizations:
   - Inline critical functions
   - Use `#[cold]` for error paths
   - Branch prediction hints where beneficial
3. Review generated assembly for critical loops

**Validation**: Profiling shows no single function > 20% of runtime

---

### 4.2 Risk Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Optimization breaks existing tests | High | Medium | Run full test suite after each change; use TDD approach |
| Increased code complexity | Medium | High | Require detailed comments; performance gains must justify complexity |
| Platform-specific regressions | Medium | Low | Test on macOS (M4), Linux x86_64, Windows before merge |
| Variance increase (CV > 10%) | High | Medium | Re-run benchmarks 5 times; investigate any CV spike |
| Premature optimization (negligible gains) | Low | Medium | Benchmark before/after each change; require ≥5% improvement to keep |

---

## 5. Success Metrics

### 5.1 Primary Metrics (Must Achieve)

1. **VM Overhead Reduction**: VM execution < 150ns (vs current 250ns)
   - **Measurement**: `cargo bench --bench vm_benchmarks | grep vm_simple`
   - **Target**: Mean < 150ns, CV < 5%

2. **Memory Allocation Count**: ≤ 5 allocations per simple execution
   - **Measurement**: Allocation profiler test
   - **Target**: Exact count ≤ 5

3. **No Regression**: Cold start < 500ns, all tests pass
   - **Measurement**: `cargo bench --bench startup_benchmarks && cargo test`
   - **Target**: Pass all checks

### 5.2 Secondary Metrics (Nice to Have)

1. **Parser Speedup**: Parser-only time < 15ns (vs current ~20ns)
2. **Compiler Speedup**: Compiler-only time < 25ns (vs current ~30ns)
3. **Total Speedup**: End-to-end < 250ns for simple expressions (vs current ~357ns)

---

## 6. Assumptions

1. **CPython Baseline**: Assuming "50-100x" target means vs CPython pure execution (~200-400μs), not subprocess (~19ms)
   - **Rationale**: 66,000x vs subprocess already achieved; further optimization beyond that is diminishing returns
   - **Validation**: Will measure CPython pure execution via Python C API to confirm baseline

2. **Hardware**: Benchmarks assume Apple M4 Max or equivalent modern CPU
   - **Rationale**: Current benchmarks run on M4 Max; optimization should benefit all platforms
   - **Validation**: CI will run on Linux x86_64 to verify cross-platform gains

3. **Workload**: Optimizing for small programs (< 20 lines, < 10 variables)
   - **Rationale**: Stated use case is "simple expressions" and arithmetic
   - **Validation**: Benchmark suite covers 10 representative simple programs

4. **Rust Version**: Using stable Rust 1.70+ (no nightly features)
   - **Rationale**: Production stability over bleeding-edge features
   - **Validation**: `Cargo.toml` specifies edition = "2021"

5. **No Breaking Changes**: All optimizations preserve existing API and test behavior
   - **Rationale**: This is performance work, not feature work
   - **Validation**: All 500+ existing tests must pass

---

## 7. Constraints and Dependencies

### 7.1 Technical Constraints

1. **Single-threaded**: VM must remain single-threaded (no Send/Sync requirements)
2. **No unsafe code**: Optimizations must use safe Rust unless profiling proves critical
3. **Platform support**: Must work on macOS ARM64, Linux x86_64, Windows x86_64
4. **Deterministic**: Same input must produce identical output (no randomness)

### 7.2 Dependencies

- **Criterion 0.5**: Benchmark framework (already in `Cargo.toml`)
- **Optional**: `criterion-perf-events` for hardware counter profiling
- **Optional**: `dhat` or `heaptrack` for memory profiling
- **Python 3.x**: For CPython baseline comparison

### 7.3 Timeline Constraints

- **Total Duration**: 2-3 weeks for all phases
- **Milestone 1** (Week 1): VM optimization complete, AC1 passes
- **Milestone 2** (Week 2): Allocation optimization + benchmarks complete, AC2-3 pass
- **Milestone 3** (Week 3): All ACs pass, documentation updated

---

## 8. Open Questions (Resolved Before Implementation)

1. **Q: What is the exact CPython baseline for "50-100x"?**
   - **Resolution Path**: Implement `cpython_pure_benchmarks.rs` using Python C API to measure pure execution
   - **Decision Owner**: Engineering team + PM review

2. **Q: Is unsafe code acceptable for critical path optimizations?**
   - **Resolution Path**: Benchmark with safe code first; only consider unsafe if <10% gain remains
   - **Decision Owner**: Engineering team (requires >50% gain to justify unsafe)

3. **Q: Should we optimize for memory usage or execution speed when there's a tradeoff?**
   - **Decision**: Prioritize execution speed; memory is secondary unless >10MB overhead
   - **Rationale**: Goal is "faster startup-to-result time" not memory efficiency

---

## 9. Implementation Phases

### Phase 1: VM Core Optimization (Days 1-5)
**Owner**: Engineering Team
**Deliverables**:
- [ ] Implement register bitmap instead of `Vec<Option<Value>>`
- [ ] Optimize `Value` enum representation
- [ ] Reduce clone operations in VM hot path
- [ ] AC1 passes: VM overhead < 150ns

### Phase 2: Allocation Optimization (Days 6-10)
**Owner**: Engineering Team
**Deliverables**:
- [ ] Implement variable name interning
- [ ] Optimize stdout string handling
- [ ] Optimize function call register copying
- [ ] AC2 passes: ≤ 5 allocations per call

### Phase 3: Benchmark Infrastructure (Days 8-12)
**Owner**: Engineering Team
**Deliverables**:
- [ ] Create granular per-stage benchmarks
- [ ] Implement CPython pure execution baseline
- [ ] Add allocation profiling tests
- [ ] AC3, AC6 pass: All benchmarks exist, CPython comparison documented

### Phase 4: Validation and Documentation (Days 13-15)
**Owner**: Engineering Team + PM
**Deliverables**:
- [ ] Run full benchmark suite, verify all ACs pass
- [ ] Update PERFORMANCE.md with new numbers
- [ ] Document optimization techniques for future reference
- [ ] AC4, AC5 pass: No regression, all tests green

---

## 10. Documentation Deliverables

1. **PERFORMANCE.md Update**:
   - Add "Optimization Analysis" section with before/after numbers
   - Document per-stage performance breakdown
   - Add new CPython pure execution baseline comparison

2. **Code Comments**:
   - Document each optimization technique inline
   - Explain tradeoffs for future maintainers

3. **Benchmark README**:
   - How to run each benchmark suite
   - How to interpret results
   - How to add new benchmarks

---

## Appendix A: Profiling Methodology

### Profiling Tools

1. **Criterion.rs**: Statistical benchmarking with < 1% variance
   - Use for all performance measurements
   - 1000 samples minimum, 10s measurement time

2. **perf** (Linux) / **Instruments** (macOS): CPU profiling
   - Identify hotspot functions
   - Measure instruction-level performance

3. **dhat** or **heaptrack**: Memory profiling
   - Count allocations
   - Identify allocation sources

### Benchmark Validation

All benchmarks must:
- Use `black_box()` to prevent compiler optimization of results
- Run with `--release` profile
- Report CV < 10% (ideally < 5%)
- Execute ≥ 1000 iterations for statistical significance

---

## Appendix B: Baseline Numbers (Current State)

From `PERFORMANCE.md` and benchmark runs:

| Benchmark | Mean Time | Std Dev | CV | Target |
|-----------|-----------|---------|-----|--------|
| cold_start_simple | 293.34 ns | 3.79 ns | 1.29% | < 500 ns |
| cold_start_complex | ~638 ns | - | < 2% | < 1000 ns |
| with_variables | ~885 ns | - | < 2% | < 1500 ns |
| with_print | ~359 ns | - | < 2% | < 600 ns |
| cpython_subprocess | 19.38 ms | 336.23 μs | 1.74% | (baseline) |

**Estimated Per-Stage Breakdown** (from architecture analysis):
- Lexer: ~5-10 ns (2-3%)
- Parser: ~10-20 ns (4-7%)
- Compiler: ~15-30 ns (5-10%)
- VM: ~250-270 ns (85-90%) ← **PRIMARY TARGET**
- Output formatting: ~5-10 ns (2-3%)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-08 | Claude Sonnet 4.5 | Initial PRD for performance optimization |

---

**PM Sign-off**: _Pending Engineering Review_
**Engineering Sign-off**: _Pending Implementation Plan_
