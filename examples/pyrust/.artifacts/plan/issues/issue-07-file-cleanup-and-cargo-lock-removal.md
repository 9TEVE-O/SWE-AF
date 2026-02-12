# issue-07-file-cleanup-and-cargo-lock-removal: Delete Backup Files, Artifacts, and Untrack Cargo.lock

## Description
Remove all backup/temporary files, build artifacts, Claude output files, and untrack Cargo.lock from git to achieve production-quality repository cleanliness. This cleanup eliminates 11+ polluting files across src/ and root directories.

## Architecture Reference
Read `/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/example-pyrust/.artifacts/plan/architecture.md` Section "Component 9: File Deletion - Backup/Temp/Artifact Cleanup" for:
- Complete file deletion list (8 root artifacts, 3 src backups)
- `git rm --cached Cargo.lock` command for untracking
- Verification strategy using find/ls commands
- Error handling for missing files (rm -f pattern)

## Interface Contracts
- **Deletion Operations**: `rm -f <file>` for each artifact (force flag suppresses missing file errors)
- **Git Untrack**: `git rm --cached Cargo.lock` (removes from tracking, preserves local file)
- **Verification**: `find src -name "*.backup" -o -name "*.tmp" -o -name "*.bak" | wc -l` returns 0

## Isolation Context
- Available: All Phase 1 components execute in parallel
- NOT available: N/A (this is a pure file system operation)
- Source of truth: Architecture Component 9 for complete file list

## Files
- **Delete (root)**: bench_output.log, test_output.log, test_output.txt, test_output_fixed.txt, dhat-heap.json, Cargo.toml.bak, .claude_output_a1bf2ba40715.json, .claude_output_bdf6d7a0d9e6.json
- **Delete (src/)**: bytecode.rs.backup, bytecode.rs.tmp, vm.rs.backup
- **Git untrack**: Cargo.lock (via `git rm --cached`)

## Dependencies
None (Phase 1 component, fully independent)

## Provides
- Clean src/ directory with no backup/temp files (satisfies PRD AC6)
- Clean root directory with no artifact files (satisfies PRD AC7)
- Cargo.lock removed from git tracking per library best practices

## Acceptance Criteria
- [ ] `find src -name "*.backup" -o -name "*.tmp" -o -name "*.bak" | wc -l` outputs 0
- [ ] `ls *.log *.txt dhat-heap.json Cargo.toml.bak .claude_output_*.json 2>/dev/null | wc -l` outputs 0
- [ ] `git ls-files Cargo.lock 2>/dev/null | wc -l` outputs 0 (Cargo.lock no longer tracked)

## Testing Strategy

### Test Files
N/A (file deletion operations verified via shell commands)

### Test Categories
- **File System Verification**: Use find/ls to confirm all backup/temp files removed
- **Git Tracking Verification**: Use `git ls-files` to confirm Cargo.lock untracked
- **Idempotency Check**: Re-run deletion commands should succeed (rm -f handles missing files)

### Run Command
```bash
# Execute deletions
rm -f bench_output.log test_output.log test_output.txt test_output_fixed.txt dhat-heap.json Cargo.toml.bak .claude_output_a1bf2ba40715.json .claude_output_bdf6d7a0d9e6.json
rm -f src/bytecode.rs.backup src/bytecode.rs.tmp src/vm.rs.backup
git rm --cached Cargo.lock

# Verify acceptance criteria
find src -name "*.backup" -o -name "*.tmp" -o -name "*.bak" | wc -l
ls *.log *.txt dhat-heap.json Cargo.toml.bak .claude_output_*.json 2>/dev/null | wc -l
git ls-files Cargo.lock 2>/dev/null | wc -l
```

## Verification Commands
- **AC Check 1**: `find src -name "*.backup" -o -name "*.tmp" -o -name "*.bak" | wc -l` (expect: 0)
- **AC Check 2**: `ls *.log *.txt dhat-heap.json Cargo.toml.bak .claude_output_*.json 2>/dev/null | wc -l` (expect: 0)
- **AC Check 3**: `git ls-files Cargo.lock 2>/dev/null | wc -l` (expect: 0)
