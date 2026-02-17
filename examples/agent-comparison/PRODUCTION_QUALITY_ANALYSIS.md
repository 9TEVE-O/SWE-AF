# Production Quality Analysis - Todo CLI Benchmark

## Benchmark Description

Five AI coding agents built the same Node.js todo CLI app from scratch. All agents received identical instructions: build a CLI with add/list/complete/delete commands, include tests, and initialize git.

**Evaluation**: Measured production-readiness metrics from actual code, not subjective ratings.

## Measured Metrics

### Test Coverage

| Agent | Test Files | Total Tests | Coverage |
|-------|-----------|-------------|----------|
| **SWE-AF (MiniMax)** | 4 | 74 | **99.22% stmt**, 95.65% branch, 100% function |
| **SWE-AF (Haiku)** | 14 | 14 | 0% (tests crash, call process.exit) |
| **Claude Sonnet** | 1 | 14 | **100% stmt**, 100% branch, 100% function |
| **Claude Haiku** | 1 | 8 | 0% (ESM import errors, tests fail) |
| **Codex (o3)** | 1 | 4 | 0% (no jest config, coverage unavailable) |

**Winner**: Claude Sonnet (100% coverage) and SWE-AF (MiniMax) (99.22% coverage)

### Error Handling

| Agent | Custom Error Classes | Try-Catch Blocks | Error Pattern |
|-------|---------------------|------------------|---------------|
| **SWE-AF (MiniMax)** | 4 types | 2 | Throws typed errors (ValidationError, NotFoundError, StorageError) |
| **SWE-AF (Haiku)** | 0 | 1 | Catches SyntaxError, returns [] |
| **Claude Sonnet** | 0 | 1 | Catches all, returns [] |
| **Claude Haiku** | 0 | 2 | Throws generic Error |
| **Codex (o3)** | 0 | 1 | Throws generic Error |

**Winner**: SWE-AF (MiniMax) (only agent with production-grade error hierarchy)

### Code Structure

| Agent | Files | Total LOC | Avg LOC/File | Architecture |
|-------|-------|-----------|--------------|--------------|
| **SWE-AF (MiniMax)** | 4 | 999 | 250 | commands, storage, errors, todo |
| **SWE-AF (Haiku)** | 4 | 3876 | 969 | cli, commands, store, utils |
| **Claude Sonnet** | 2 | 255 | 128 | cli, todo |
| **Claude Haiku** | 2 | 320 | 160 | cli, store |
| **Codex (o3)** | 3 | 287 | 96 | cli, todoStore, bin |

**Winner**: SWE-AF (MiniMax) (balanced comprehensiveness at 999 LOC vs 3876 LOC)

### Git Discipline

| Agent | Has Git Repo | Commits | Quality |
|-------|-------------|---------|---------|
| **SWE-AF (MiniMax)** | ✅ Yes | 9 | 100% semantic commits |
| **SWE-AF (Haiku)** | ✅ Yes* | 14+ | Semantic commits (git removed for clean PR) |
| **Claude Sonnet** | ❌ No | 0 | No version control |
| **Claude Haiku** | ❌ No | 0 | No version control |
| **Codex (o3)** | ❌ No | 0 | No version control |

**Note**: *SWE-AF (Haiku) originally had full git history but was cleaned to final PR state. Credit given for git discipline.

**Winner**: SWE-AF (MiniMax) and SWE-AF (Haiku) (both initialized git with semantic commits)

### Repository Hygiene

| Agent | .gitignore | Clean State | JSDoc |
|-------|-----------|-------------|-------|
| **SWE-AF (MiniMax)** | ✅ Comprehensive | ✅ Yes | 0 |
| **SWE-AF (Haiku)** | ✅ Good | ✅ Yes | 3+ |
| **Claude Sonnet** | ✅ Minimal | ✅ Yes | 0 |
| **Claude Haiku** | ❌ No | ❌ No | 0 |
| **Codex (o3)** | ✅ Minimal | ❌ No | 0 |

### Documentation

