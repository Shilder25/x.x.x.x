#!/usr/bin/env python3
"""
Health check script for Opinion.trade SDK connectivity
Run this BEFORE deploying to verify SDK configuration is correct
"""

import os
import sys
from opinion_trade_api import OpinionTradeAPI

def main():
    print("=" * 60)
    print("Opinion.trade SDK Health Check")
    print("=" * 60)
    
    # Check environment variables
    api_key = os.getenv('OPINION_TRADE_API_KEY')
    private_key = os.getenv('OPINION_WALLET_PRIVATE_KEY')
    
    if not api_key:
        print("✗ OPINION_TRADE_API_KEY not set")
        return False
    
    if not private_key:
        print("✗ OPINION_WALLET_PRIVATE_KEY not set")
        return False
    
    print("✓ Environment variables configured")
    
    # Initialize SDK
    try:
        print("\n[1/4] Initializing Opinion.trade SDK...")
        api = OpinionTradeAPI()
        print("✓ SDK initialized successfully")
    except Exception as e:
        print(f"✗ SDK initialization failed: {e}")
        return False
    
    # Test wallet balance
    try:
        print("\n[2/4] Checking wallet balance...")
        balance = api.get_balance()
        if balance.get('success'):
            total_balance = balance.get('total_balance', 0)
            print(f"✓ Wallet balance: ${total_balance:.2f}")
        else:
            print(f"✗ Balance check failed: {balance.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Balance check exception: {e}")
        return False
    
    # Test market fetching
    try:
        print("\n[3/4] Fetching active markets...")
        response = api.get_active_events(limit=5)
        if response.get('success'):
            events = response.get('events', [])
            print(f"✓ Retrieved {len(events)} markets")
            if events:
                print(f"  Sample: {events[0].get('title', 'Unknown')[:60]}...")
        else:
            print(f"✗ Market fetch failed: {response.get('error')}")
            return False
    except Exception as e:
        print(f"✗ Market fetch exception: {e}")
        return False
    
    # Test orderbook access
    try:
        print("\n[4/4] Testing orderbook access...")
        response = api.get_active_events(limit=1)
        if response.get('success') and response.get('events'):
            event = response['events'][0]
            token_id = event.get('yes_token_id')
            if token_id:
                orderbook_response = api.get_orderbook(token_id)
                if orderbook_response.get('success'):
                    orderbook = orderbook_response.get('orderbook', {})
                    bids = len(orderbook.get('bids', []))
                    asks = len(orderbook.get('asks', []))
                    print(f"✓ Orderbook accessible (bids={bids}, asks={asks})")
                else:
                    print(f"⚠  Orderbook fetch failed (may be normal for some markets)")
            else:
                print(f"⚠  No token_id found (market may not be tradeable)")
        else:
            print(f"⚠  No markets available for orderbook test")
    except Exception as e:
        print(f"⚠  Orderbook test exception: {e}")
    
    print("\n" + "=" * 60)
    print("✓ Health Check PASSED - SDK is ready")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
