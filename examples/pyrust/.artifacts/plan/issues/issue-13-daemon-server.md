# issue-13-daemon-server: Implement Unix socket daemon server

## Description
Create `src/daemon.rs` implementing the DaemonServer with Unix socket event loop, signal handling (SIGTERM/SIGINT), PID file management, and request processing via daemon_protocol. Enables long-running daemon process accepting sequential connections to amortize process spawn overhead and achieve <190μs per-request latency.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section "Phase 2: Daemon Mode" → "Component 2.2: Daemon Server" for:
- DaemonServer struct with UnixListener and shutdown flag
- Signal handler registration using ctrlc crate
- Non-blocking event loop with 10ms polling interval
- Sequential connection handling with 5s read timeout
- PID file write/remove methods
- DaemonError enum with display implementation
- Socket permission enforcement (0o600)
- Request size limit (1MB) and response encoding

## Interface Contracts
```rust
pub struct DaemonServer { listener: UnixListener, shutdown: Arc<AtomicBool> }
impl DaemonServer {
    pub fn new() -> Result<Self, DaemonError>
    pub fn register_signal_handlers(&self) -> Result<(), DaemonError>
    pub fn run(&mut self) -> Result<(), DaemonError>
    pub fn shutdown(&self) -> Result<(), DaemonError>
    pub fn write_pid_file() -> Result<(), DaemonError>
    pub fn remove_pid_file() -> Result<(), DaemonError>
}
```

- **Implements**: Unix socket daemon server with signal handling
- **Exports**: DaemonServer, DaemonError, SOCKET_PATH ("/tmp/pyrust.sock"), PID_FILE_PATH ("/tmp/pyrust.pid")
- **Consumes**: daemon_protocol::DaemonResponse, execute_python() from lib.rs
- **Consumed by**: issue-14-daemon-client (client connection), issue-15-daemon-cli-integration (main.rs startup)

## Files
- **Create**: `src/daemon.rs`
- **Modify**: `Cargo.toml` (add `ctrlc = "3.4"` to [dependencies])

## Dependencies
- issue-12-daemon-protocol (provides: DaemonResponse, ResponseStatus, encode/decode methods)

## Provides
- DaemonServer with new(), run(), shutdown() methods
- Signal handling infrastructure for graceful shutdown
- PID file management (write_pid_file, remove_pid_file)
- Socket permission enforcement (0o600 owner-only)
- Request timeout (5s) and size limit (1MB)
- Constants: SOCKET_PATH, PID_FILE_PATH

## Acceptance Criteria
- [ ] AC2.1: Server creates /tmp/pyrust.sock with 0600 permissions and /tmp/pyrust.pid
- [ ] Server accepts connections and handles requests sequentially via handle_connection()
- [ ] SIGTERM/SIGINT trigger graceful shutdown via ctrlc handler setting shutdown flag
- [ ] Cleanup removes socket and PID file on shutdown
- [ ] Request timeout prevents hung connections (5s read timeout)
- [ ] Request size limit enforced (1MB max)

## Testing Strategy

### Test Files
- Integration testing delegated to issue-16-daemon-concurrency-testing
- Unit tests in `src/daemon.rs` using #[cfg(test)] module

### Test Categories
- **Unit tests**: PID file write/remove, socket cleanup logic, error enum Display trait
- **Functional tests**: (in issue-16) Start daemon, verify socket exists, send request via nc -U, stop daemon, verify cleanup
- **Edge cases**: Request size limit enforcement, timeout on slow reads, signal handling cleanup

### Run Command
`cargo test --release daemon::tests`
