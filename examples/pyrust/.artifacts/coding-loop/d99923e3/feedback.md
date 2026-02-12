# Feedback: register-state-optimization

**Action**: FIX

## Summary

The implementation passes all 357 tests and meets the structural acceptance criteria, but contains a **critical logic error** that completely negates the optimization's intended 90-95% performance improvement. The compiler currently stores a **global max_register_used** (the maximum register used anywhere in the code) into every function's metadata. This means all functions will save all registers if any code uses high registers, defeating the entire purpose of the optimization.

## Critical Issue

**Problem**: Compiler tracks global `max_register_used`, not per-function
- Current behavior: Store the maximum register index used across **all code** in each function's metadata
- Result: All functions save the same number of registers, regardless of their actual register usage
- Impact: Zero performance benefit in real code (negates 90-95% improvement claim)

**Fix Required**: Modify the compiler to track `max_register_used` **separately for each function** during compilation.

## Actionable Changes

1. **In the compiler (during function compilation)**:
   - When entering a function context, reset or initialize a per-function `max_register_used` counter
   - During compilation of that function's instructions, update **this function's** counter, not a global one
   - Store the final per-function value into that function's `FunctionMetadata.max_register_used`
   - This ensures each function only saves the registers it actually uses

2. **Verify the fix**:
   - Simple function using only registers [0..2] should have `max_register_used = 2`
   - Complex function using registers [0..7] should have `max_register_used = 7`
   - Not all functions should have the same `max_register_used` value

## Example of Expected Behavior After Fix

```
Function A uses only r0, r1, r2 → stores max_register_used = 2
Function B uses r0..r7          → stores max_register_used = 7
Function C uses only r0         → stores max_register_used = 0

Result: Function calls save only the registers they need
```

## Test Validation

Once fixed, re-run all tests. The optimization should:
- Still pass all 357 tests
- Show ~90-95% performance improvement for register-light functions
- Show modest improvement for register-heavy functions
- Vary per-function, not be uniform across all functions
