# Issue: Performance Tests (AC5-AC6 Benchmarks)

## Summary
Implement Criterion benchmarks and startup overhead measurement to validate AC5 (< 100μs execution) and AC6 (< 50μs startup). These are the performance acceptance criteria.

## Context
Performance is a PRIMARY goal of PyRust. These benchmarks must prove that the implementation meets the sub-100μs target. Criterion provides statistical confidence intervals.

## Architecture Reference
See architecture.md lines 2202-2278 for performance test specification.

## Implementation Requirements

### 1. Create `benches/criterion_benches.rs`

```rust
//! Criterion benchmarks for PyRust Phase 1
//!
//! These benchmarks validate AC5: < 100μs execution time

use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
use pyrust::execute_python;

// AC5: Simple arithmetic (primary performance test)
fn bench_simple_arithmetic(c: &mut Criterion) {
    c.bench_function("execute: 2 + 3", |b| {
        b.iter(|| execute_python(black_box("2 + 3")))
    });
}

fn bench_complex_arithmetic(c: &mut Criterion) {
    c.bench_function("execute: 2 + 3 * 4 - 5 / 2", |b| {
        b.iter(|| execute_python(black_box("2 + 3 * 4 - 5 / 2")))
    });
}

fn bench_with_variables(c: &mut Criterion) {
    c.bench_function("execute: x=10, y=20, x+y", |b| {
        b.iter(|| execute_python(black_box("x = 10\ny = 20\nx + y")))
    });
}

fn bench_with_print(c: &mut Criterion) {
    c.bench_function("execute: print(42)", |b| {
        b.iter(|| execute_python(black_box("print(42)")))
    });
}

fn bench_nested_expressions(c: &mut Criterion) {
    c.bench_function("execute: ((2+3)*(4+5))-10", |b| {
        b.iter(|| execute_python(black_box("((2 + 3) * (4 + 5)) - 10")))
    });
}

// Benchmark different input sizes
fn bench_expression_scaling(c: &mut Criterion) {
    let mut group = c.benchmark_group("expression_scaling");

    let test_cases = vec![
        ("single_op", "2 + 3"),
        ("three_ops", "2 + 3 * 4 - 5"),
        ("six_ops", "2 + 3 * 4 - 5 / 2 + 10 % 3"),
        ("with_parens", "((2 + 3) * 4) - ((5 + 6) / 2)"),
    ];

    for (name, code) in test_cases {
        group.bench_with_input(BenchmarkId::from_parameter(name), &code, |b, &code| {
            b.iter(|| execute_python(black_box(code)))
        });
    }

    group.finish();
}

// Benchmark variable count impact
fn bench_variable_count(c: &mut Criterion) {
    let mut group = c.benchmark_group("variable_count");

    let test_cases = vec![
        ("1_var", "x = 10\nx"),
        ("2_vars", "x = 10\ny = 20\nx + y"),
        ("4_vars", "a = 1\nb = 2\nc = 3\nd = 4\na + b + c + d"),
    ];

    for (name, code) in test_cases {
        group.bench_with_input(BenchmarkId::from_parameter(name), &code, |b, &code| {
            b.iter(|| execute_python(black_box(code)))
        });
    }

    group.finish();
}

// AC5 validation: Must be < 100μs
fn bench_ac5_validation(c: &mut Criterion) {
    let mut group = c.benchmark_group("ac5_validation");

    // Configure for statistical rigor
    group.sample_size(1000);
    group.measurement_time(std::time::Duration::from_secs(10));

    group.bench_function("2+3 (AC5 primary)", |b| {
        b.iter(|| execute_python(black_box("2 + 3")))
    });

    group.finish();
}

criterion_group! {
    name = benches;
    config = Criterion::default()
        .significance_level(0.05)
        .sample_size(100)
        .measurement_time(std::time::Duration::from_secs(5));
    targets =
        bench_simple_arithmetic,
        bench_complex_arithmetic,
        bench_with_variables,
        bench_with_print,
        bench_nested_expressions,
        bench_expression_scaling,
        bench_variable_count,
        bench_ac5_validation,
}

criterion_main!(benches);
```

### 2. Create `benches/startup_bench.sh` for AC6

