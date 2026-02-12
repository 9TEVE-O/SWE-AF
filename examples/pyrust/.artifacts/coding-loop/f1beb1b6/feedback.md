# Feedback Summary

**Status**: FIX REQUIRED
**Blocker**: Critical indentation tracking algorithm is fundamentally broken

---

## Critical Issue: Indentation-Based Function Body Parsing

### Problem
The parser uses column position (`column == 1`) to detect the end of function bodies. This fails for:
- Nested functions
- Mixed indentation (tabs + spaces)
- Any valid Python code where a statement at column 1 appears during a function body
- Functions defined at non-zero indentation levels

**Location**: Parser function body parsing logic (indentation tracking section)

**Root Cause**: The algorithm assumes statements at column 1 end a function, which is incorrect. It should track indentation *levels* relative to the function definition line, not absolute column positions.

### Required Fix
Implement proper indentation level tracking:

1. **Track indentation context**: When entering a function body, record the base indentation level of the function definition line.
2. **Calculate relative indentation**: Each statement in the body should have indentation > base indentation of the def line.
3. **Detect body end**: The body ends when a token appears at indentation ≤ the def line's indentation level.
4. **Example**:
   ```python
   def outer():           # indentation level 0 (base)
       def inner():       # indentation level 1 (valid body statement)
           return 42      # indentation level 2 (valid nested body)
       return 0           # indentation level 1 (still in outer body)
   x = 1                  # indentation level 0 (ends outer function body)
   ```

### Test Case to Validate
Add test for nested function that currently fails:
```python
def outer():
    def inner():
        return 42
    return inner()
```

---

## High Priority Issues

### 1. Missing Indentation Validation
**File**: Parser function definition handler
**Issue**: Parser accepts non-indented function bodies (invalid Python)
**Fix**: Validate that the first statement in the function body has indentation > the def line's indentation. Reject code like:
```python
def foo():
return 42  # ERROR: not indented
```

### 2. Single-Line Functions Not Supported
**File**: Parser, line 177 (requires newline after colon)
**Issue**: Parser requires newline after `:` in function definitions, blocking valid Python:
```python
def foo(): return 42  # Should be valid
```
**Fix**: Allow function body to start on the same line as the colon. Check if next token is an expression (return, identifier, etc.) instead of requiring NEWLINE.

---

## Test Coverage Improvements Needed

Current tests use simple, consistently-indented code which masked indentation bugs. Add tests for:
- Nested functions (at least 2 levels)
- Functions at different indentation levels (not just column 0)
- Mixed indentation (tabs vs spaces) — validate rejection
- Invalid indentation (non-indented body) — validate error
- Single-line functions: `def foo(): return 42`
- Functions with multiple statements at different indentation levels

These tests should have caught the column-based detection bug.

---

## What's Working Well

✅ Lexer extensions (def, return, colon, comma) are correctly implemented
✅ Function call parsing (Expression::Call) is correct
✅ Return statement parsing with/without values is correct
✅ AST representation (FunctionDef, Return, Call) follows patterns correctly
✅ Code follows existing style and maintains zero-copy philosophy

---

## Next Steps

1. **Replace column-based detection** with proper indentation level tracking
2. **Add indentation validation** for function body statements
3. **Support single-line functions** (optional but recommended)
4. **Add comprehensive indentation tests** before submitting
5. Run full test suite (should still pass 300/300 after fixes)

All existing tests should continue passing with correct indentation tracking.
