# issue-13-documentation-consolidation: Consolidate Documentation into docs/ Directory

## Description
Create a structured `docs/` directory and consolidate 5 scattered markdown files from the repository root with consistent lowercase/kebab-case naming. This eliminates root directory clutter and establishes a single source of truth for technical documentation.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section "Component 13: Documentation Consolidation" for:
- File move operations (VALIDATION.md → docs/validation.md, etc.)
- Internal markdown link verification strategy (`grep -r "\[.*\](.*\.md)"`)
- docs/README.md content template (documentation index structure)
- Naming transformation rules (UPPERCASE → lowercase, underscores → kebab-case)

## Interface Contracts
- **Implements**: File system move operations with renaming
  ```bash
  mkdir -p docs
  mv VALIDATION.md docs/validation.md
  mv PERFORMANCE.md docs/performance.md
  mv IMPLEMENTATION_NOTES.md docs/implementation-notes.md
  mv INTEGRATION_VERIFICATION_RESULTS.md docs/integration-verification.md
  mv TEST_VERIFICATION_EVIDENCE.md docs/test-verification.md
  ```
- **Exports**: Consolidated docs/ directory with 6 markdown files (5 moved + docs/README.md)
- **Consumes**: README.md existence validation (dependency: issue-12-readme-creation)
- **Consumed by**: issue-14-final-validation (verifies AC12-AC13)

## Isolation Context
- **Available**: README.md in root (from issue-12-readme-creation)
- **NOT available**: No sibling issue code dependencies
- **Source of truth**: Architecture document Component 13 for file operations and verification strategy

## Files
- **Create**: `docs/README.md` (documentation index)
- **Modify**: None (move operations only)

## Dependencies
- issue-12-readme-creation (provides: README.md must exist before verifying "only README in root")

## Provides
- Structured docs/ directory with consolidated documentation
- docs/README.md index file
- Clean root directory with only README.md

## Acceptance Criteria
- [ ] `test -d docs` exits with code 0 (docs/ directory exists)
- [ ] `find docs -name '*.md' | wc -l` outputs 6 (5 moved files plus docs/README.md)
- [ ] `ls *.md 2>/dev/null | grep -v 'README.md' | wc -l` outputs 0 (no loose markdown in root except README)
- [ ] `test -f docs/validation.md` exits with code 0
- [ ] `test -f docs/performance.md` exits with code 0
- [ ] `test -f docs/implementation-notes.md` exits with code 0
- [ ] `test -f docs/integration-verification.md` exits with code 0
- [ ] `test -f docs/test-verification.md` exits with code 0
- [ ] `test -f docs/README.md` exits with code 0

## Testing Strategy

### Test Files
- No test files (verification via filesystem commands only)

### Test Categories
- **File system verification**: Execute all AC commands to verify docs/ structure
- **Edge cases**: Check for internal markdown links using `grep -r "\[.*\](.*\.md)" docs/*.md`
- **Root cleanup**: Verify no loose markdown files remain in root (except README.md)

### Run Command
```bash
# Execute all acceptance criteria commands in sequence
test -d docs && echo "PASS: docs/ exists"
find docs -name '*.md' | wc -l  # Expected: 6
ls *.md 2>/dev/null | grep -v 'README.md' | wc -l  # Expected: 0
```

## Verification Commands
- **Mkdir**: `mkdir -p docs`
- **Moves**: `mv VALIDATION.md docs/validation.md` (repeat for all 5 files)
- **Link check**: `grep -r "\[.*\](.*\.md)" docs/*.md` (update if found)
- **Final check**: `find docs -name '*.md' | wc -l` outputs 6
