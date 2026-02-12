# Merged Feedback: integration-regression-functions

## Decision: **FIX**

Your test infrastructure is excellent (69 integration tests + 16 benchmarks), and you correctly identified the root cause. However, AC2.1-AC2.5 are BLOCKING until the compiler bytecode layout bug is fixed. Most acceptance criteria cannot pass with the current compiler implementation.

---

## Critical Blocker (Iteration 2 Priority)

### Compiler Bytecode Layout Bug
**What:** Function bodies are emitted BEFORE `DefineFunction` instructions instead of AFTER `Halt`, causing immediate execution and "Return outside of function" errors.

**Impact:**
- AC2.1 FAILS: End-to-end execution impossible (35+ tests fail with this error)
- AC2.2 FAILS: Zero-parameter functions fail
- AC2.3 FAILS: Parameterized functions fail (24 tests show "Undefined variable" for parameters)
- AC2.4 FAILS: Scope isolation cannot be tested
- AC2.5 FAILS: Return statements fail when in function context
- AC2.7 FAILS: Only ~8 tests pass (error handling); 48 created but 40 fail due to this bug

**Fix Required:**
In your compiler's bytecode generation:
1. Emit `DefineFunction` instruction with function metadata
2. Emit `Halt` to skip function body during definition
3. Emit function body bytecode AFTER the `Halt`
4. When a function is called, `call` instruction jumps to the function body location

Current (broken): `[FunctionBody bytecode, DefineFunction]`
Correct: `[DefineFunction, Halt, FunctionBody bytecode]`

**How to Verify:** After fixing, all 69 integration tests should pass (currently only 8 pass).

---

## Missing Regression Verification

### AC2.6 Regression Gate
You claim "338 library tests pass" but provided no evidence (no test run output).

**What to do:**
1. Run the full test suite and capture output
2. Include actual test run evidence in next iteration (test execution logs showing "338 passed")
3. Clarify the test count discrepancy (you mention 199 required, 338 passing, but ~462 tests exist)

---

## AC2.7 Test Status Clarification

Your 69 created tests are comprehensive and well-designed, but AC2.7 requires **20+ PASSING tests**, not just 20 created tests.

**Current state:** Only ~8 error handling tests pass; 40 others fail due to the compiler bug.

**Next iteration:** All 69 tests should pass once the compiler is fixed.

---

## Performance Benchmark (AC2.8)

Benchmarks compile successfully and infrastructure is solid. However, they measure code that doesn't execute correctly due to the compiler bug.

**Action for next iteration:** Re-run benchmarks after fixing compiler. Function call overhead should be < 5μs when tested on correctly-executing code.

---

## Summary of Required Changes

**Iteration 2 must:**
1. **FIX the compiler bytecode layout** — This is the single blocking issue
   - Verify `DefineFunction` instruction placement
   - Ensure function bodies execute only when called, not during definition
   - Confirm `Halt` correctly skips function body during definition

2. **Provide regression test evidence** — Run full test suite and document results

3. **Re-run performance benchmarks** — Measure overhead on working code

**Expected outcome:** AC2.1-AC2.8 all pass, 69 integration tests pass, regression gate passes.

---

## What's Working Well

✓ Test infrastructure (69 comprehensive integration tests)
✓ Test coverage (AC2.1-AC2.5 have complete test cases)
✓ Test quality (excellent organization, clear assertions, edge cases)
✓ Benchmark infrastructure (16 performance benchmarks set up correctly)
✓ Root cause identification (you correctly diagnosed the bytecode layout issue)

Focus next iteration on fixing the compiler, not on test design — that part is solid.
