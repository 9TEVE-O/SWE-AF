# Code Review Issues - Daemon CLI Integration

## BLOCKING Issues

### 1. Race Condition in Daemon Startup
**Severity:** BLOCKING
**Location:** `src/main.rs:119-120`

**Issue:**
The parent process exits immediately after fork without waiting for the child daemon to complete initialization (socket creation, PID file writing). This creates a race condition where:
- The `--daemon` command returns before the daemon is ready
- Subsequent commands may fail if they try to connect before the socket exists
- Tests work around this with arbitrary sleep delays (0.3s), which is unreliable

**Current Code:**
```rust
} else if pid > 0 {
    // Parent process - exit successfully
    println!("Daemon started with PID {}", pid);
    process::exit(0);
}
```

**Impact:**
Users running `pyrust --daemon && pyrust -c '2+3'` may experience intermittent failures. This violates AC2.1's implicit requirement that the daemon be usable immediately after the command returns.

**Recommendation:**
Implement proper synchronization using a signal or secondary pipe to confirm daemon initialization before parent exits.

---

### 2. Error Handling After File Descriptor Closure
**Severity:** BLOCKING
**Location:** `src/main.rs:134-168`

**Issue:**
The daemon startup closes stderr (line 137) and redirects to /dev/null (lines 141-152), but then attempts to write error messages to stderr (lines 160, 166). Additionally, if `open("/dev/null")` fails (fd < 0), the code continues without proper file descriptors, leading to potential crashes.

**Current Code:**
```rust
unsafe {
    libc::close(2); // stderr
}
// ... redirect to /dev/null
match DaemonServer::new() {
    Ok(daemon) => {
        if let Err(e) = daemon.run() {
            // Error will be lost since stderr is redirected, but we try anyway
            let _ = writeln!(std::io::stderr(), "Daemon error: {}", e);
```

**Impact:**
- Daemon startup failures are silent and impossible to debug
- If /dev/null redirection fails, the daemon continues in an invalid state
- Violates AC2.3's implicit requirement for observable errors during daemon lifecycle

**Recommendation:**
1. Write startup errors to a log file before closing file descriptors
2. Add proper error handling for open() failures
3. Consider using syslog or a dedicated log file for daemon errors

---

## SHOULD_FIX Issues

### 3. Test Coverage Gap
**Severity:** SHOULD_FIX
**Location:** `tests/*.sh`

**Issue:**
All tests are written as bash scripts that won't be executed by `cargo test`. While comprehensive for manual testing, they:
- Don't integrate with Rust's standard testing infrastructure
- Won't run in CI/CD pipelines that use `cargo test`
- Don't provide coverage metrics
- Require manual execution with `bash tests/test_*.sh`

**Recommendation:**
Convert bash tests to Rust integration tests in `tests/` directory or create a test harness that executes the shell scripts via `std::process::Command`.

---

### 4. Unsafe Code Without Comprehensive Error Handling
**Severity:** SHOULD_FIX
**Location:** `src/main.rs:111-153`

**Issue:**
Multiple unsafe system calls have incomplete error handling:
- `fork()`: Only checks `pid < 0`, doesn't handle EAGAIN or ENOMEM specifically
- `setsid()`: Exits on failure but error message goes to closed stderr
- `open()`: Checks `fd >= 0` but doesn't exit/log on failure
- `dup2()`: No error checking at all

**Recommendation:**
Add comprehensive error checking for all unsafe calls and ensure errors are logged before file descriptors are closed.

---

### 5. Lost Error Messages After Daemon Detachment
**Severity:** SHOULD_FIX
**Location:** `src/main.rs:159-168`

**Issue:**
Error messages written to stderr after daemon detachment (lines 160, 166) are redirected to /dev/null, making debugging impossible. This makes it nearly impossible to diagnose daemon startup failures in production.

**Recommendation:**
Implement proper daemon logging:
- Write to a log file (e.g., `/tmp/pyrust-daemon.log`)
- Use syslog for production deployments
- Provide `--daemon-log <path>` flag for custom log location

---

## SUGGESTIONS

### 6. Magic Numbers in Test Scripts
**Severity:** SUGGESTION
**Location:** `tests/*.sh` (various sleep commands)

**Issue:**
Hardcoded sleep durations (0.1s, 0.2s, 0.3s) may be insufficient on slow systems or under heavy load, causing flaky tests.

**Recommendation:**
Implement proper polling with timeout instead of arbitrary sleeps:
```bash
wait_for_socket() {
    local timeout=5
    local elapsed=0
    while [ ! -S "$SOCKET_PATH" ] && [ $elapsed -lt $timeout ]; do
        sleep 0.1
        elapsed=$((elapsed + 1))
    done
}
```

---

### 7. Code Organization
**Severity:** SUGGESTION
**Location:** `src/main.rs:100-209`

**Issue:**
Daemon management functions (`start_daemon`, `stop_daemon`, `show_daemon_status`) are mixed with CLI parsing logic in main.rs, reducing modularity.

**Recommendation:**
Move daemon management functions to a separate `daemon_manager` module for better organization and testability.

---

## Acceptance Criteria Review

| AC | Description | Status | Notes |
|----|-------------|--------|-------|
| AC2.1 | pyrust --daemon forks background process | ⚠️ PARTIAL | Works but has race condition (Issue #1) |
| AC2.2 | pyrust -c '2+3' with daemon returns correct output | ✅ PASS | Tests verify correct output |
| AC2.3 | pyrust --stop-daemon shuts down cleanly | ✅ PASS | Cleanup verified in tests |
| AC2.4 | Fallback works when daemon not running | ✅ PASS | Comprehensive fallback testing |
| AC2.5 | Error messages identical for daemon vs direct | ✅ PASS | Test verifies message identity |

---

## Summary

The implementation successfully implements the core daemon CLI functionality and passes all integration tests. However, there are **2 BLOCKING issues** that must be addressed:

1. **Race condition in daemon startup** - The parent exits before the daemon is ready, requiring arbitrary sleeps in tests
2. **Error handling after file descriptor closure** - Daemon errors are silently lost, making debugging impossible

These issues don't prevent the feature from working in the test environment but create reliability and debuggability problems in production use. The SHOULD_FIX issues relate to test infrastructure and error handling improvements that would enhance production readiness.

**Recommendation:** Fix blocking issues #1 and #2 before merging to ensure production reliability.