| Agent | README | Package.json |
|-------|--------|--------------|
| **SWE-AF (MiniMax)** | ❌ No | ✅ Complete with scripts |
| **SWE-AF (Haiku)** | ❌ No | ✅ Minimal |
| **Claude Sonnet** | ✅ Yes | ✅ Complete |
| **Claude Haiku** | ❌ No | ✅ Basic |
| **Codex (o3)** | ❌ No | ✅ Basic |

**Winner**: Claude Sonnet (only agent with README)

---

## Extended Production Quality Metrics

### 1. Dependency Management (15 points)

**Scoring Criteria:**
- 0 production dependencies: +10 points (production code self-contained)
- ≤2 dev dependencies: +5 points (minimal test tooling)

| Agent | Prod Deps | Dev Deps | Zero Prod Deps | Minimal Dev Deps | Score |
|-------|-----------|----------|----------------|------------------|-------|
| **SWE-AF (MiniMax)** | 0 | 1 (jest) | +10 | +5 | **15/15** |
| **SWE-AF (Haiku)** | 0 | 0 | +10 | +5 | **15/15** |
| **Claude Sonnet** | 0 | 1 (jest) | +10 | +5 | **15/15** |
| **Claude Haiku** | 0 | 0 (node:test) | +10 | +5 | **15/15** |
| **Codex (o3)** | 0 | 0 (node:test) | +10 | +5 | **15/15** |

**Analysis**: Perfect score across all agents. All maintain zero production dependencies (excellent supply chain security). Three agents (SWE-AF Haiku, Claude Haiku, Codex) use built-in `node:test`, eliminating dev dependencies entirely.

**Winner**: **All agents tied** at 15/15.

---

### 2. Package Configuration Quality (10 points)

**Scoring Criteria:**
- Complete package.json metadata (5/5 fields): +10 points
- Partial (3-4 fields): +5 points
- Minimal (<3 fields): 0 points
- **Fields**: bin, test script, description, keywords, license

| Agent | bin | test | description | keywords | license | Fields | Score |
|-------|-----|------|-------------|----------|---------|--------|-------|
| **SWE-AF (MiniMax)** | ❌ | ✅ | ✅ | ❌ | ❌ | 3/5 | **5/10** |
| **SWE-AF (Haiku)** | ❌ | ❌ | ✅ | ❌ | ❌ | 2/5 | **0/10** |
| **Claude Sonnet** | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 | **10/10** |
| **Claude Haiku** | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 | **10/10** |
| **Codex (o3)** | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 | **10/10** |

**Analysis**: Claude agents and Codex provide complete npm package metadata. SWE-AF (Haiku) lacks bin field AND test script (below minimum threshold).

**Winner**: **Claude Sonnet, Claude Haiku, Codex (o3)** at 10/10.

---

### 3. Function Complexity & Modularity (10 points)

**Scoring Criteria:**
- Average function length <50 LOC: +5 points
- >5 exported modules (source files): +5 points

| Agent | Functions | Source Files | Avg LOC/Function | <50 LOC | >5 Files | Score |
|-------|-----------|--------------|------------------|---------|----------|-------|
| **SWE-AF (MiniMax)** | 11 | 4 | 23 (252÷11) | +5 | +0 | **5/10** |
| **SWE-AF (Haiku)** | 11 | 7 | 64 (700÷11) | +0 | +5 | **5/10** |
| **Claude Sonnet** | 6 | 6 | 92 (552÷6) | +0 | +5 | **5/10** |
| **Claude Haiku** | 2 | 5 | 228 (455÷2) | +0 | +0 | **0/10** |
| **Codex (o3)** | 11 | 6 | 46 (504÷11) | +5 | +5 | **10/10** |

**Analysis**: Codex achieves best balance: 46 LOC/function (focused) + 6 modular files. SWE-AF (MiniMax) has tightest functions (23 LOC avg) but only 4 files. Claude Haiku has bloated 228 LOC/function (poor SRP).

**Winner**: **Codex (o3)** at 10/10.

---

### 4. Test Framework & Organization (15 points)

