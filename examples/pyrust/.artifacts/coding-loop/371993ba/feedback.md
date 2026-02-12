# Feedback - Iteration 371993ba

## Decision: FIX Required

All tests pass, but 2 BLOCKING issues prevent approval. These affect production reliability and debuggability.

---

## BLOCKING Issue #1: Race Condition in Daemon Startup

**Location:** `src/main.rs:119-120` (parent exit after fork)

**Problem:** Parent exits immediately without waiting for daemon to complete initialization. Users running `pyrust --daemon && pyrust -c '2+3'` may experience intermittent failures.

**Fix:**
Add synchronization before parent exits. Use a pipe to signal when daemon is ready:

1. In `start_daemon()` after `fork()`, create a pipe before forking:
   ```rust
   let mut pipe_fds = [0i32; 2];
   unsafe { libc::pipe(pipe_fds.as_mut_ptr()) };
   let read_fd = pipe_fds[0];
   let write_fd = pipe_fds[1];
   ```

2. Child daemon: After successfully creating socket and PID file, write a single byte to `write_fd`, then close it.

3. Parent process (before `process::exit(0)`): Block on reading from `read_fd` with a timeout (e.g., 5 seconds). If read succeeds, daemon is ready. If timeout, report error.

This ensures `--daemon` command only returns after daemon is fully operational.

---

## BLOCKING Issue #2: Lost Error Messages After File Descriptor Closure

**Location:** `src/main.rs:134-168` (daemon detachment)

**Problem:** Daemon closes stderr (line 137), then tries to write errors to stderr (lines 160, 166). All daemon errors are silently lost. If `/dev/null` open fails, daemon continues in invalid state.

**Fix:**
Implement proper daemon logging BEFORE closing file descriptors:

1. **Add error checking for open("/dev/null")**:
   ```rust
   let fd = unsafe { libc::open(b"/dev/null\0".as_ptr() as *const i8, libc::O_RDWR) };
   if fd < 0 {
       eprintln!("FATAL: Cannot open /dev/null");
       process::exit(1);
   }
   ```

2. **Create log file for daemon errors** before redirecting stderr:
   ```rust
   // After setsid, BEFORE closing fds
   let log_path = "/tmp/pyrust-daemon.log";
   let log_file = OpenOptions::new()
       .create(true)
       .append(true)
       .open(log_path);
   ```

3. **Replace stderr writes with log writes**:
   - Lines 160, 166: Instead of `writeln!(std::io::stderr(), ...)`, write to the log file
   - Add timestamps to log entries
   - Log successful startup message with PID

4. **Add error handling for dup2**:
   ```rust
   for i in 0..3 {
       if unsafe { libc::dup2(fd, i) } < 0 {
           // Log to file before exiting
           process::exit(1);
       }
   }
   ```

---

## Testing Your Fixes

After implementing:
1. Remove the `sleep 0.3` workaround from `tests/test_daemon_integration.sh` (lines with sleep after `--daemon`)
2. Run `pyrust --daemon && pyrust -c '2+3'` immediately - should work without races
3. Test daemon error logging: break socket creation and verify errors appear in `/tmp/pyrust-daemon.log`

---

## Non-Blocking Items (Tracked as Debt)

The following are acceptable for now but tracked for future improvement:
- Test coverage gap (bash tests not in `cargo test`)
- Incomplete error handling on other unsafe calls
- Magic numbers in test sleep durations
- Code organization (daemon functions in main.rs)

---

## Summary

Fix the two blocking issues:
1. Add pipe-based synchronization to eliminate startup race condition
2. Implement log file for daemon errors before closing stderr

Both fixes are in `src/main.rs` in the `start_daemon()` function. After these changes, re-run all tests to verify the workarounds are no longer needed.
