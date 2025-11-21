#!/bin/bash
# Execute commands on Railway environment
# Usage: ./scripts/run_remote_command.sh "python health_check.py"

if [ -z "$1" ]; then
    echo "Usage: ./scripts/run_remote_command.sh \"<command>\""
    echo ""
    echo "Examples:"
    echo "  ./scripts/run_remote_command.sh \"python --version\""
    echo "  ./scripts/run_remote_command.sh \"cat autonomous_cycle.log\""
    echo "  ./scripts/run_remote_command.sh \"curl localhost:8000/health\""
    exit 1
fi

COMMAND="$1"

echo "=========================================="
echo "Running on Railway: $COMMAND"
echo "=========================================="

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

# Execute command remotely
railway run "$COMMAND"
