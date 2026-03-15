#!/bin/bash
# Install git hooks for OneEmployeeOrg
# Run this after cloning the repository

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_DIR="$SCRIPT_DIR/.git/hooks"

echo "Installing git hooks..."

# Ensure .git/hooks directory exists
mkdir -p "$HOOKS_DIR"

# Create pre-commit hook
cat > "$HOOKS_DIR/pre-commit" << 'HOOK'
#!/bin/bash
# pre-commit hook for OneEmployeeOrg
# Runs linting and tests on staged Python files
#
# To bypass this hook: git commit --no-verify

set -e

echo "Running pre-commit checks..."

# Get staged Python files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM "*.py" 2>/dev/null || true)

if [ -z "$STAGED_FILES" ]; then
    echo "No staged Python files to check."
    exit 0
fi

# Filter to files that exist (skip deleted files)
EXISTING_FILES=""
for file in $STAGED_FILES; do
    if [ -f "$file" ]; then
        EXISTING_FILES="$EXISTING_FILES $file"
    fi
done

if [ -z "$EXISTING_FILES" ]; then
    echo "No existing staged Python files to check."
    exit 0
fi

echo "Checking files:$EXISTING_FILES"

# Check for required tools
check_tool() {
    if ! command -v "$1" &> /dev/null; then
        echo "Error: $1 is not installed. Run: pip install $2"
        exit 1
    fi
}

check_tool "ruff" "ruff"
check_tool "black" "black"
check_tool "pytest" "pytest"

# Run ruff
echo ""
echo "Running ruff check..."
ruff check $EXISTING_FILES

# Run black check
echo ""
echo "Running black --check..."
black --check $EXISTING_FILES

# Run pytest on staged test files only
TEST_FILES=""
for file in $EXISTING_FILES; do
    if [[ "$file" == tests/* ]] || [[ "$file" == test_*.py ]] || [[ "$file" == *_test.py ]]; then
        TEST_FILES="$TEST_FILES $file"
    fi
done

if [ -n "$TEST_FILES" ]; then
    echo ""
    echo "Running pytest on staged test files..."
    pytest $TEST_FILES -v --tb=short
else
    echo ""
    echo "No staged test files to run."
fi

echo ""
echo "All checks passed!"
exit 0
HOOK

# Make executable
chmod +x "$HOOKS_DIR/pre-commit"

echo "✓ pre-commit hook installed"
echo ""
echo "Hooks are now active. To bypass: git commit --no-verify"
