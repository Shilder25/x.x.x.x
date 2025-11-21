#!/bin/bash
# View Railway logs without Project Token conflicts
# Uses Account Token + railway link for authentication

# Unset Project Token to avoid conflicts with railway link
unset RAILWAY_TOKEN

# Show logs (pass any arguments like --lines, etc.)
railway logs "$@"
