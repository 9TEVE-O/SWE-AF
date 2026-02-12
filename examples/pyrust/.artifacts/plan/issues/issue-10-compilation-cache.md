# issue-10-compilation-cache: Implement LRU compilation cache

## Description
Create in-memory LRU cache with SipHash-based collision detection to achieve <50μs cached execution latency. Supports thread-local mode (library) and global mode (daemon) with <10MB memory footprint for 1000 entries.

## Architecture Reference
Read architecture.md Section 3.1 (Cache Implementation) for:
- `CompilationCache` struct with HashMap + LRU eviction logic
- `CacheEntry` struct with full source storage for collision detection
- `hash_code()` using DefaultHasher (SipHash) for cryptographic-quality hashing
- `get()`, `insert()`, `evict_lru()`, `stats()`, `clear()` method signatures
- Performance budget: hash ~20μs, lookup ~10μs, Arc clone ~5μs = ~35μs total

## Interface Contracts
- Implements:
  ```rust
  pub fn new(capacity: usize) -> Self
  pub fn from_env() -> Self  // reads PYRUST_CACHE_SIZE env var
  pub fn get(&mut self, code: &str) -> Option<Arc<Bytecode>>
  pub fn insert(&mut self, code: String, bytecode: Bytecode)
  pub fn stats(&self) -> CacheStats
  ```
- Exports: `CompilationCache`, `CacheStats` (hits, misses, size, capacity, hit_rate)
- Consumes: `crate::bytecode::Bytecode`
- Consumed by: issue-15-cache-integration (library/daemon integration)

## Files
- **Create**: `src/cache.rs`
- **Modify**: `Cargo.toml` (add `lazy_static = "1.4"` dependency)

## Dependencies
None (standalone module)

## Provides
- `CompilationCache` with O(1) lookup and O(n) LRU eviction
- SipHash-based collision detection via full source comparison
- Cache statistics tracking (hit rate, size, capacity)

## Acceptance Criteria
- [ ] Cache hit rate ≥95% for 100 identical requests (AC3.1)
- [ ] LRU eviction: 1001st entry evicts oldest (AC3.4)
- [ ] Memory usage ≤10MB for 1000 cached scripts (AC3.5)
- [ ] Cache invalidation: different code produces different results (AC3.6)
- [ ] Cache hit lookup completes in <50μs

## Testing Strategy

### Test Files
- `src/cache.rs`: Inline unit tests with `#[cfg(test)] mod tests`

### Test Categories
- **Unit tests**: `test_cache_hit_miss` (verify get/insert/stats), `test_lru_eviction` (verify 1001st entry evicts oldest), `test_collision_detection` (verify full source comparison prevents false positives), `test_capacity_limit` (verify cache never exceeds capacity)
- **Functional tests**: `test_env_variable` (verify PYRUST_CACHE_SIZE env var), `test_clear` (verify clear resets all state)
- **Edge cases**: Empty cache stats, single entry cache, zero capacity handling

### Run Command
`cargo test --lib cache::tests`
