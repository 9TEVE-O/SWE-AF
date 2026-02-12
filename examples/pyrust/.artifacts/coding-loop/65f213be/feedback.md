# Feedback for daemon-protocol Implementation

## Decision: FIX

All tests pass and functionality is solid, but there is **1 BLOCKING issue** that must be fixed before approval.

---

## 🚨 BLOCKING ISSUE

### Decode methods must return bytes consumed

**Files**: `src/daemon.rs` (or wherever `Request::decode` and `Response::decode` are implemented)

**Problem**: The decode methods currently return `Result<Self, ProtocolError>` but the interface specification requires `Result<(Self, usize), ProtocolError>`.

**Why this matters**: The `usize` indicates how many bytes were consumed from the buffer. This is critical for streaming protocols where multiple messages may be in the buffer, or where you need to know how much data to discard after processing.

**Fix**:
1. Update `Request::decode(bytes: &[u8])` signature to return `Result<(Request, usize), ProtocolError>`
2. Update `Response::decode(bytes: &[u8])` signature to return `Result<(Response, usize), ProtocolError>`
3. Calculate bytes consumed:
   - For `Request`: `4 + code.len()` (u32 length prefix + UTF-8 code)
   - For `Response`: `1 + 4 + output.len()` (u8 status + u32 length prefix + UTF-8 output)
4. Return `Ok((decoded_message, bytes_consumed))`
5. Update all call sites to destructure the tuple: `let (request, consumed) = Request::decode(buf)?;`

**Example**:
```rust
impl Request {
    pub fn decode(bytes: &[u8]) -> Result<(Self, usize), ProtocolError> {
        // ... existing validation ...
        let code = String::from_utf8(bytes[4..4 + length].to_vec())
            .map_err(|_| ProtocolError::InvalidUtf8)?;
        let consumed = 4 + length;
        Ok((Request { code }, consumed))
    }
}
```

---

## ⚠️ SHOULD FIX (fix these while you're at it)

### 1. Add integer overflow protection
**Lines**: 95, 188 in encode methods

The code casts `usize` to `u32` without checking for overflow. On 64-bit systems, payloads >4GB will silently truncate.

**Fix**:
- Add `PayloadTooLarge` variant to `ProtocolError`
- Check before casting: `let length = u32::try_from(code.len()).map_err(|_| ProtocolError::PayloadTooLarge)?;`

### 2. Add test coverage for bytes consumed
Once the decode signature is fixed, add tests to verify `bytes_consumed` is correct:
- Test that `consumed` equals the exact message size
- Test `decode` with trailing data to ensure only message bytes are consumed

---

## ✅ What's Good

- Comprehensive test coverage (37 tests)
- All acceptance criteria functionally met
- Clean error handling
- Good edge case coverage

## Next Steps

Fix the blocking issue (decode return type), apply the two should-fix items, and you're done.
