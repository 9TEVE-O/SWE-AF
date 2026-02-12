# issue-09-daemon-protocol: Implement binary protocol for daemon IPC

## Description
Create daemon_protocol.rs with DaemonRequest/DaemonResponse structs using length-prefixed binary encoding. Supports zero-copy IPC with encode/decode methods and error handling for daemon communication.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section "Phase 2: Daemon Mode" → "Component 2.1: Binary Protocol Definition" for:
- Complete DaemonRequest/DaemonResponse struct definitions
- Binary wire format specifications (length-prefixed encoding)
- ProtocolError enum with UTF-8 validation handling
- Performance budget (encode <5μs, decode <10μs)

## Interface Contracts
- Implements:
  - `DaemonRequest::encode(&self) -> Vec<u8>` (format: [u32 length][UTF-8 code])
  - `DaemonRequest::decode(buf: &[u8]) -> Result<(Self, usize), ProtocolError>`
  - `DaemonResponse::encode(&self) -> Vec<u8>` (format: [u8 status][u32 length][UTF-8 output])
  - `DaemonResponse::decode(buf: &[u8]) -> Result<(Self, usize), ProtocolError>`
- Exports: DaemonRequest, DaemonResponse, ResponseStatus enum, ProtocolError
- Consumes: Nothing (standalone protocol module)
- Consumed by: issue-10-daemon-server, issue-11-daemon-client

## Files
- **Create**: `src/daemon_protocol.rs`

## Dependencies
None (uses std only)

## Provides
- Binary protocol for daemon communication
- DaemonRequest and DaemonResponse types
- Protocol encode/decode methods with error handling

## Acceptance Criteria
- [ ] Protocol encodes request as [u32 length][UTF-8 code]
- [ ] Protocol encodes response as [u8 status][u32 length][UTF-8 output]
- [ ] Decode validates UTF-8 and returns ProtocolError on invalid data
- [ ] Unit tests verify round-trip encode/decode for various payloads

## Testing Strategy

### Test Files
- `src/daemon_protocol.rs`: Inline unit tests with #[cfg(test)] module

### Test Categories
- **Unit tests**: Round-trip encode/decode for all protocol types
- **Edge cases**: Empty code (""), large payload (1MB string), invalid UTF-8 bytes
- **Performance**: Inline benchmarks verify encode <5μs, decode <10μs

### Test Cases
1. `test_request_encode_decode_empty` - Round-trip with empty string
2. `test_request_encode_decode_simple` - Round-trip with "2+3"
3. `test_request_encode_decode_large` - Round-trip with 1MB payload
4. `test_request_decode_invalid_utf8` - Verify ProtocolError on invalid bytes
5. `test_response_encode_decode_success` - Round-trip with ResponseStatus::Success
6. `test_response_encode_decode_error` - Round-trip with ResponseStatus::Error
7. `test_response_decode_invalid_status` - Verify ProtocolError on invalid status byte

### Run Command
`cargo test --release daemon_protocol`