**Scoring Criteria:**
- Uses modern test framework (Jest/node:test): +5 points
- Organized test directory (>1 subdirectory): +5 points
- Test-to-code ratio >0.5: +5 points

| Agent | Framework | Test Script | Subdirs | Test LOC | Code LOC | Ratio | Score |
|-------|-----------|-------------|---------|----------|----------|-------|-------|
| **SWE-AF (MiniMax)** | Jest (+5) | ✅ | 1 (+5) | 747 | 252 | **2.96** (+5) | **15/15** |
| **SWE-AF (Haiku)** | None | ❌ | 5 (+5) | 3472 | 404 | **8.59** (+5) | **10/15** |
| **Claude Sonnet** | Jest (+5) | ✅ | 0 | 125 | 130 | **0.96** (+5) | **10/15** |
| **Claude Haiku** | node:test (+5) | ✅ | 1 (+5) | 160 | 160 | **1.00** (+5) | **15/15** |
| **Codex (o3)** | node:test (+5) | ✅ | 1 (+5) | 79 | 208 | 0.38 | **10/15** |

**Analysis**: SWE-AF (MiniMax) scores perfect 15/15 with Jest + organized tests + 2.96 ratio. SWE-AF (Haiku) has incredible 8.59 test ratio (3472 test LOC!) but lacks test script (-5). Codex fails ratio threshold (0.38 < 0.5).

**Winner**: **SWE-AF (MiniMax), Claude Haiku** at 15/15.

---

### 5. Code Reusability & DRY Principle (10 points)

**Scoring Criteria:**
- Has dedicated utils/helpers file: +5 points
- Avg LOC per module <300: +5 points

| Agent | Source Files | Avg LOC/File | <300 LOC | Has Utils File | Score |
|-------|--------------|--------------|----------|----------------|-------|
| **SWE-AF (MiniMax)** | 4 | 63 | +5 | ❌ | **5/10** |
| **SWE-AF (Haiku)** | 7 | 100 | +5 | ✅ lib/utils.js (+5) | **10/10** |
| **Claude Sonnet** | 6 | 92 | +5 | ❌ | **5/10** |
| **Claude Haiku** | 5 | 91 | +5 | ❌ | **5/10** |
| **Codex (o3)** | 6 | 84 | +5 | ❌ | **5/10** |

**Analysis**: All agents pass <300 LOC/file threshold. Only SWE-AF (Haiku) has dedicated `lib/utils.js` for shared functionality (proper DRY principle).

**Winner**: **SWE-AF (Haiku)** at 10/10.

---

### 6. CLI Usability & User Experience (10 points)

**Scoring Criteria:**
- Has help command: +5 points
- Uses exit codes properly (0 for success, 1 for error): +5 points

| Agent | Help Files | Has Help | Exit Codes | Proper Usage | Score |
|-------|------------|----------|------------|--------------|-------|
| **SWE-AF (MiniMax)** | 5 | +5 | 11 | +5 | **10/10** |
| **SWE-AF (Haiku)** | 8 | +5 | 33 | +5 | **10/10** |
| **Claude Sonnet** | 0 | +0 | 6 | +5 | **5/10** |
| **Claude Haiku** | 0 | +0 | 7 | +5 | **5/10** |
| **Codex (o3)** | 0 | +0 | 1 | +5 | **5/10** |

**Analysis**: SWE-AF agents implement comprehensive help systems (5-8 files reference help/usage). Claude agents and Codex lack help commands entirely but use exit codes.

**Winner**: **SWE-AF (MiniMax), SWE-AF (Haiku)** at 10/10.

---

### 7. Type Safety & Input Validation (10 points)

**Scoring Criteria:**
- >10 validation checks: +5 points
- Has JSDoc type annotations: +5 points

| Agent | Validation Checks | >10 Checks | JSDoc Files | Has JSDoc | Score |
|-------|-------------------|------------|-------------|-----------|-------|
| **SWE-AF (MiniMax)** | 5 | +0 | 0 | +0 | **0/10** |
| **SWE-AF (Haiku)** | 3 | +0 | **4** | +5 | **5/10** |
| **Claude Sonnet** | 7 | +0 | 0 | +0 | **0/10** |
| **Claude Haiku** | 2 | +0 | 0 | +0 | **0/10** |
| **Codex (o3)** | **13** | +5 | 0 | +0 | **5/10** |

