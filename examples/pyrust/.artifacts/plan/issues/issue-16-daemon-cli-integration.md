# issue-16-daemon-cli-integration: Integrate daemon into main.rs CLI

## Description
Modify main.rs to add daemon management commands (--daemon, --stop-daemon, --daemon-status), route execution through daemon client with fallback to direct execution, and implement fork-based daemon startup. This completes the CLI integration layer for Phase 2 daemon mode.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section "Phase 2: Daemon Mode → Component 2.4: CLI Integration" for:
- Complete main() function replacement with daemon command handling
- daemon_mode() function with fork-based background process startup
- run_daemon_server() function connecting to DaemonServer::new()
- Integration with daemon_client::DaemonClient::execute_or_fallback()

## Interface Contracts
- **Implements**:
  ```rust
  fn main() // Modified to handle --daemon, --stop-daemon, --daemon-status
  fn daemon_mode() // Fork background process, parent exits
  fn run_daemon_server() // Child process calls DaemonServer::new() and run()
  ```
- **Exports**: CLI commands for daemon management
- **Consumes**: daemon_client::DaemonClient, daemon::DaemonServer (from issue-11, issue-12)
- **Consumed by**: End users via command-line interface

## Files
- **Modify**: `src/main.rs` (add daemon module imports, replace main(), add daemon_mode() and run_daemon_server())

## Dependencies
- issue-11-daemon-server (provides: DaemonServer::new(), run(), write_pid_file(), remove_pid_file())
- issue-12-daemon-client (provides: DaemonClient::execute_or_fallback(), stop_daemon(), daemon_status(), is_daemon_running())

## Provides
- CLI integration for daemon mode
- Daemon management commands (--daemon, --stop-daemon, --daemon-status)
- Automatic daemon routing with fallback to direct execution
- Fork-based background daemon startup

## Acceptance Criteria
- [ ] AC2.1: `pyrust --daemon` forks background process and exits parent
- [ ] AC2.2: `pyrust -c '2+3'` with daemon running returns correct output
- [ ] AC2.3: `pyrust --stop-daemon` shuts down daemon cleanly
- [ ] AC2.4: Fallback works when daemon not running
- [ ] AC2.5: Error messages identical for daemon vs direct execution

## Testing Strategy

### Test Files
- `tests/test_daemon_lifecycle.sh`: Daemon startup, execution, and shutdown workflow
- `tests/test_daemon_fallback.sh`: Execution without daemon verifies fallback
- `tests/test_error_propagation.sh`: Compare error output between daemon and direct modes

### Test Categories
- **Integration tests**: Full daemon lifecycle (start → execute → stop)
- **Fallback tests**: Verify direct execution when daemon not running
- **Error equivalence**: Division by zero, undefined variables, syntax errors produce identical output

### Run Command
`./tests/test_daemon_lifecycle.sh && ./tests/test_daemon_fallback.sh && ./tests/test_error_propagation.sh`
