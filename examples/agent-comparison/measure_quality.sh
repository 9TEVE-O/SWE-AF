#!/bin/bash

AGENTS=("swe-af" "swe-af-minimax/todo-app-benchmark" "claude-code-sonnet" "claude-code-haiku" "codex")
BASE_DIR="/Users/santoshkumarradha/Documents/agentfield/code/int-agentfield-examples/af-swe/examples/agent-comparison"

for agent in "${AGENTS[@]}"; do
  echo "=========================================="
  echo "=== $agent ==="
  echo "=========================================="

  cd "$BASE_DIR/$agent" || continue

  # Dependency count
  if [ -f "package.json" ]; then
    prod_deps=$(cat package.json | jq '.dependencies | length // 0' 2>/dev/null)
    dev_deps=$(cat package.json | jq '.devDependencies | length // 0' 2>/dev/null)
    has_bin=$(cat package.json | jq 'has("bin")' 2>/dev/null)
    has_test=$(cat package.json | jq '.scripts.test != null' 2>/dev/null)
    has_desc=$(cat package.json | jq '.description != null' 2>/dev/null)
    has_keywords=$(cat package.json | jq '.keywords != null' 2>/dev/null)
    has_license=$(cat package.json | jq '.license != null' 2>/dev/null)
    test_cmd=$(cat package.json | jq -r '.scripts.test // "none"' 2>/dev/null)

    echo "Production dependencies: $prod_deps"
    echo "Dev dependencies: $dev_deps"
    echo "Has bin field: $has_bin"
    echo "Has test script: $has_test"
    echo "Has description: $has_desc"
    echo "Has keywords: $has_keywords"
    echo "Has license: $has_license"
    echo "Test command: $test_cmd"
  else
    echo "No package.json found"
  fi

  # Function count (excluding node_modules)
  func_count=$(find . -name "*.js" -not -path "*/node_modules/*" -not -path "*/test/*" -not -path "*/tests/*" -exec grep -h "^function \|^const.*= .*function\|^const.*= (.*) =>" {} \; 2>/dev/null | wc -l | tr -d ' ')
  echo "Function definitions: $func_count"

  # Validation/guard clause count
  validation_count=$(find . -name "*.js" -not -path "*/node_modules/*" -not -path "*/test/*" -not -path "*/tests/*" -exec grep -h "if (!.*)" {} \; 2>/dev/null | wc -l | tr -d ' ')
  echo "Validation checks (!): $validation_count"

  # Sync file operations
  sync_ops=$(find . -name "*.js" -not -path "*/node_modules/*" -exec grep -h "Sync(" {} \; 2>/dev/null | wc -l | tr -d ' ')
  echo "Sync operations: $sync_ops"

  # Help/usage implementation
  has_help=$(find . -name "*.js" -not -path "*/node_modules/*" -exec grep -l "help\|usage" {} \; 2>/dev/null | wc -l | tr -d ' ')
  echo "Files with help/usage: $has_help"

  # Exit codes
  exit_codes=$(find . -name "*.js" -not -path "*/node_modules/*" -exec grep -h "process.exit" {} \; 2>/dev/null | wc -l | tr -d ' ')
  echo "process.exit calls: $exit_codes"

  # Test subdirectories
  if [ -d "tests" ] || [ -d "test" ]; then
    test_dirs=$(find tests test -type d 2>/dev/null | wc -l | tr -d ' ')
    echo "Test subdirectories: $test_dirs"
  else
    echo "Test subdirectories: 0"
  fi

  # Source files (excluding tests and node_modules)
  src_files=$(find . -name "*.js" -not -path "*/node_modules/*" -not -path "*/test/*" -not -path "*/tests/*" 2>/dev/null | wc -l | tr -d ' ')
  echo "Source files: $src_files"

  # Average LOC per source file
  if [ "$src_files" -gt 0 ]; then
    total_loc=$(find . -name "*.js" -not -path "*/node_modules/*" -not -path "*/test/*" -not -path "*/tests/*" -exec wc -l {} \; 2>/dev/null | awk '{sum+=$1} END {print sum}')
    avg_loc=$((total_loc / src_files))
    echo "Avg LOC per file: $avg_loc"
  fi

  echo ""
done
