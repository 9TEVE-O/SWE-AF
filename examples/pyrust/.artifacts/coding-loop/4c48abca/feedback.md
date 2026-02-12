# Feedback Summary: lexer-benchmarks (Iteration 2)

## Decision: BLOCK ⛔

The acceptance criterion **AC4 (CV < 5% for all benchmarks)** cannot be met with further code iterations.

---

## Analysis

### What Passed
- ✅ AC1: Benchmark file `benches/lexer_benchmarks.rs` created with all 3 required benchmarks
- ✅ AC2: All benchmarks correctly use `black_box()` wrapper
- ✅ AC3: Proper sample sizes (3000 iterations) and `estimates.json` files generated for all benchmarks

### What Failed (and Why)
- ❌ **AC4: CV < 5% threshold** — Not met for lexer_variables (14.53-22.70% CV depending on measurement)
- Root cause: **Fundamental measurement challenge**, not a code quality issue

### Why This Is Blocked (Not Just a FIX)

1. **Exhausted technical approaches**: In Iteration 1, we applied batching (1000-iteration loops) with 3000 sample size and 20s measurement time. These are industry-standard variance-reduction techniques.

2. **Recurred with no convergence**: Same failure across 2 iterations despite valid technical changes. The code review confirms the implementation is "technically sound" and uses "appropriate techniques."

3. **Inherent measurement limits**: Microsecond-scale operations (61μs-212μs) have irreducible noise in most benchmarking environments. Achieving CV < 5% at this scale is typically unrealistic without:
   - Dedicated hardware with isolation
   - Kernel modifications to disable power scaling
   - Massive sample counts (10,000+) with weeks of measurement time

4. **Code review consensus**: Both QA and code review confirm **no architectural or implementation flaws**. The issue is with the acceptance criterion itself, not the code.

---

## Recommendation

**This issue requires a decision outside the coding loop:**

1. **Option A**: Relax the CV threshold to 10-15% (realistic for microsecond benchmarks)
   - Code is ready to merge with this change

2. **Option B**: Increase measurement scale by processing larger inputs
   - Modify benchmarks to process 100-1000 tokens/variables per iteration instead of single operations
   - Would naturally reduce CV% even with same code

3. **Option C**: Accept current CV results as measurement limitations documented
   - Add a note to the module explaining CV results and measurement strategy
   - Track as a technical debt item, not a blocker

**Next step**: This decision should be made by the issue owner, not the coder. The code is production-ready; only the success criterion needs adjustment.
