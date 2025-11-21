#!/bin/bash
# Stream Railway backend logs in real-time
# Usage: ./scripts/tail_backend_logs.sh [service_name]

SERVICE_NAME="${1:-tradingagents-backend}"

echo "=========================================="
echo "Streaming Railway Logs: $SERVICE_NAME"
echo "=========================================="
echo "Press Ctrl+C to stop"
echo ""

# Check if Railway CLI is available
if ! command -v railway &> /dev/null; then
    echo "✗ Railway CLI not installed"
    echo "Run: ./scripts/setup_railway_cli.sh"
    exit 1
fi

# Check authentication
if [ -z "$RAILWAY_TOKEN" ]; then
    echo "✗ RAILWAY_TOKEN not set"
    echo "Add your Railway token to Replit Secrets as RAILWAY_TOKEN"
    exit 1
fi

export RAILWAY_TOKEN

# Stream logs (follows new entries in real-time)
railway logs --follow

# Alternative: filter for specific patterns
# railway logs --follow | grep -E "\[BET\]|\[SKIP\]|\[CATEGORY\]|\[ERROR\]"
