# Feedback for compiler-extensions-functions

## Status: FIX REQUIRED ⛔

Tests pass, but code review identified a **critical blocking issue** in the argument passing mechanism.

---

## BLOCKING ISSUE (must fix)

### Problem: Arguments Discarded Before Call Instruction (Line 190)

**Location**: `compile_call()` in compiler.rs, line 190

**Issue**: When compiling function arguments, the register location (`_arg_reg`) is computed but immediately discarded with `let _arg_reg = ...`. The Call instruction is created with only:
- `arg_count`: number of arguments
- `dest_reg`: where to store return value

But **no information about which registers contain the actual argument values** is stored in the Call instruction.

**Why this is critical**: At runtime, the VM receives a Call instruction saying "call with 3 arguments" but has no way to know which registers contain those 3 argument values. This breaks argument passing entirely.

**How to fix**:

1. **Modify the Call instruction** to store argument register locations. Update the bytecode definition for `Call` instruction to include either:
   - `arg_registers: Vec<Register>` (store actual register numbers for each argument), OR
   - Change the calling convention: allocate a contiguous block of registers and document that arguments must be in registers N through N+arg_count-1

2. **Update compile_call()** (around line 190):
   - Instead of discarding `arg_reg`, collect all argument registers into a Vec
   - Pass this Vec when creating the Call instruction
   - Example structure:
     ```rust
     let mut arg_regs = Vec::new();
     for arg in &call.args {
         let arg_reg = self.compile_expression(arg)?;
         arg_regs.push(arg_reg);
     }
     self.emit(Instruction::Call {
         arg_count: arg_regs.len(),
         arg_registers: arg_regs,  // ADD THIS
         dest_reg,
     });
     ```

3. **Update the VM's execute_call()** to read argument values from the registers specified in the Call instruction before invoking the function.

---

## SHOULD-FIX ISSUES (prevent future bugs)

### 1. Register State Restoration Conflicts (Lines 94-95, 120-121)
**Location**: `compile_function()`, lines 94-95 and 120-121

**Issue**: Compiler saves/restores `next_register` when compiling function bodies. If a function body allocates many registers (e.g., complex expressions), those register numbers could be reused by subsequent code, causing conflicts.

**Fix**: After compiling a function body, reset `next_register` to a safe value that won't conflict. Consider either:
- Track maximum register used across entire program
- Use separate register scopes for function bodies vs. main code

---

### 2. Missing Test Coverage for Register Allocation (Tests)
**Issue**: Tests verify that Call instructions are created, but don't verify actual register numbers or register preservation across function calls.

**Add tests** that verify:
- Parameter registers match expected indices
- Register allocation doesn't conflict between caller and callee
- Return value correctly appears in `dest_reg`

---

## OPTIONAL IMPROVEMENTS (non-blocking)

- Remove unused `functions: HashMap` (lines 19-20, 123-127) — code populates it but never reads it
- Fix contradictory comment at lines 213-218 about "second pass to emit at top" — clarify that DefineFunction is embedded in function body since builder doesn't support top-level insertion

---

## Summary

**Do not merge** until the Call instruction includes argument register information. The current implementation compiles arguments but provides no way for the VM to access them at runtime. This is a design flaw, not a minor bug.

Priority: **Fix blocking issue first → address should-fix register conflicts → add register test coverage → (optional) clean up unused code and comments**