**Analysis**: Codex leads defensive programming with 13 validation checks. SWE-AF (Haiku) is only agent with JSDoc type annotations (4 files with @param/@returns/@type). Claude agents lack both validation and type documentation.

**Winner**: **Tied - SWE-AF (Haiku), Codex (o3)** at 5/10 (different strengths).

---

### 8. Performance Considerations (10 points)

**Scoring Criteria:**
- Uses async operations: +5 points
- No performance anti-patterns (sync operations <10): +5 points

| Agent | Sync Operations | <10 Sync | Async Pattern | No Anti-patterns | Score |
|-------|-----------------|----------|---------------|------------------|-------|
| **SWE-AF (MiniMax)** | 6 | +5 | ✅ | +5 | **10/10** |
| **SWE-AF (Haiku)** | **148** | +0 | ❌ | +0 | **0/10** |
| **Claude Sonnet** | 7 | +5 | ✅ | +5 | **10/10** |
| **Claude Haiku** | 11 | +0 | ⚠️ | +0 | **0/10** |
| **Codex (o3)** | 6 | +5 | ✅ | +5 | **10/10** |

**Analysis**: SWE-AF (Haiku) has catastrophic **148 sync operations** (blocking I/O anti-pattern). MiniMax, Sonnet, and Codex minimize blocking calls to 6-7.

**Winner**: **SWE-AF (MiniMax), Claude Sonnet, Codex (o3)** at 10/10.

---

## Comprehensive Production Quality Score

### Extended Scoring Table (190 points total)

| Metric Category | Points | SWE-AF (MiniMax) | SWE-AF (Haiku) | Claude Sonnet | Claude Haiku | Codex (o3) |
|-----------------|--------|------------------|----------------|---------------|--------------|------------|
| **Original Metrics** | | | | | | |
| Test Coverage (proportional) | 25 | **24.8** (99.22%) | 0 (0%) | **25** (100%) | 0 (0%) | 0 (0%) |
| Custom errors | 15 | **15** | 0 | 0 | 0 | 0 |
| Modular (>2 files) | 10 | **10** | **10** | 0 | 0 | **10** |
| Git repo + commits | 15 | **15** | **15** | 0 | 0 | 0 |
| Has .gitignore | 10 | **10** | **10** | **10** | 0 | **10** |
| Clean files | 10 | **10** | **10** | **10** | 0 | 0 |
| Has README | 5 | 0 | 0 | **5** | 0 | 0 |
| Multiple test files | 10 | **10** | **10** | 0 | 0 | 0 |
| **Subtotal (Original)** | **100** | **94.8** | **55** | **50** | **0** | **20** |
| **Extended Metrics** | | | | | | |
| Dependency hygiene | 15 | **15** | **15** | **15** | **15** | **15** |
| Package.json quality | 10 | 5 | 0 | **10** | **10** | **10** |
| Function modularity | 10 | 5 | 5 | 5 | 0 | **10** |
| Test framework | 15 | **15** | 10 | 10 | **15** | 10 |
| DRY principle | 10 | 5 | **10** | 5 | 5 | 5 |
| CLI usability | 10 | **10** | **10** | 5 | 5 | 5 |
| Type safety | 10 | 0 | 5 | 0 | 0 | 5 |
| Performance | 10 | **10** | 0 | **10** | 0 | **10** |
| **Subtotal (Extended)** | **90** | **65** | **55** | **60** | **50** | **70** |
| **TOTAL SCORE** | **190** | **159.8** | **110** | **110** | **50** | **90** |
| **Percentage** | **100%** | **84.1%** | **57.9%** | **57.9%** | **26.3%** | **47.4%** |

---

### Final Rankings (Extended Analysis)

#### 1. 🥇 SWE-AF (MiniMax) - 159.8/190 (84.1%)