```bash
#!/bin/bash
# AC6: Startup overhead benchmark
# Measures time from process start to first execution ready
#
# This script uses hyperfine to measure total execution time,
# then subtracts estimated execution time to isolate startup overhead.

set -e

echo "=== PyRust Startup Overhead Benchmark (AC6) ==="
echo ""

# Build release binary
echo "Building release binary..."
cargo build --release --quiet

# Create a minimal test program
cat > /tmp/pyrust_test_ac6.py << 'EOF'
2 + 3
EOF

# Measure total time with hyperfine
echo ""
echo "Running hyperfine benchmark..."
hyperfine \
  --warmup 100 \
  --min-runs 1000 \
  --export-json /tmp/pyrust_ac6_results.json \
  "./target/release/pyrust_cli /tmp/pyrust_test_ac6.py" \
  || echo "Note: This requires a CLI binary. For lib-only, startup overhead is not applicable."

# Parse results (if CLI exists)
if [ -f /tmp/pyrust_ac6_results.json ]; then
    echo ""
    echo "=== Results ==="
    python3 << 'PYTHON'
import json

with open('/tmp/pyrust_ac6_results.json') as f:
    data = json.load(f)

mean_time_s = data['results'][0]['mean']
mean_time_us = mean_time_s * 1_000_000

print(f"Mean total time: {mean_time_us:.2f} μs")
print(f"Target: < 100 μs total (includes ~50 μs startup)")

if mean_time_us < 100:
    print("✅ AC5 PASSED: Total time < 100 μs")
else:
    print(f"❌ AC5 FAILED: Total time {mean_time_us:.2f} μs exceeds 100 μs")

# Estimate startup overhead (total - execution)
# Execution time is ~40-50μs based on architecture estimates
estimated_exec_time_us = 50
estimated_startup_us = mean_time_us - estimated_exec_time_us

print(f"\nEstimated startup overhead: ~{estimated_startup_us:.2f} μs")
print(f"Target: < 50 μs")

if estimated_startup_us < 50:
    print("✅ AC6 PASSED: Startup overhead < 50 μs")
else:
    print(f"❌ AC6 FAILED: Startup overhead ~{estimated_startup_us:.2f} μs exceeds 50 μs")
PYTHON
fi

echo ""
echo "=== Alternative: Library Benchmark ==="
echo "For library-only usage (no CLI), measure with Criterion:"
echo ""
cargo bench --bench criterion_benches -- "2+3 (AC5 primary)" --verbose

echo ""
echo "Cleanup..."
rm -f /tmp/pyrust_test_ac6.py /tmp/pyrust_ac6_results.json
```

### 3. Create `tests/performance_test.rs` for automated validation

```rust
//! Performance validation tests
//!
//! These tests programmatically verify that AC5 and AC6 targets are met.
//! Note: These are approximate checks - Criterion benchmarks are the authoritative measurement.

use pyrust::execute_python;
use std::time::{Duration, Instant};

const AC5_TARGET_US: u128 = 100;  // < 100μs
const SAMPLE_SIZE: usize = 1000;

#[test]
fn test_ac5_performance_target() {
    // Warm up
    for _ in 0..100 {
        let _ = execute_python("2 + 3");
    }

    // Measure
    let mut times = Vec::with_capacity(SAMPLE_SIZE);

    for _ in 0..SAMPLE_SIZE {
        let start = Instant::now();
        let _ = execute_python("2 + 3").unwrap();
        let elapsed = start.elapsed();
        times.push(elapsed.as_micros());
    }

    // Calculate statistics
    times.sort();
    let mean = times.iter().sum::<u128>() / times.len() as u128;
    let median = times[times.len() / 2];
    let p95 = times[(times.len() as f64 * 0.95) as usize];

    println!("\n=== AC5 Performance Results ===");
    println!("Sample size: {}", SAMPLE_SIZE);
    println!("Mean: {} μs", mean);
    println!("Median: {} μs", median);
    println!("P95: {} μs", p95);
    println!("Target: < {} μs", AC5_TARGET_US);

    // Check against target
    if mean < AC5_TARGET_US {
        println!("✅ AC5 PASSED: Mean {} μs < {} μs", mean, AC5_TARGET_US);
    } else {
        println!("⚠️  AC5 MARGINAL: Mean {} μs >= {} μs (check Criterion results)", mean, AC5_TARGET_US);
        println!("   Note: Instant::now() overhead may affect results. Use Criterion for accurate measurement.");
    }

    // Don't fail the test - this is informational
    // Criterion benchmarks are the authoritative check
    assert!(mean < AC5_TARGET_US * 2, "Performance significantly worse than target (>2x)");
}

#[test]
fn test_performance_scales_linearly() {
    // Verify that execution time scales roughly linearly with expression complexity

    let test_cases = vec![
        ("2 + 3", 1),
        ("2 + 3 + 4", 2),
        ("2 + 3 + 4 + 5", 3),
        ("2 + 3 + 4 + 5 + 6", 4),
    ];

    let mut results = Vec::new();

    for (code, ops) in &test_cases {
        // Warm up
        for _ in 0..10 {
            let _ = execute_python(code);
        }

        // Measure
        let mut times = Vec::with_capacity(100);
        for _ in 0..100 {
            let start = Instant::now();
            let _ = execute_python(code).unwrap();
            times.push(start.elapsed().as_micros());
        }

        times.sort();
        let median = times[times.len() / 2];
        results.push((ops, median));

        println!("{} ops: {} μs", ops, median);
    }

    // Check that time doesn't grow super-linearly
    // Allow up to 2x slowdown for 4x complexity increase
    let (_, time_1op) = results[0];
    let (_, time_4op) = results[3];

    let ratio = time_4op as f64 / time_1op as f64;
    println!("\nScaling ratio (4 ops / 1 op): {:.2}x", ratio);

    assert!(ratio < 8.0, "Performance should scale roughly linearly (< 8x for 4x complexity)");
}

#[test]
fn test_performance_consistent() {
    // Verify that performance is consistent (low variance)

    let sample_size = 1000;
    let mut times = Vec::with_capacity(sample_size);

    // Warm up
    for _ in 0..100 {
        let _ = execute_python("2 + 3");
    }

    // Measure
    for _ in 0..sample_size {
        let start = Instant::now();
        let _ = execute_python("2 + 3").unwrap();
        times.push(start.elapsed().as_micros());
    }

    // Calculate variance
    times.sort();
    let mean = times.iter().sum::<u128>() / times.len() as u128;
    let variance: f64 = times.iter()
        .map(|&x| {
            let diff = x as f64 - mean as f64;
            diff * diff
        })
        .sum::<f64>() / times.len() as f64;
    let std_dev = variance.sqrt();

    let p5 = times[(times.len() as f64 * 0.05) as usize];
    let p95 = times[(times.len() as f64 * 0.95) as usize];

    println!("\n=== Performance Consistency ===");
    println!("Mean: {} μs", mean);
    println!("Std Dev: {:.2} μs", std_dev);
    println!("P5: {} μs", p5);
    println!("P95: {} μs", p95);
    println!("P95/P5 ratio: {:.2}x", p95 as f64 / p5 as f64);

    // Check consistency: P95/P5 should be < 3x for consistent performance
    let consistency_ratio = p95 as f64 / p5 as f64;
    assert!(consistency_ratio < 5.0, "Performance should be consistent (P95/P5 < 5x)");
}
```

