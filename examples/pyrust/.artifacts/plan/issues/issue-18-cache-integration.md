# issue-18-cache-integration: Integrate cache into library and daemon

## Description
Wire the CompilationCache into lib.rs and daemon.rs to enable sub-50μs cached execution in daemon mode and zero-overhead caching in library mode. Replaces execute_python() with cached variants using thread-local storage for library API and global mutex for daemon mode.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section 3.2 (Cache Integration) for:
- Thread-local cache initialization (THREAD_CACHE with RefCell)
- Global cache initialization (GLOBAL_CACHE with Mutex)
- execute_python_with_cache() implementation
- execute_python_daemon() for daemon mode
- Cache management functions (clear_cache, cache_stats)

## Interface Contracts
- Implements:
  ```rust
  pub fn execute_python(code: &str) -> Result<String, PyRustError>;      // Thread-local cached
  pub fn execute_python_daemon(code: &str) -> Result<String, PyRustError>; // Global cached
  pub fn clear_cache();
  pub fn clear_global_cache();
  pub fn cache_stats() -> CacheStats;
  ```
- Exports: Cached execution functions for library and daemon modes
- Consumes: CompilationCache from issue-15-compilation-cache
- Consumed by: issue-17-daemon-cli-integration, issue-20-cache-performance-benchmark

## Files
- **Modify**: `src/lib.rs` (add imports, thread_local!, lazy_static!, replace execute_python, add cache management)
- **Modify**: `src/daemon.rs` (change execute call to use execute_python_daemon)
- **Modify**: `src/main.rs` (add --clear-cache command handler)

## Dependencies
- issue-15-compilation-cache (provides: CompilationCache type)
- issue-13-daemon-cli-integration (provides: daemon.rs infrastructure)

## Provides
- Cached execute_python() variants (thread-local and global)
- Thread-local cache for library API (zero locking overhead)
- Global cache for daemon mode (shared across requests)
- Cache management functions (clear, stats)

## Acceptance Criteria
- [ ] AC3.2: Cached execution ≤50μs mean in daemon mode after warm-up
- [ ] AC3.3: Cache miss performance within 5% of no-cache baseline
- [ ] Thread-local THREAD_CACHE used by library API
- [ ] Global GLOBAL_CACHE used by daemon mode
- [ ] clear_cache() and clear_global_cache() functions work correctly
- [ ] daemon.rs calls execute_python_daemon() instead of execute_python()

## Testing Strategy

### Test Files
- `benches/cache_performance.rs`: Measures cache hit/miss latency and validates performance

### Test Categories
- **Unit tests**: Cache statistics tracking via cache_stats()
- **Functional tests**:
  - Cache hit: 100 identical requests achieve ≥95% hit rate
  - Cache miss: Performance within 5% of no-cache baseline
  - Daemon cache: execute_python_daemon() shares cache across requests
- **Performance tests**:
  - Warm cache with 100 identical requests
  - Measure next 100 requests for <50μs mean latency
  - Compare cache miss vs no-cache via criterion

### Run Command
`cargo bench cache_performance`