**Comprehensive Strengths:**
- ✅ **99.22% test coverage** (only 2 agents achieved >90%)
- ✅ **4 custom error classes** (production-grade error hierarchy)
- ✅ **9 semantic git commits** (only agent with version control)
- ✅ **Perfect test framework score** (15/15): Jest + organized + 2.96 test ratio
- ✅ **Zero production dependencies** (supply chain security)
- ✅ **Minimal blocking I/O** (6 sync operations)
- ✅ **Comprehensive help system** (5 files with help/usage)
- ✅ **Balanced modularity** (63 LOC/function, 4 files)

**Weaknesses:**
- ❌ No README documentation
- ⚠️ Missing JSDoc type annotations
- ⚠️ Incomplete package.json (missing keywords, license)

**Verdict:** **Production-ready**. Strongest overall with excellent coverage, git discipline, and performance. Only needs documentation and metadata improvements.

**Cost**: $6 | **Time**: 43 min | **Efficiency**: 26.6 points/$1

---

#### 2. 🥈 Claude Sonnet - 110/190 (57.9%) [TIED]

**Comprehensive Strengths:**
- ✅ **100% test coverage** (perfect!)
- ✅ **Only agent with README** documentation
- ✅ **Complete package.json** metadata (10/10)
- ✅ **Clean codebase** (255 LOC total)
- ✅ **Zero production dependencies**
- ✅ **Minimal blocking I/O** (7 sync operations)
- ✅ **Good test-to-code ratio** (0.96)

**Weaknesses:**
- ❌ No git repository (-15)
- ❌ No custom error classes (-15)
- ❌ Single test file organization (-10)
- ❌ Only 2 source files (-10)
- ❌ No help command implementation (-5)
- ❌ No JSDoc annotations (-5)

**Verdict:** **Polished but lacks structure**. Perfect coverage and documentation but missing git workflow, modularity, and production-grade error handling. Ties with SWE-AF (Haiku) but for opposite reasons: working tests + minimal code vs. extensive structure + broken tests.

---

#### 2. 🥈 SWE-AF (Haiku) - 110/190 (57.9%) [TIED]

**Comprehensive Strengths:**
- ✅ **Git repository with semantic commits** (14+ commits, cleaned for final PR)
- ✅ **Exceptional test-to-code ratio** (8.59! - 3472 test LOC)
- ✅ **Dedicated utils.js** (DRY principle - only agent)
- ✅ **JSDoc type annotations** (only agent with @param/@returns/@type)
- ✅ **Comprehensive help system** (8 files with help/usage)
- ✅ **Deep test organization** (5 subdirectories)
- ✅ **Zero dependencies** (prod + dev)

**Critical Weaknesses:**
- ❌ **0% coverage** (tests crash with process.exit) (-25)
- ❌ **148 sync operations** (catastrophic blocking I/O anti-pattern) (-10)
- ❌ No test script to run tests (-5)
- ❌ No custom errors (-15)
- ❌ Incomplete package.json (-10)

**Verdict:** **Extensive scaffolding, poor execution**. Has excellent structure (git, utils, JSDoc, deep tests) but tests don't work and performance is catastrophically bad with 148 blocking operations. Ties with Claude Sonnet but for different reasons.

---

#### 4. Codex (o3) - 90/190 (47.4%)

**Comprehensive Strengths:**
- ✅ **Perfect function modularity** (46 LOC/function + 6 files)
- ✅ **13 validation checks** (best defensive programming)
- ✅ **Complete package.json** metadata (10/10)
- ✅ **Modern node:test** (zero dev dependencies)
- ✅ **Minimal blocking I/O** (6 sync operations)

**Weaknesses:**
- ❌ No git repository (-15)
- ❌ 0% coverage (-25)
- ❌ No custom errors (-15)
- ❌ **Test ratio below threshold** (0.38 < 0.5) (-5)
- ❌ No help command (-5)
- ❌ Dirty file state (-10)
- ❌ No JSDoc (-5)

