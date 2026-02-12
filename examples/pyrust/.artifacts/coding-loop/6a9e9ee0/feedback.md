# Feedback: Iteration 6a9e9ee0

**Decision**: ❌ FIX REQUIRED

**Summary**: Forward reference validation is incomplete. While main-level validation works correctly, function bodies are not validated, allowing forward references inside functions to pass without error.

---

## BLOCKING ISSUE: Function Bodies Not Validated

**Location**: `src/compiler.rs`, lines 391-401 (in `compile_program()`)

**Problem**:
The current code only validates main-level statements. When a `FunctionDef` is encountered, it's added to `function_defs` but its body statements are never checked for forward references.

**Example that should fail but currently passes**:
```python
def foo():
    bar()  # Should error - bar not defined yet
def bar():
    return 42
```

**Fix Required**:
Add validation for function body statements immediately after line 394:

```rust
if let Statement::FunctionDef { name, body, .. } = stmt {
    function_defs.push(stmt);
    // ADD THIS: Validate function body for forward references
    for body_stmt in body {
        Self::validate_no_forward_references(body_stmt, &defined_so_far, &all_defined_functions)?;
    }
    defined_so_far.insert(name.clone());
}
```

**Why this is critical**: AC4.3 requires detecting forward references in ALL contexts, not just main-level code. Without validating function bodies, the implementation is incomplete.

---

## NON-BLOCKING DEBT (track but don't fix now)

- **Error message clarity**: Consider changing "Call to undefined function" to "Forward reference error: function called before defined" for clearer messaging
- **Documentation**: Add doc comments explaining what forward references are and why they're prohibited

---

## Test Status

✅ AC4.3: `test_function_calling_before_definition` passes (for main-level case)
✅ AC4.2: All 377 library tests pass (3 failures are not regressions)

However, the fix above is needed to ensure forward references are caught in ALL contexts.

---

## Action Items

1. Add the function body validation loop in `compile_program()` around line 394
2. Re-run tests to verify both AC4.3 and AC4.2 still pass
3. No other changes needed - the validation logic itself is correct, it's just not being applied to function bodies
