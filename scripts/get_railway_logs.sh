#!/bin/bash
# Fetch Railway logs and save to file for analysis
# Usage: ./scripts/get_railway_logs.sh [search_pattern]

SEARCH_PATTERN="${1:-ORDERBOOK DEBUG}"
OUTPUT_FILE="/tmp/railway_logs_$(date +%Y%m%d_%H%M%S).log"

echo "=========================================="
echo "Fetching Railway Logs"
echo "=========================================="

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
    echo "❌ Error: Railway configuration not found"
    echo ""
    echo "Run this first to configure:"
    echo "  ./scripts/configure_railway_cli.sh"
    exit 1
fi

source "$CONFIG_FILE"

echo "Fetching last 500 log lines from Railway..."
echo "Service: $SERVICE_NAME ($SERVICE_ID)"
echo "Environment: $ENVIRONMENT"
echo "Filtering for: '$SEARCH_PATTERN'"
echo ""

# Get logs with explicit SERVICE_ID
# Note: --lines fetches historical logs (doesn't stream)
railway logs \
  -s "$SERVICE_ID" \
  -e "$ENVIRONMENT" \
  --lines 500 | grep -i "$SEARCH_PATTERN" | tee "$OUTPUT_FILE"

echo ""
echo "=========================================="
echo "✓ Logs saved to: $OUTPUT_FILE"
echo "=========================================="
echo ""
echo "Full log count: $(wc -l < "$OUTPUT_FILE") lines"
echo ""
echo "To view all logs:"
echo "  cat $OUTPUT_FILE"
echo ""
echo "To search within logs:"
echo "  grep 'pattern' $OUTPUT_FILE"