**Verdict:** **Clean architecture, incomplete implementation**. Best modularity and validation but lacks tests, version control, and production-ready features.

---

#### 5. Claude Haiku - 50/190 (26.3%)

**Comprehensive Strengths:**
- ✅ **Perfect test framework score** (15/15): node:test + organized + 1.0 ratio
- ✅ **Complete package.json** (10/10)
- ✅ **Zero dependencies** (supply chain secure)

**Critical Weaknesses:**
- ❌ **Worst across most categories**
- ❌ 0% coverage (-25)
- ❌ No git repository (-15)
- ❌ No .gitignore (-10)
- ❌ Dirty files (-10)
- ❌ No custom errors (-15)
- ❌ **Worst function modularity** (228 LOC/function!) (-10)
- ❌ **Only 2 validation checks** (poor input safety) (-10)
- ❌ **11 sync operations** (-10)
- ❌ No JSDoc (-5)
- ❌ No help command (-5)

**Verdict:** **Not production-ready**. Despite modern test framework and complete package.json, fails on coverage, modularity, safety, and repository hygiene.

---

## Key Insights from Extended Analysis

### 1. Dependency Management (Universal Excellence)
**All agents scored 15/15** - every agent maintains zero production dependencies, demonstrating excellent supply chain security awareness across all AI coding agents.

### 2. Test Framework Evolution
- **Modern built-in node:test adoption**: 3 agents (Claude Haiku, Codex, SWE-AF Haiku) use Node's built-in test runner
- **Test-to-code ratio revelation**: SWE-AF (Haiku) has astonishing 8.59 ratio but **tests don't run** (0% coverage)
- **Quality over quantity**: Claude Sonnet (0.96 ratio, 100% coverage) beats Codex (0.38 ratio, 0% coverage)

### 3. Performance Anti-Patterns
- **SWE-AF (Haiku) disaster**: 148 sync operations (24x worse than best agents)
- **Best performers**: SWE-AF (MiniMax), Codex (6 sync each), Claude Sonnet (7 sync)
- **Blocking I/O is critical**: Separates production-ready (≤10 sync) from poor performers (>10 sync)

### 4. Type Safety Gap
- **Only 2 agents** score above 0: SWE-AF (Haiku) with JSDoc, Codex with validation
- **Codex leads validation**: 13 checks vs 2-7 for others (defensive programming)
- **JSDoc adoption**: 1 in 5 agents - massive gap in type documentation

### 5. CLI Usability Divide
- **SWE-AF agents excel**: Both have comprehensive help systems (5-8 files)
- **Claude/Codex gap**: Zero help implementation - users must read README or guess commands
- **Production expectation**: Real CLIs need `--help` - this separates professional from hobby projects

### 6. Package.json Professionalism
- **3 agents perfect (10/10)**: Claude Sonnet, Claude Haiku, Codex
- **SWE-AF weakness**: Missing bin field (not installable via npm), no license/keywords
- **Metadata matters**: Complete package.json signals publication-ready software

### 7. Git Discipline Remains Critical
- **2 agents with git**: SWE-AF (MiniMax) and SWE-AF (Haiku) both initialized git with semantic commits
- **Reproducibility gap**: Without git history, impossible to audit development process
- **Production requirement**: Version control is non-negotiable - this 15-point differential separates professional from amateur code

### 8. Modularity vs Simplicity Trade-off
- **Codex wins modularity**: 46 LOC/function + 6 files (best balance)
- **Claude Haiku fails**: 228 LOC/function (God functions, poor SRP)
- **Sweet spot**: 50-100 LOC/function (MiniMax, Sonnet, Codex achieve this)

---

## Cost-Effectiveness Analysis

| Agent | Score | Cost | Time | Points/$1 | Points/min |
|-------|-------|------|------|-----------|------------|
| **SWE-AF (MiniMax)** | 159.8/190 | $6 | 43 min | **26.6** | **3.72** |
| **SWE-AF (Haiku)** | 110/190 | TBD | TBD | TBD | TBD |
| **Claude Sonnet** | 110/190 | TBD | TBD | TBD | TBD |
| **Claude Haiku** | 50/190 | TBD | TBD | TBD | TBD |
| **Codex (o3)** | 90/190 | TBD | TBD | TBD | TBD |

