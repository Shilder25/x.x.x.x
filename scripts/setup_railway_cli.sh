#!/bin/bash
# Railway CLI setup script for Replit
# This installs Railway CLI and authenticates for remote log access and command execution

set -e

echo "=========================================="
echo "Railway CLI Setup for TradingAgents"
echo "=========================================="

# Check if Railway CLI is already installed
if command -v railway &> /dev/null; then
    echo "✓ Railway CLI already installed: $(railway --version)"
else
    echo "[1/3] Installing Railway CLI..."
    npm install -g @railway/cli
    echo "✓ Railway CLI installed successfully"
fi

# Check for Railway token
if [ -z "$RAILWAY_TOKEN" ]; then
    echo ""
    echo "⚠️  WARNING: RAILWAY_TOKEN environment variable not set"
    echo ""
    echo "To authenticate Railway CLI, you need to:"
    echo "1. Go to https://railway.app/account/tokens"
    echo "2. Create a new token (Project or Account token)"
    echo "3. Add it to Replit Secrets as RAILWAY_TOKEN"
    echo ""
    echo "Then re-run this script."
    exit 1
fi

echo "[2/3] Authenticating with Railway..."
# Export token for railway commands
export RAILWAY_TOKEN

# Verify authentication
if railway whoami &> /dev/null; then
    echo "✓ Authenticated as: $(railway whoami)"
else
    echo "✗ Authentication failed. Check your RAILWAY_TOKEN"
    exit 1
fi

echo "[3/3] Linking to Railway project..."
# Link to project (you may need to adjust project ID)
# Run 'railway status' to verify connection
if railway status &> /dev/null; then
    echo "✓ Connected to Railway project"
    railway status
else
    echo "⚠️  Not linked to a Railway project yet"
    echo "Run: railway link"
    echo "Then select your TradingAgents project"
fi

echo ""
echo "=========================================="
echo "✓ Railway CLI Setup Complete!"
echo "=========================================="
echo ""
echo "Available commands:"
echo "  ./scripts/tail_backend_logs.sh  - Stream Railway logs in real-time"
echo "  ./scripts/run_remote_command.sh - Execute commands on Railway"
echo "  railway status                  - Check deployment status"
echo "  railway logs                    - View recent logs"
echo ""
