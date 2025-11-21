#!/bin/bash
# Stream Railway backend logs in real-time
# Usage: ./scripts/tail_backend_logs.sh

echo "=========================================="
echo "Streaming Railway Production Logs"
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
    echo "✗ RAILWAY_TOKEN not set in Replit Secrets"
    echo ""
    echo "To fix:"
    echo "1. Go to https://railway.app → Your Project → Settings → Tokens"
    echo "2. Create a new Project Token"
    echo "3. Add it to Replit Secrets as RAILWAY_TOKEN"
    exit 1
fi

export RAILWAY_TOKEN

# Load configuration
CONFIG_FILE="scripts/.railway_config"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "✗ Railway configuration not found"
    echo ""
    echo "Run this first to configure:"
    echo "  ./scripts/configure_railway_cli.sh"
    exit 1
fi

source "$CONFIG_FILE"

echo "Service: $SERVICE_NAME ($SERVICE_ID)"
echo "Environment: $ENVIRONMENT"
echo "Using RAILWAY_TOKEN from environment..."
echo ""

# Stream logs with Railway token using SERVICE_ID
# Note: Project Token requires explicit service ID (not service name)
railway logs -s "$SERVICE_ID" -e "$ENVIRONMENT"

# Alternative: filter for specific debug patterns
# railway logs -s "$SERVICE_ID" -e "$ENVIRONMENT" | grep -E "\[ORDERBOOK DEBUG\]|\[BET\]|\[SKIP\]|\[ERROR\]"
