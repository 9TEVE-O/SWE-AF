# Code Review Issues - Register State Optimization

## BLOCKING Issues

### 1. Incorrect max_register_used in FunctionMetadata (CRITICAL)

**Location**: `src/vm.rs:289`

**Issue**: When storing function metadata during DefineFunction execution, the code stores the **global** `bytecode.metadata.max_register_used` value for every function:

```rust
max_register_used: Some(bytecode.metadata.max_register_used),
```

**Problem**: This defeats the entire optimization! The global `max_register_used` tracks the maximum register used across ALL code (main program + all functions). If the main program uses register 255, then EVERY function will save all 256 registers (0-255), even if an individual function only uses registers 0-2.

**Impact**:
- Optimization provides **zero benefit** in most realistic scenarios
- A simple function using 3 registers will save all 256 registers if any other code uses high registers
- The promised 90-95% performance improvement will not materialize
- Tests may pass (they work correctly, just inefficiently) but benchmarks will show no improvement

**Root Cause**: The compiler tracks only a single global `max_register_used` value and doesn't track per-function register usage.

**Required Fix**:
1. Compiler must track `max_register_used` separately for each function during compilation
2. Store per-function max_register_used in bytecode (options: add field to DefineFunction instruction, or create parallel metadata array)
3. VM must use function-specific max_register_used when creating call frames

---

### 2. Missing per-function register tracking in compiler

**Location**: `src/compiler.rs:324-402`

**Issue**: The compiler has only a single `max_register_used` field (line 86) that accumulates the global maximum across all code. When compiling function bodies:

1. It saves/restores `next_register` for register allocation isolation (lines 327, 358)
2. But it does NOT track or save the maximum register used within each specific function
3. All function compilations update the same global `max_register_used`

**Missing Logic**:
```rust
// Should track per-function max, like:
let function_max_register = self.max_register_used;
// ... compile function body ...
function_metadata.push((name, params, body_start, body_len, function_max_register));
```

**Required Fix**:
1. Before compiling each function, save the current `max_register_used` value
2. After compiling the function body, capture the function-specific `max_register_used`
3. Store this per-function value in the metadata structure
4. Reset or manage `max_register_used` appropriately for the next function

---

## Verification

**How to verify this is a problem**:
1. Create a test where main program uses high registers (e.g., 100+)
2. Define a simple function that only uses 2-3 registers
3. Add debug logging to see how many registers are saved during the function call
4. Expected (if bug exists): Will save 100+ registers
5. Expected (if fixed): Will save only 2-3 registers

**Example test case**:
```rust
// Main uses many registers
let x0 = 1;
let x1 = 2;
// ... lots of variables forcing high register usage ...
let x50 = 51;

// Simple function using only 2 registers
def simple():
    a = 10
    b = 20
    return a + b

result = simple()
```

With the current bug, `simple()` will save 50+ registers. With the fix, it should save only ~2-5 registers.
