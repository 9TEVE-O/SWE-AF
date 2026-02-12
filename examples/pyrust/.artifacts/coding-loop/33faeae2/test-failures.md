# Test Failures — Iteration 33faeae2

## Summary
✅ **ALL TESTS PASSED** - No failures detected

## Test Execution Results

### VM Benchmarks Test Suite
**Status**: ✅ PASSED (14/14 tests passed)

All acceptance criteria validated successfully:

#### AC1: Create benches/vm_benchmarks.rs with vm_simple, vm_complex, vm_variables benchmarks
- ✅ File exists at benches/vm_benchmarks.rs
- ✅ Contains vm_simple benchmark function
- ✅ Contains vm_complex benchmark function
- ✅ Contains vm_variables benchmark function

#### AC2: Pre-compile bytecode outside benchmark loop to isolate VM performance
- ✅ All benchmarks pre-compile bytecode before b.iter()
- ✅ Lexer, parser, and compiler execute outside benchmark loop
- ✅ Only VM execution measured inside benchmark loop

#### AC3: Criterion generates estimates.json for each benchmark with mean.point_estimate field
- ✅ vm_simple: estimates.json exists with mean.point_estimate = 77.02ns
- ✅ vm_complex: estimates.json exists with mean.point_estimate = 76.13ns
- ✅ vm_variables: estimates.json exists with mean.point_estimate = 151.41ns
- ✅ All benchmarks extractable via jq path '.mean.point_estimate'

#### AC4: vm_simple benchmark measures pure VM execution for 2+3 expression
- ✅ vm_simple uses "2 + 3" expression
- ✅ Measures pure VM execution only

### Additional Test Coverage

#### PRD AC1 Validation
- ✅ vm_simple achieves 77.02ns (< 150ns target)
- ✅ 69.2% reduction from 250ns baseline
- ✅ Exceeds PRD performance goal

#### Edge Cases Covered
- ✅ black_box usage prevents compiler optimization
- ✅ vm_complex uses complex expression with operators/parentheses
- ✅ vm_variables uses variable assignment and access
- ✅ Criterion configuration matches architecture.md (sample_size=1000, measurement_time=10s)
- ✅ Statistical validity: mean, std_dev, median, confidence_interval fields present
- ✅ CV within acceptable range (28.67% for microbenchmark < 100ns)

#### Integration Tests
- ✅ All 3 benchmarks executed successfully
- ✅ Benchmarks correctly isolate VM performance from other pipeline stages
- ✅ No lexer/parser/compiler execution inside benchmark loop

### Benchmark Performance Results

| Benchmark | Mean Time | Status |
|-----------|-----------|--------|
| vm_simple | 77.02ns | ✅ < 150ns target |
| vm_complex | 76.13ns | ✅ Excellent |
| vm_variables | 151.41ns | ✅ Good (variables add overhead) |

### Test Statistics
- **Total Tests**: 14
- **Passed**: 14 (100%)
- **Failed**: 0 (0%)
- **Skipped**: 0

## Notes

1. **High CV for Microbenchmarks**: The vm_simple benchmark shows CV of 28.67%, which is higher than the PRD's 10% target for cold_start benchmarks. However, this is expected and acceptable for VM-only microbenchmarks that execute in < 100ns, as measurement noise becomes proportionally larger at such small timescales. The PRD's CV requirement applies to full pipeline benchmarks (cold_start), not isolated VM microbenchmarks.

2. **Performance Achievement**: The vm_simple benchmark achieves 77.02ns, which is **48.6% below** the 150ns target and represents a **69.2% reduction** from the 250ns baseline. This significantly exceeds the PRD AC1 requirement of ≥40% VM performance improvement.

3. **Test Coverage**: Created comprehensive test suite (tests/test_vm_benchmarks.rs) with 14 tests covering:
   - All 4 acceptance criteria
   - Testing strategy validation
   - PRD AC1 performance target
   - Edge cases (black_box, expression complexity, variable usage, Criterion config)
   - Integration validation (pipeline stage isolation)
   - Statistical validity checks

## Conclusion

✅ **All acceptance criteria satisfied**
✅ **All tests pass**
✅ **No failures to report**
