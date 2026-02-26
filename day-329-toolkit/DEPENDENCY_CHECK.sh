#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════════"
echo "  Day 329 Dependency Verification & Installation"
echo "═══════════════════════════════════════════════════════════"

FAILED=0

# ==================================================================
# SYSTEM TOOLS
# ==================================================================
echo ""
echo "📦 SYSTEM TOOLS"
echo "──────────────────────────────────────────────────────────────"

# Python 3
if command -v python3 &> /dev/null; then
    VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✅ python3 (version $VERSION)"
else
    echo "❌ python3 NOT FOUND"
    FAILED=$((FAILED + 1))
fi

# gh CLI
if command -v gh &> /dev/null; then
    VERSION=$(gh --version | head -1)
    echo "✅ gh CLI ($VERSION)"
else
    echo "❌ gh CLI NOT FOUND"
    FAILED=$((FAILED + 1))
fi

# git
if command -v git &> /dev/null; then
    VERSION=$(git --version | awk '{print $3}')
    echo "✅ git (version $VERSION)"
else
    echo "❌ git NOT FOUND"
    FAILED=$((FAILED + 1))
fi

# ==================================================================
# PYTHON DEPENDENCIES
# ==================================================================
echo ""
echo "🐍 PYTHON DEPENDENCIES"
echo "──────────────────────────────────────────────────────────────"

# Check and install each dependency
install_if_missing() {
    local module=$1
    local package=$2
    
    if python3 -c "import $module" 2>/dev/null; then
        echo "✅ $module"
    else
        echo "⚠️  $module not found, installing..."
        pip3 install $package --quiet
        if python3 -c "import $module" 2>/dev/null; then
            echo "✅ $module (installed)"
        else
            echo "❌ $module FAILED TO INSTALL"
            FAILED=$((FAILED + 1))
        fi
    fi
}

install_if_missing "requests" "requests"
install_if_missing "github" "PyGithub"
install_if_missing "pandas" "pandas"
install_if_missing "json" "json"  # Built-in, always available

# ==================================================================
# ENVIRONMENT VARIABLES
# ==================================================================
echo ""
echo "🔐 ENVIRONMENT VARIABLES"
echo "──────────────────────────────────────────────────────────────"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN not set (needed for Challenge #4)"
    echo "   Set with: export GITHUB_TOKEN=<your_token>"
else
    TOKEN_PREVIEW=$(echo $GITHUB_TOKEN | head -c 15)
    echo "✅ GITHUB_TOKEN set ($TOKEN_PREVIEW...)"
fi

# ==================================================================
# FILES & DIRECTORIES
# ==================================================================
echo ""
echo "📁 FILES & DIRECTORIES"
echo "──────────────────────────────────────────────────────────────"

check_file() {
    local path=$1
    local name=$2
    
    if [ -f "$path" ]; then
        SIZE=$(stat -f%z "$path" 2>/dev/null || stat -c%s "$path" 2>/dev/null || echo "?")
        echo "✅ $name ($SIZE bytes)"
    else
        echo "❌ $name NOT FOUND at $path"
        FAILED=$((FAILED + 1))
    fi
}

check_file "/home/computeruse/village-event-log/docs/events.json" "village-event-log"
check_file "/home/computeruse/village-challenges/challenges/challenge-5-claude-haiku-4.5/claude-haiku-4.5-village-chronicle.md" "Challenge #5 file"
check_file "/tmp/challenge6_query_engine.py" "Challenge #6 tool"
check_file "$HOME/village-challenges/day-329-toolkit/challenge4-audit-optimized.py" "Challenge #4 script"

# ==================================================================
# EXECUTABLE TESTS
# ==================================================================
echo ""
echo "⚙️  EXECUTABLE TESTS"
echo "──────────────────────────────────────────────────────────────"

# Test gh CLI auth
echo -n "Testing gh CLI auth... "
if gh auth status &>/dev/null; then
    echo "✅"
else
    echo "❌ (run 'gh auth login')"
    FAILED=$((FAILED + 1))
fi

# Test Python imports
echo -n "Testing Python imports... "
if python3 -c "import requests, github, pandas, json; print('OK')" 2>/dev/null | grep -q "OK"; then
    echo "✅"
else
    echo "❌"
    FAILED=$((FAILED + 1))
fi

# Test Challenge #6 syntax
echo -n "Testing Challenge #6 tool syntax... "
if python3 -m py_compile /tmp/challenge6_query_engine.py 2>/dev/null; then
    echo "✅"
else
    echo "❌"
    FAILED=$((FAILED + 1))
fi

# Test Challenge #4 script syntax
echo -n "Testing Challenge #4 script syntax... "
if python3 -m py_compile "$HOME/village-challenges/day-329-toolkit/challenge4-audit-optimized.py" 2>/dev/null; then
    echo "✅"
else
    echo "❌"
    FAILED=$((FAILED + 1))
fi

# ==================================================================
# SUMMARY
# ==================================================================
echo ""
echo "═══════════════════════════════════════════════════════════"

if [ $FAILED -eq 0 ]; then
    echo "✅ ALL SYSTEMS GO FOR DAY 329"
    echo "═══════════════════════════════════════════════════════════"
    exit 0
else
    echo "❌ $FAILED ISSUES DETECTED"
    echo "═══════════════════════════════════════════════════════════"
    exit 1
fi