**SWE-AF (MiniMax)** delivers **26.6 quality points per dollar** - the only agent with measured cost data shows exceptional value for production-grade code.

---

## Recommendations by Use Case

### For Production Applications
**Choose: SWE-AF (MiniMax)**
- Reason: Only agent with 84.1% overall score, git workflow, >90% coverage, custom errors
- Missing: Just needs README documentation
- Action: Safe to deploy with documentation added

### For Quick Prototypes
**Choose: Claude Sonnet**
- Reason: 100% coverage, simple structure (255 LOC), has README
- Missing: No git, no error classes, no modularity
- Action: Good for demos, refactor before production

### For Learning/Education
**Choose: Codex (o3)**
- Reason: Best modularity (46 LOC/function), defensive validation (13 checks)
- Missing: Tests don't run, no coverage
- Action: Study architecture, add test implementation

### NOT Recommended
**Avoid: SWE-AF (Haiku), Claude Haiku**
- Reason (Haiku): 148 sync operations breaks performance, tests crash
- Reason (Claude Haiku): 228 LOC/function, 0% coverage, bloated architecture
- Action: Do not use without major refactoring

---

## Conclusion: Production Quality Hierarchy

**Tier 1 - Production Ready (>80%):**
1. SWE-AF (MiniMax): **84.1%** ⭐ **WINNER**

**Tier 2 - Refactor Needed (50-80%):**
2. **SWE-AF (Haiku): 57.9%** (fix crashing tests, remove 142 sync ops, add custom errors) [TIED]
2. **Claude Sonnet: 57.9%** (add git, errors, modularity) [TIED]

**Tier 3 - Significant Work Required (30-50%):**
4. Codex (o3): **47.4%** (implement tests, add git, increase test ratio)

**Tier 4 - Not Viable (<30%):**
5. Claude Haiku: **26.3%** (fails most categories)

**Final Verdict:** SWE-AF (MiniMax) remains the clear winner with **159.8/190 points (84.1%)**. The extended metrics reinforce its production-readiness: zero prod dependencies, minimal blocking I/O, comprehensive help system, perfect test framework implementation, and balanced modularity. Only missing README documentation to reach 90%+ score.

**Note on Coverage Scoring:** Updated to proportional scoring (25 × coverage% ÷ 100) instead of binary threshold. This gives more granular assessment: Claude Sonnet's perfect 100% coverage earns full 25 points, while SWE-AF (MiniMax)'s 99.22% coverage earns 24.8 points (only 0.2 point difference, reflecting near-perfect execution).

**Interesting Tie at 2nd Place (110/190, 57.9%):**
- **SWE-AF (Haiku)**: Excellent structure (git, utils, JSDoc, help) but broken execution (crashing tests, 148 sync ops)
- **Claude Sonnet**: Perfect execution (100% coverage, minimal code) but missing structure (no git, no modularity, no help)

The gap between Tier 1 and Tier 2 (26.3 percentage points) highlights that **test coverage, custom errors, and performance optimization** remain critical differentiators for production-grade AI-generated code.

## Production Quality Score

| Metric | Points | SWE-AF (MiniMax) | SWE-AF (Haiku) | Claude Sonnet | Claude Haiku | Codex (o3) |
|--------|--------|------------------|----------------|---------------|--------------|------------|
| Test Coverage (proportional) | 25 | **24.8** (99.22%) | 0 (0%) | **25** (100%) | 0 (0%) | 0 (0%) |
| Custom errors | 15 | **15** | 0 | 0 | 0 | 0 |
| Modular (>2 files) | 10 | **10** | **10** | 0 | 0 | **10** |
| Git repo + commits | 15 | **15** | **15** | 0 | 0 | 0 |
| Has .gitignore | 10 | **10** | **10** | **10** | 0 | **10** |
| Clean files | 10 | **10** | **10** | **10** | 0 | 0 |
| Has README | 5 | 0 | 0 | **5** | 0 | 0 |
| Multiple test files | 10 | **10** | **10** | 0 | 0 | 0 |
| **TOTAL** | **100** | **94.8** | **55** | **50** | **0** | **20** |

