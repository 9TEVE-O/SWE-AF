# Code Review Issues - documentation-consolidation

## BLOCKING Issues

### 1. Test file references old PERFORMANCE.md path (BLOCKING)

**Severity:** BLOCKING
**File:** `tests/test_performance_documentation.rs`
**Lines:** Multiple (35+ occurrences throughout the file)

**Issue:**
The test file `tests/test_performance_documentation.rs` contains 35+ references to `PERFORMANCE.md` (the old root path) instead of `docs/performance.md` (the new path after consolidation). This causes all tests in this file to fail because the file no longer exists at the old location.

**Evidence:**
```rust
// Line 18
let path = Path::new("PERFORMANCE.md");

// Line 37
let content = fs::read_to_string("PERFORMANCE.md")
    .expect("PERFORMANCE.md not found - run test_performance_md_exists first");

// And 33+ more similar references throughout the file
```

**Impact:**
- All 20+ tests in this file will fail
- CI/CD pipeline will fail
- Acceptance criteria validation is broken
- The purpose of the tests (validating PERFORMANCE.md) cannot be fulfilled

**Required Fix:**
Update all references in `tests/test_performance_documentation.rs` from `PERFORMANCE.md` to `docs/performance.md`.

**Why This is Blocking:**
This breaks fundamental functionality (tests fail) and prevents validation of acceptance criteria. Tests are a critical part of the codebase and must pass.

---

## Summary

The coder successfully:
- ✅ Fixed 8 broken internal markdown links in README.md and docs/performance.md
- ✅ Updated README.md to reference `docs/implementation-notes.md` and `docs/performance.md`
- ✅ Updated docs/performance.md to fix references in shell commands and acceptance criteria table
- ✅ All 9 acceptance criteria for documentation structure pass

However, the coder **failed to update the test file** that validates the PERFORMANCE.md documentation. This test file still references the old root path and will cause all tests to fail.

**Status:** BLOCKING - Tests will fail due to incorrect file paths.
