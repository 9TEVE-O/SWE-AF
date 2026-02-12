# Feedback - Iteration 3d3bd3e8

## Decision: FIX

## Summary
Cache implementation is excellent and all unit tests pass, but the cache is **never used** in the execution pipeline. The code is non-functional because there's no integration with `execute_python()`.

## Critical Issues (MUST FIX)

### 1. Cache Not Integrated into Execution Pipeline
**Problem**: The `CompilationCache` exists in `src/cache.rs` but is never instantiated or used by `execute_python()` in `src/lib.rs`.

**Fix**:
1. Add a global cache instance in `src/lib.rs`:
   ```rust
   use once_cell::sync::Lazy;
   use std::sync::Mutex;

   static COMPILATION_CACHE: Lazy<Mutex<CompilationCache>> = Lazy::new(|| {
       Mutex::new(CompilationCache::new(1000))
   });
   ```
2. Modify `execute_python()` to check cache before compilation:
   ```rust
   // After getting source_code string, before lexer:
   let cache_key = CompilationCache::hash_source(&source_code);
   if let Ok(cache) = COMPILATION_CACHE.lock() {
       if let Some(cached_bytecode) = cache.get(cache_key) {
           return execute_cached_bytecode(cached_bytecode, locals);
       }
   }

   // ... existing lexer → parser → compiler flow ...

   // After compilation succeeds, insert into cache:
   if let Ok(mut cache) = COMPILATION_CACHE.lock() {
       cache.insert(cache_key, bytecode.clone());
   }
   ```

3. Add `execute_cached_bytecode()` helper function that runs VM with cached bytecode

**Files to modify**:
- `src/lib.rs` - add cache integration to `execute_python()`
- `Cargo.toml` - add `once_cell = "1.19"` dependency

### 2. LRU Order Vector Memory Leak (CRITICAL for long-running processes)
**Problem**: In `src/cache.rs`, the `lru_order` vector grows unbounded. After 10,000 inserts with capacity 1000, it contains 10,000 entries instead of 1000.

**Fix** in `src/cache.rs`, line ~60 in `insert()`:
```rust
// Replace:
self.lru_order.push(key);

// With:
self.lru_order.retain(|&k| k != key); // Remove old position if exists
self.lru_order.push(key);
if self.lru_order.len() > self.capacity {
    self.lru_order.remove(0); // Remove oldest entry
}
```

## Non-Blocking Debt (defer to future issues)
- Missing integration tests with real lexer→parser→compiler pipeline (unit tests only use mock bytecode)
- Zero capacity behavior inconsistency between `insert()` and `get()`
- No cache statistics logging for daemon mode
- CacheStats missing total inserts/evictions metrics

## Validation Checklist
After fixing:
1. Run `cargo test` - all tests must pass
2. Run benchmark: `cargo bench --bench cache_performance` - verify cache hit latency <50μs
3. Manually test: run the same Python code twice and verify second execution uses cache (add debug logging if needed)
4. Check memory: run 10,000 inserts and verify `lru_order.len() == capacity` (not 10,000)
