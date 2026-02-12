# Code Review Issues - daemon-protocol

## BLOCKING Issues

### 1. Incorrect decode() return type signature
**Severity**: BLOCKING
**Location**: `src/daemon_protocol.rs:107, 201`

**Issue**: The decode methods return `Result<Self, ProtocolError>` but the interface specification requires `Result<(Self, usize), ProtocolError>`. The `usize` indicates how many bytes were consumed from the buffer.

**Current Implementation**:
```rust
pub fn decode(bytes: &[u8]) -> Result<Self, ProtocolError>
```

**Required Interface** (from issue-09-daemon-protocol.md, lines 16-18):
```rust
pub fn decode(buf: &[u8]) -> Result<(Self, usize), ProtocolError>
```

**Why this is blocking**:
1. **Interface Contract Violation**: The specification explicitly defines this return type, which future daemon server/client implementations (issue-10, issue-11) will depend on
2. **Streaming Protocol Support**: Without returning bytes consumed, the protocol cannot handle streaming scenarios where multiple messages arrive in the same buffer
3. **Incomplete Message Handling**: The caller needs to know how many bytes to remove from the buffer after successful decode

**Required Fix**:
- `DaemonRequest::decode()` should return `Ok((request, 4 + length))`
- `DaemonResponse::decode()` should return `Ok((response, 5 + length))`
- Update all test cases to destructure the tuple: `let (decoded, consumed) = decode(...)`

---

## SHOULD_FIX Issues

### 1. Potential integer overflow in encode methods
**Severity**: SHOULD_FIX
**Location**: `src/daemon_protocol.rs:95, 188`

**Issue**: The code casts `usize` to `u32` without overflow checking. On 64-bit systems, if the payload exceeds `u32::MAX` (4,294,967,295 bytes ≈ 4GB), the cast will silently truncate, causing data corruption.

**Current Code**:
```rust
let length = code_bytes.len() as u32;  // Line 95
let length = output_bytes.len() as u32; // Line 188
```

**Why this matters**:
- While 4GB Python code is unrealistic, the protocol should fail gracefully rather than silently corrupt data
- This violates the principle of robust error handling
- Could cause mysterious failures if someone tries to use this for non-code data

**Recommended Fix**:
```rust
// Add new error variant
pub enum ProtocolError {
    InvalidUtf8(String),
    IncompleteMessage(String),
    InvalidStatus(u8),
    PayloadTooLarge(usize), // Add this
}

// In encode methods:
let length = code_bytes.len();
if length > u32::MAX as usize {
    return Err(ProtocolError::PayloadTooLarge(length));
}
let length = length as u32;
```

However, since `encode()` currently returns `Vec<u8>`, you'd need to change the signature to return `Result<Vec<u8>, ProtocolError>` to propagate this error. This would require updating all callers.

**Alternative approach**: Add a `checked_encode()` method that returns `Result`, keep the existing `encode()` for backwards compatibility but document the limitation.

### 2. Missing test coverage for bytes consumed
**Severity**: SHOULD_FIX
**Location**: `src/daemon_protocol.rs:236-619` (test module)

**Issue**: Once the decode signature is fixed to return `(Self, usize)`, tests should verify the bytes consumed value is correct.

**Required Test Cases**:
```rust
#[test]
fn test_request_decode_returns_correct_bytes_consumed() {
    let request = DaemonRequest::new("2+3");
    let encoded = request.encode();
    let (decoded, consumed) = DaemonRequest::decode(&encoded).unwrap();
    assert_eq!(consumed, 7); // 4 bytes length + 3 bytes code
    assert_eq!(decoded.code(), "2+3");
}

#[test]
fn test_response_decode_returns_correct_bytes_consumed() {
    let response = DaemonResponse::success("42");
    let encoded = response.encode();
    let (decoded, consumed) = DaemonResponse::decode(&encoded).unwrap();
    assert_eq!(consumed, 7); // 1 byte status + 4 bytes length + 2 bytes output
    assert_eq!(decoded.output(), "42");
}

#[test]
fn test_decode_with_trailing_data() {
    let request = DaemonRequest::new("2+3");
    let mut buffer = request.encode();
    buffer.extend_from_slice(b"extra trailing data");

    let (decoded, consumed) = DaemonRequest::decode(&buffer).unwrap();
    assert_eq!(consumed, 7);
    assert_eq!(decoded.code(), "2+3");
    // Verify trailing data wasn't consumed
    assert_eq!(&buffer[consumed..], b"extra trailing data");
}
```

---

## SUGGESTIONS

### 1. Consider adding validation for maximum payload size
**Severity**: SUGGESTION
**Location**: `src/daemon_protocol.rs:107, 201`

**Suggestion**: Add a constant `MAX_PAYLOAD_SIZE` and validate the length prefix doesn't exceed it. This protects against malicious clients sending huge length values that could cause memory exhaustion.

```rust
const MAX_PAYLOAD_SIZE: u32 = 100 * 1024 * 1024; // 100MB reasonable limit

pub fn decode(bytes: &[u8]) -> Result<(Self, usize), ProtocolError> {
    // ... existing length prefix reading ...

    if length > MAX_PAYLOAD_SIZE as usize {
        return Err(ProtocolError::PayloadTooLarge(length));
    }

    // ... rest of decode ...
}
```

### 2. Documentation could mention endianness explicitly
**Severity**: SUGGESTION
**Location**: `src/daemon_protocol.rs:10, 17`

**Suggestion**: While the doc comments mention "big-endian", it would be helpful to explicitly document why big-endian was chosen (network byte order standard, cross-platform compatibility).

---

## Summary

**Total Issues**: 1 BLOCKING, 2 SHOULD_FIX, 2 SUGGESTIONS

The implementation is high quality with comprehensive tests, but has one critical interface mismatch that must be fixed before merge. The decode methods must return the bytes consumed tuple as specified in the interface contract.
