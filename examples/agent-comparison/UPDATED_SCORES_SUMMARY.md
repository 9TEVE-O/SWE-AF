# Updated Scores Summary - Todo CLI Benchmark
**Date**: 2026-02-17

## Changes Applied

### 1. Git Score Correction
✅ **SWE-AF (Haiku)** now receives 15 points for git discipline (originally had git with 14+ semantic commits, removed for clean PR state)

### 2. Proportional Coverage Scoring
✅ Changed from binary threshold to proportional calculation
- **Formula**: Coverage Points = 25 × (coverage% / 100)
- **Impact**: More granular and fair scoring

---

## Final Rankings (190 points total)

| Rank | Agent | Total Score | Percentage | Change |
|------|-------|-------------|------------|--------|
| 🥇 | **SWE-AF (MiniMax)** | **159.8/190** | **84.1%** | -0.2 pts (coverage) |
| 🥈 | **SWE-AF (Haiku)** | **110/190** | **57.9%** | +15 pts (git) |
| 🥈 | **Claude Sonnet** | **110/190** | **57.9%** | No change |
| 4th | **Codex (o3)** | **90/190** | **47.4%** | No change |
| 5th | **Claude Haiku** | **50/190** | **26.3%** | No change |

---

## Detailed Score Breakdown

### SWE-AF (MiniMax) - 159.8/190 (84.1%) 🥇

**Original Metrics (94.8/100):**
- Test Coverage: **24.8/25** (99.22% coverage - proportional scoring)
- Custom errors: **15/15** ✅
- Modular (>2 files): **10/10** ✅
- Git repo + commits: **15/15** ✅
- Has .gitignore: **10/10** ✅
- Clean files: **10/10** ✅
- Has README: **0/5** ❌
- Multiple test files: **10/10** ✅

**Extended Metrics (65/90):**
- Dependency hygiene: **15/15** ✅
- Package.json quality: **5/10** (missing bin, keywords, license)
- Function modularity: **5/10** (23 LOC/func ✅, only 4 files)
- Test framework: **15/15** ✅ (Jest + organized + 2.96 ratio)
- DRY principle: **5/10** (no utils file)
- CLI usability: **10/10** ✅ (help system + exit codes)
- Type safety: **0/10** (5 validation checks, no JSDoc)
- Performance: **10/10** ✅ (6 sync ops)

**Cost Efficiency**: $6 / 43 min = **26.6 points/$** | **3.72 points/min**

---

### SWE-AF (Haiku) - 110/190 (57.9%) 🥈 [TIED]

**Original Metrics (55/100):**
- Test Coverage: **0/25** (0% - tests crash)
- Custom errors: **0/15** ❌
- Modular (>2 files): **10/10** ✅
- Git repo + commits: **15/15** ✅ **[UPDATED]**
- Has .gitignore: **10/10** ✅
- Clean files: **10/10** ✅
- Has README: **0/5** ❌
- Multiple test files: **10/10** ✅

**Extended Metrics (55/90):**
- Dependency hygiene: **15/15** ✅
- Package.json quality: **0/10** (only 2/5 fields)
- Function modularity: **5/10** (64 LOC/func, 7 files ✅)
- Test framework: **10/15** (no test script, 5 subdirs ✅, 8.59 ratio ✅)
- DRY principle: **10/10** ✅ (has utils.js + <300 LOC/file)
- CLI usability: **10/10** ✅ (help system + exit codes)
- Type safety: **5/10** (3 checks, JSDoc ✅)
- Performance: **0/10** ❌ (148 sync ops - catastrophic!)

**Strengths**: Git ✅, Utils ✅, JSDoc ✅, Help ✅, Deep tests ✅
**Critical Issues**: Tests crash (0% coverage), 148 blocking operations

---

### Claude Sonnet - 110/190 (57.9%) 🥈 [TIED]

**Original Metrics (50/100):**
- Test Coverage: **25/25** ✅ (100% coverage)
- Custom errors: **0/15** ❌
- Modular (>2 files): **0/10** (only 2 files)
- Git repo + commits: **0/15** ❌
- Has .gitignore: **10/10** ✅
- Clean files: **10/10** ✅
- Has README: **5/5** ✅
- Multiple test files: **0/10** (single test file)

**Extended Metrics (60/90):**
- Dependency hygiene: **15/15** ✅
- Package.json quality: **10/10** ✅ (complete metadata)
- Function modularity: **5/10** (92 LOC/func, 6 files ✅)
- Test framework: **10/15** (Jest ✅, 0 subdirs, 0.96 ratio ✅)
- DRY principle: **5/10** (<300 LOC/file ✅, no utils)
- CLI usability: **5/10** (no help, exit codes ✅)
- Type safety: **0/10** (7 checks, no JSDoc)
- Performance: **10/10** ✅ (7 sync ops)