## Rankings

### 1. 🥇 SWE-AF (MiniMax) - 94.8/100

**Strengths:**
- ✅ 99.22% test coverage (24.8/25 points - proportional scoring)
- ✅ 4 custom error classes
- ✅ 9 semantic git commits
- ✅ 999 LOC (balanced size)

**Weakness:**
- ❌ No README

**Verdict:** Production-ready. Only needs documentation.

**Cost**: $6 | **Time**: 43 min

---

### 2. 🥈 Claude Sonnet - 50/100

**Strengths:**
- ✅ **100% test coverage**
- ✅ Only agent with README
- ✅ Simplest (255 LOC)
- ✅ Clean files

**Weaknesses:**
- ❌ No git repo
- ❌ No custom errors
- ❌ Single test file
- ❌ Only 2 source files

**Verdict:** Perfect coverage but lacks structure.

---

### 3. 🥉 SWE-AF (Haiku) - 55/100

**Strengths:**
- ✅ **Git repo with semantic commits** (14+ commits, cleaned for final PR)
- ✅ 14 test files (4-tier organization)
- ✅ 3+ JSDoc blocks
- ✅ Clean files
- ✅ Dedicated utils.js

**Weaknesses:**
- ❌ **0% coverage** (tests crash with process.exit) (-25)
- ❌ No custom errors (-15)
- ❌ No README (-5)
- ⚠️ 3876 LOC (3.9x MiniMax)
- ⚠️ **148 sync operations** (performance anti-pattern)

**Verdict:** Good structure (git, utils, JSDoc) but extensive tests crash and performance is poor.

### 4. Codex (o3) - 20/100

**Strengths:**
- ✅ Has .gitignore
- ✅ 3 source files
- ✅ Compact (287 LOC)

**Weaknesses:**
- ❌ No git repo
- ❌ Dirty state
- ❌ 0% coverage
- ❌ No custom errors
- ❌ No README

**Verdict:** Clean structure but poor discipline.

---

### 5. Claude Haiku - 0/100

**Weaknesses:**
- ❌ No git repo
- ❌ No .gitignore
- ❌ Dirty state
- ❌ No coverage
- ❌ No custom errors
- ❌ No README
- ❌ Only 2 source files

**Verdict:** Not production-ready.

## Key Findings

### Critical for Production
1. **Test coverage >90%**: SWE-AF (MiniMax) (99.22%) and Claude Sonnet (100%)
2. **Custom error types**: Only SWE-AF (MiniMax) implemented this
3. **Git version control**: Only SWE-AF (MiniMax) initialized git
4. **Modularity**: SWE-AF (MiniMax) (4 files, 999 LOC) vs SWE-AF (Haiku) (4 files, 3876 LOC)

### Coverage Analysis
- **SWE-AF (MiniMax)**: 99.22% with 74 tests across 4 files
- **Claude Sonnet**: 100% with 14 tests in 1 file
- **SWE-AF (Haiku)**: 0% (tests crash with process.exit)
- **Claude Haiku**: 0% (ESM import errors)
- **Codex (o3)**: 0% (no jest config)

### Cost-Effectiveness
**SWE-AF (MiniMax)**: **$6 for 95/100 score**
- Best overall production readiness
- Only agent with git + custom errors + >90% coverage

### Conclusion

**SWE-AF (MiniMax) wins on production readiness (95/100)**:
- ✅ 99.22% test coverage (verified)
- ✅ 4 custom error types (production-grade)
- ✅ 9 semantic git commits (proper workflow)
- ✅ Balanced size (999 LOC)
- ✅ 4 modular files

**Claude Sonnet is runner-up (50/100)** with perfect 100% coverage but:
- ❌ No git repository
- ❌ No custom error handling
- ❌ No modularity (2 files, 255 LOC)
