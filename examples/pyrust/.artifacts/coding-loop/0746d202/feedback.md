# Feedback: Iteration 0746d202

## Decision: FIX

**Status**: Tests pass ✅ | Code review blocking issues ❌

## Summary

Good progress! You successfully fixed the previous iteration's race condition and error handling issues. All 5 acceptance criteria pass with comprehensive test coverage. However, 2 **BLOCKING** resource management bugs must be fixed before approval.

## BLOCKING Issues (Must Fix)

### 1. Memory Leak - Pipe FDs Not Closed on Fork Failure
**Location**: `src/main.rs`, lines 123-125 (fork error path)

**Problem**: When `fork()` fails, the pipe file descriptors remain open, leaking resources.

**Fix**: Add cleanup before returning error:
```rust
Err(e) => {
    // Close pipe FDs to prevent leak
    let _ = nix::unistd::close(read_fd);
    let _ = nix::unistd::close(write_fd);
    return Err(format!("Failed to fork daemon process: {}", e));
}
```

### 2. Unsafe /dev/null Handling - Daemon Runs with Invalid Stdio
**Location**: `src/main.rs`, lines 194-206 (stdio redirection in daemon)

**Problem**: If `/dev/null` cannot be opened or `dup2()` fails, the daemon continues running with broken stdio. This can cause crashes or undefined behavior when the daemon tries to write output.

**Fix**: Make stdio redirection mandatory - exit daemon if it fails:
```rust
let dev_null = std::fs::OpenOptions::new()
    .read(true)
    .write(true)
    .open("/dev/null")
    .expect("Failed to open /dev/null - cannot safely daemonize");

let null_fd = dev_null.as_raw_fd();
nix::unistd::dup2(null_fd, 0).expect("Failed to redirect stdin");
nix::unistd::dup2(null_fd, 1).expect("Failed to redirect stdout");
nix::unistd::dup2(null_fd, 2).expect("Failed to redirect stderr");
```

**Rationale**: These operations should never fail on a healthy system. If they do, the daemon cannot run safely. Using `expect()` here is appropriate because continuing without valid stdio is worse than failing fast.

## Non-Blocking Issues (Tracked as Debt)

The following issues are identified but don't block approval:
- TOCTOU race in startup check (can cause confusing error messages)
- Signal safety violation using `eprintln!` after fork
- Missing CLI integration test for AC2.5

These are acceptable technical debt and will be tracked separately.

## What to Do

1. Apply both fixes above to `src/main.rs`
2. Run tests to ensure no regressions
3. The fixes are localized - no architectural changes needed

## Why This Matters

- **Issue #1**: Resource leaks accumulate over time and can exhaust system limits
- **Issue #2**: A daemon with broken stdio can crash unpredictably or corrupt output

Both are critical for production reliability.