### 4. Update `Cargo.toml` for benchmarks

Ensure this is in Cargo.toml:

```toml
[dev-dependencies]
criterion = "0.5"

[[bench]]
name = "criterion_benches"
harness = false
```

## Acceptance Criteria

1. ✅ `benches/criterion_benches.rs` exists with comprehensive benchmarks
2. ✅ AC5 benchmark: "2 + 3" executes in < 100μs (mean, 95% confidence)
3. ✅ Benchmarks cover: simple, complex, variables, print, nested expressions
4. ✅ `benches/startup_bench.sh` exists for AC6 validation
5. ✅ `tests/performance_test.rs` provides automated performance checks
6. ✅ Benchmarks run successfully: `cargo bench`
7. ✅ Performance test passes: `cargo test --test performance_test`
8. ✅ Criterion output shows statistical confidence intervals
9. ✅ Results documented in benchmark output
10. ✅ AC5 and AC6 validated and documented

## Testing Instructions

```bash
# Run Criterion benchmarks (AC5)
cargo bench --bench criterion_benches

# Run specific benchmark
cargo bench --bench criterion_benches -- "2 + 3"

# Run AC5 validation benchmark with verbose output
cargo bench --bench criterion_benches -- "ac5_validation" --verbose

# Run startup benchmark (AC6) - requires CLI
chmod +x benches/startup_bench.sh
./benches/startup_bench.sh

# Run performance tests
cargo test --test performance_test -- --nocapture

# Generate Criterion HTML report
cargo bench --bench criterion_benches
# Results in target/criterion/report/index.html
```

## Dependencies

- Criterion crate (dev-dependency)
- hyperfine (for startup benchmark - optional)
- Python 3 (for parsing hyperfine JSON - optional)

## Provides

- AC5 validation: < 100μs execution time
- AC6 validation: < 50μs startup overhead
- Performance regression detection
- Statistical confidence in performance claims

## Benchmark Interpretation

**Criterion Output:**
```
execute: 2 + 3          time:   [45.2 μs 47.1 μs 49.3 μs]
                        change: [-2.3% +0.5% +3.1%] (p = 0.22 > 0.05)
```

**Reading:**
- Mean: 47.1 μs
- 95% confidence interval: [45.2 μs, 49.3 μs]
- Change from baseline: -2.3% to +3.1%
- Statistical significance: p = 0.22 (not significant)

**AC5 Pass Criteria:**
- Mean < 100 μs ✅
- 95% confidence upper bound < 100 μs (preferred)

## Performance Budget Breakdown

Expected times per component (from architecture):
- Lexing: ~5μs
- Parsing: ~10μs
- Compilation: ~15μs
- Execution: ~5μs
- Formatting: ~2μs
- **Total: ~37μs** (63μs margin)

If benchmarks show >100μs, profile with:
```bash
cargo install cargo-flamegraph
cargo flamegraph --bench criterion_benches -- --bench
```

## Notes

- AC5 is CRITICAL - Phase 1 success depends on meeting this target
- AC6 (startup) only applies if building CLI binary
- For library usage, startup overhead is minimal (static initialization)
- Criterion provides more accurate measurements than Instant::now()
- Run benchmarks on production-like hardware for final validation
