# issue-20-cache-performance-benchmark: Create cache hit/miss performance benchmark

## Description
Implement comprehensive cache performance benchmarking measuring cache hit latency (warm cache), cache miss latency, and hit rate. Validates AC6.3 target of <50μs cached execution and confirms cache effectiveness with ≥95% hit rate on repeated code.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section 6.3 (Cache Performance Benchmark) for:
- Complete benchmark structure with cache_hit_latency and cache_miss_latency functions
- Criterion configuration: sample_size=1000, measurement_time=10s
- Test function `verify_cache_hit_rate()` for AC3.1 validation
- Statistical validation approach with Criterion JSON parsing

## Interface Contracts
- **Implements**: Cache performance benchmark using Criterion
- **Exports**:
  - `cache_hit_2_plus_3` benchmark (mean ≤50μs target)
  - `cache_miss` benchmark (within 5% of baseline)
  - `verify_cache_hit_rate` test (≥95% hit rate)
- **Consumes**:
  - `pyrust::execute_python(code: &str) -> Result<String, PyRustError>`
  - `pyrust::clear_cache()` — clears thread-local cache
  - `pyrust::cache_stats() -> CacheStats` — returns cache statistics with hit_rate field
- **Consumed by**: speedup-validation-scripts, performance-documentation

## Files
- **Create**: `benches/cache_performance.rs`
- **Modify**: `Cargo.toml` (add `[[bench]]` entry)

## Dependencies
- issue-15 (cache-integration) — provides execute_python, clear_cache, cache_stats

## Provides
- Cache performance benchmark suite
- Statistical validation of <50μs cache hit latency
- Cache hit rate measurement (≥95% validation)
- Cache miss baseline comparison

## Acceptance Criteria
- [ ] AC6.3: Cache hit benchmark mean ≤50μs verified in Criterion output
- [ ] Benchmark measures hit rate achieving ≥95% (via test function)
- [ ] Cache miss performance within 5% of baseline
- [ ] CV < 10% for statistical stability (Criterion default validation)

## Testing Strategy

### Test Files
- `benches/cache_performance.rs`: Benchmarks cache hit/miss latency and tests hit rate

### Test Categories
- **Benchmarks**:
  - `cache_hit_2_plus_3` — measures warm cache latency with pre-warmed "2 + 3"
  - `cache_miss` — measures cold cache latency with clear_cache() per iteration
- **Unit tests**:
  - `verify_cache_hit_rate` — runs 100 identical requests, asserts hit_rate ≥0.95

### Run Command
```bash
cargo bench --bench cache_performance
cargo test --bench cache_performance verify_cache_hit_rate
```
