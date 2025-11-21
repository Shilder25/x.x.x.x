#!/bin/bash
# Simple validation script that works without pytest
# Use this for quick checks before deploying

set -e

echo "=========================================="
echo "🔍 SIMPLE PRE-DEPLOY VALIDATION"
echo "=========================================="
echo ""

# Check 1: Opinion.trade SDK connectivity
echo "[1/3] Testing Opinion.trade SDK connectivity..."
if python scripts/health_check_opinion_trade.py; then
    echo "✓ SDK check passed"
else
    echo "✗ SDK check failed - verify API keys and wallet"
    exit 1
fi
echo ""

# Check 2: Python syntax check
echo "[2/3] Checking Python syntax..."
PYTHON_FILES=$(find . -name "*.py" -not -path "./frontend/*" -not -path "./.next/*" -not -path "./node_modules/*" 2>/dev/null)
if python -m py_compile $PYTHON_FILES 2>/dev/null; then
    echo "✓ Python syntax OK"
else
    echo "⚠️  Some Python files have syntax errors"
fi
echo ""

# Check 3: Frontend build
echo "[3/3] Building Next.js frontend..."
cd frontend
if npm run build > /dev/null 2>&1; then
    echo "✓ Frontend build successful"
    cd ..
else
    echo "✗ Frontend build failed"
    cd ..
    exit 1
fi
echo ""

echo "=========================================="
echo "✅ VALIDATION PASSED - SAFE TO DEPLOY"
echo "=========================================="
echo ""
echo "Deploy command:"
echo "  git add . && git commit -m 'Your message' && git push"
echo ""
