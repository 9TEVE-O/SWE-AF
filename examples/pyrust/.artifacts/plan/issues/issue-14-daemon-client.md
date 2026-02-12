# issue-14-daemon-client: Implement daemon client with fallback

## Description
Create daemon client that connects to the Unix socket daemon, sends code execution requests, and falls back to direct execution if the daemon is unavailable. Includes daemon management commands (stop, status).

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section 2.3 (Daemon Client) for:
- DaemonClient struct with execute_or_fallback(), execute_via_daemon(), stop_daemon(), is_daemon_running()
- DaemonClientError enum with 9 error variants (ConnectionFailed, SocketConfig, WriteFailed, ReadFailed, InvalidUtf8, InvalidStatus, ExecutionError, ResponseTooLarge, PidFileRead, InvalidPid, ShutdownFailed)
- Unix socket connection logic with 5-second read timeout and 1-second write timeout
- Binary protocol encoding/decoding (u32 length prefix + UTF-8 code bytes)
- 10MB max response size safety check
- SIGTERM-based daemon shutdown with verification

## Interface Contracts
- Implements:
  ```rust
  pub struct DaemonClient;
  impl DaemonClient {
      pub fn is_daemon_running() -> bool;
      pub fn execute_or_fallback(code: &str) -> Result<String, Box<dyn std::error::Error>>;
      pub fn stop_daemon() -> Result<(), DaemonClientError>;
  }
  ```
- Exports: DaemonClient with fallback execution, daemon management
- Consumes: daemon_protocol (ResponseStatus), daemon (SOCKET_PATH, PID_FILE_PATH), execute_python from lib
- Consumed by: daemon-cli-integration (main.rs CLI routing)

## Files
- **Create**: `src/daemon_client.rs`

## Dependencies
- issue-10-daemon-protocol (provides: ResponseStatus, binary protocol format)

## Provides
- Daemon client connection logic
- Fallback to direct execution
- Daemon management commands (stop, status)

## Acceptance Criteria
- [ ] Client detects running daemon via socket existence check (AC2.4)
- [ ] execute_or_fallback() tries daemon first, falls back to direct execution on error (AC2.4)
- [ ] stop_daemon() sends SIGTERM to PID, verifies socket/PID file cleanup (AC2.3)
- [ ] Connection timeout (5s read, 1s write) prevents hung requests
- [ ] Error propagation matches direct execution format (ExecutionError variant displays error string) (AC2.5)
- [ ] Response size limited to 10MB to prevent unbounded allocation

## Testing Strategy

### Test Files
- `tests/daemon_fallback_test.rs`: Integration test for daemon fallback behavior
- Unit tests in `src/daemon_client.rs`: Test is_daemon_running() with/without socket file

### Test Categories
- **Unit tests**: is_daemon_running() returns true when socket exists, false otherwise
- **Integration tests**:
  - Start daemon, call execute_or_fallback('2+3'), verify result='5'
  - Stop daemon, call execute_or_fallback('2+3'), verify fallback works
  - Test error propagation: division by zero returns identical error as direct execution
- **Edge cases**: Connection timeout, invalid PID file, response size limit exceeded

### Run Command
`cargo test --release daemon_client`