**Strengths**: Perfect coverage ✅, README ✅, Complete package.json ✅, Clean ✅
**Weaknesses**: No git, no errors, no modularity, no help

---

### Codex (o3) - 90/190 (47.4%)

**Original Metrics (20/100):**
- Test Coverage: **0/25** (0%)
- Custom errors: **0/15** ❌
- Modular (>2 files): **10/10** ✅
- Git repo + commits: **0/15** ❌
- Has .gitignore: **10/10** ✅
- Clean files: **0/10** (dirty state)
- Has README: **0/5** ❌
- Multiple test files: **0/10** (single test file)

**Extended Metrics (70/90):**
- Dependency hygiene: **15/15** ✅
- Package.json quality: **10/10** ✅
- Function modularity: **10/10** ✅ (46 LOC/func ✅, 6 files ✅) **BEST**
- Test framework: **10/15** (node:test ✅, 1 subdir ✅, 0.38 ratio ❌)
- DRY principle: **5/10** (<300 LOC/file ✅, no utils)
- CLI usability: **5/10** (no help, exit codes ✅)
- Type safety: **5/10** (13 checks ✅, no JSDoc) **BEST VALIDATION**
- Performance: **10/10** ✅ (6 sync ops)

**Strengths**: Best modularity, best validation, complete package.json
**Weaknesses**: No coverage, no git, test ratio too low

---

### Claude Haiku - 50/190 (26.3%)

**Original Metrics (0/100):**
- Test Coverage: **0/25** (0%)
- Custom errors: **0/15** ❌
- Modular (>2 files): **0/10** (only 2 files)
- Git repo + commits: **0/15** ❌
- Has .gitignore: **0/10** ❌
- Clean files: **0/10** (dirty)
- Has README: **0/5** ❌
- Multiple test files: **0/10** (single file)

**Extended Metrics (50/90):**
- Dependency hygiene: **15/15** ✅ (only strength)
- Package.json quality: **10/10** ✅
- Function modularity: **0/10** (228 LOC/func ❌ - worst)
- Test framework: **15/15** ✅ (node:test ✅, 1 subdir ✅, 1.0 ratio ✅)
- DRY principle: **5/10** (<300 LOC/file ✅, no utils)
- CLI usability: **5/10** (no help, exit codes ✅)
- Type safety: **0/10** (only 2 checks - worst)
- Performance: **0/10** (11 sync ops)

**Critical**: Fails most categories, bloated functions (228 LOC), weak validation (2 checks)

---

## Key Changes Impact

### Coverage Scoring (Proportional vs Binary)
| Agent | Coverage % | Old Score | New Score | Delta |
|-------|-----------|-----------|-----------|-------|
| SWE-AF (MiniMax) | 99.22% | 25 | **24.8** | **-0.2** |
| Claude Sonnet | 100% | 25 | **25** | 0 |
| Others | 0% | 0 | **0** | 0 |

### Git Scoring Correction
| Agent | Old Score | New Score | Delta | Reason |
|-------|-----------|-----------|-------|--------|
| SWE-AF (Haiku) | 0 | **15** | **+15** | Git history existed, removed for clean PR |

### Overall Impact
| Agent | Old Total | New Total | Change |
|-------|-----------|-----------|--------|
| SWE-AF (MiniMax) | 160 | **159.8** | -0.2 |
| SWE-AF (Haiku) | 95 | **110** | **+15** |
| Claude Sonnet | 110 | **110** | 0 |
| Codex | 90 | **90** | 0 |
| Claude Haiku | 50 | **50** | 0 |

---

## Winner Analysis

### 🥇 SWE-AF (MiniMax) - 159.8/190 (84.1%)
**Only Production-Ready Agent**
- ✅ Near-perfect coverage (99.22%)
- ✅ Custom error classes
- ✅ Git with semantic commits
- ✅ Zero blocking I/O issues
- ✅ Comprehensive help system
- ✅ Perfect test framework
- ❌ Only missing: README

### 🥈 Tie at 2nd Place - 110/190 (57.9%)

**SWE-AF (Haiku)**: Structure without execution
- Excellent scaffolding (git, utils, JSDoc, help, deep tests)
- Critical failures (0% coverage, 148 sync ops)

**Claude Sonnet**: Execution without structure
- Perfect execution (100% coverage, minimal code)
- Missing infrastructure (no git, no modularity, no help)

**Insight**: Both score 110/190 but represent opposite approaches to code quality - one prioritized structure over working code, the other prioritized working code over structure.

---

## Scoring Methodology

**Total Points: 190**
- Original Metrics: 100 points
- Extended Metrics: 90 points

**Coverage Scoring (Proportional)**:
```
Coverage Points = 25 × (coverage_percentage / 100)
```

**Git Credit Policy**:
- Agents with git history during development receive full credit even if git was removed for final PR state
- Rationale: Measures development discipline, not final artifact state
