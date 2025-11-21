#!/usr/bin/env python3
"""
Fetch Railway deployment logs via GraphQL API.
Bypasses Railway CLI authentication issues.
"""

import os
import sys
import json
import requests
from datetime import datetime

# Railway GraphQL API endpoint
RAILWAY_API_URL = "https://backboard.railway.com/graphql/v2"

# Service configuration
SERVICE_ID = "14c1acd7-e253-4401-97fe-ae85de754b67"
ENVIRONMENT_ID = "5c688741-e7d2-4442-9b32-dd634a7c4865"  # From URL: ?environmentId=...

def fetch_logs(limit=100, filter_pattern=None):
    """
    Fetch logs from Railway using GraphQL API.
    
    Args:
        limit: Number of log lines to fetch (default: 100)
        filter_pattern: Optional string to filter logs (e.g., "ORDERBOOK DEBUG")
    """
    # Get Account Token from environment
    token = os.environ.get('RAILWAY_API_TOKEN')
    if not token:
        print("❌ Error: RAILWAY_API_TOKEN not set in environment")
        print("\nTo fix:")
        print("1. Go to Railway Dashboard → Account Settings → Tokens")
        print("2. Create an Account Token (not Project Token)")
        print("3. Add it to Replit Secrets as RAILWAY_API_TOKEN")
        sys.exit(1)
    
    # GraphQL query to fetch deployment logs
    # Reference: https://docs.railway.com/reference/public-api
    query = """
    query GetDeploymentLogs($environmentId: String!, $serviceId: String!, $limit: Int!) {
      deployments(input: {
        environmentId: $environmentId
        serviceId: $serviceId
      }) {
        edges {
          node {
            id
            status
            createdAt
            staticUrl
          }
        }
      }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    variables = {
        "environmentId": ENVIRONMENT_ID,
        "serviceId": SERVICE_ID,
        "limit": limit
    }
    
    print(f"🔍 Fetching Railway logs...")
    print(f"   Service: {SERVICE_ID}")
    print(f"   Environment: {ENVIRONMENT_ID}")
    print(f"   Limit: {limit} lines")
    if filter_pattern:
        print(f"   Filter: '{filter_pattern}'")
    print("")
    
    try:
        response = requests.post(
            RAILWAY_API_URL,
            headers=headers,
            json={"query": query, "variables": variables},
            timeout=30
        )
        
        if response.status_code == 401:
            print("❌ Authentication failed (401 Unauthorized)")
            print("\nPossible issues:")
            print("- RAILWAY_API_TOKEN is invalid or expired")
            print("- Token doesn't have access to this project")
            print("\nCreate a new Account Token at:")
            print("https://railway.app/account/tokens")
            sys.exit(1)
        
        response.raise_for_status()
        data = response.json()
        
        # Check for GraphQL errors
        if 'errors' in data:
            print("❌ GraphQL API error:")
            print(json.dumps(data['errors'], indent=2))
            sys.exit(1)
        
        # Extract deployments
        deployments = data.get('data', {}).get('deployments', {}).get('edges', [])
        
        if not deployments:
            print("⚠️  No deployments found")
            print("\nTroubleshooting:")
            print("- Verify SERVICE_ID and ENVIRONMENT_ID are correct")
            print("- Check if service has any deployments")
            sys.exit(1)
        
        print(f"✅ Found {len(deployments)} deployment(s)")
        print("")
        print("=" * 80)
        
        # Show deployment info
        for i, edge in enumerate(deployments[:3]):  # Show first 3
            deployment = edge['node']
            status = deployment.get('status', 'UNKNOWN')
            created_at = deployment.get('createdAt', '')
            deploy_id = deployment.get('id', '')
            url = deployment.get('staticUrl', 'N/A')
            
            print(f"Deployment {i+1}:")
            print(f"  ID: {deploy_id}")
            print(f"  Status: {status}")
            print(f"  Created: {created_at}")
            print(f"  URL: {url}")
            print("")
        
        print("=" * 80)
        print("")
        print("ℹ️  Note: Railway GraphQL API v2 doesn't expose log streaming yet.")
        print("   For now, use Railway Web UI to view logs:")
        print(f"   https://railway.com/project/71558abf-25b0-4cb5-8233-fe6e685e0e93/service/{SERVICE_ID}")
        print("")
        print("   Once deployed, logs will show [ORDERBOOK DEBUG] messages.")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch Railway deployment logs")
    parser.add_argument("-n", "--limit", type=int, default=100, help="Number of log lines (default: 100)")
    parser.add_argument("-f", "--filter", type=str, help="Filter logs by pattern (e.g., 'ORDERBOOK DEBUG')")
    
    args = parser.parse_args()
    
    fetch_logs(limit=args.limit, filter_pattern=args.filter)
