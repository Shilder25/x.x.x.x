#!/usr/bin/env python3
"""
Quick test to verify the orderbook-based get_latest_price() workaround works.
"""
import os
import sys
from opinion_trade_api import OpinionTradeAPI

def test_orderbook_workaround():
    print("="*60)
    print("Testing Orderbook-based get_latest_price() Workaround")
    print("="*60)
    
    # Initialize API
    api = OpinionTradeAPI()
    
    # Get some markets
    print("\n1. Fetching markets...")
    markets_response = api.get_available_events(limit=3)
    
    if not markets_response.get('success'):
        print(f"❌ Failed to fetch markets: {markets_response.get('message')}")
        return False
    
    events = markets_response.get('events', [])
    if not events:
        print("❌ No markets available for testing")
        return False
    
    print(f"✓ Found {len(events)} markets")
    
    # Test get_latest_price on first market's YES token
    event = events[0]
    token_id = event.get('yes_token_id')
    
    print(f"\n2. Testing get_latest_price() on market:")
    print(f"   Title: {event.get('title', 'Unknown')[:60]}...")
    print(f"   Token ID: {token_id}")
    
    price_response = api.get_latest_price(token_id)
    
    if price_response.get('success'):
        print(f"\n✅ SUCCESS! Price fetched via orderbook workaround:")
        print(f"   Price: {price_response.get('price', 'N/A')}")
        print(f"   Bid: {price_response.get('bid_price', 'N/A')}")
        print(f"   Ask: {price_response.get('ask_price', 'N/A')}")
        print(f"   Spread: {price_response.get('spread', 'N/A')}")
        print(f"   Source: {price_response.get('data', {}).get('source', 'Unknown')}")
        return True
    else:
        print(f"\n❌ Failed to fetch price:")
        print(f"   Error: {price_response.get('error')}")
        print(f"   Message: {price_response.get('message')}")
        return False

if __name__ == "__main__":
    try:
        success = test_orderbook_workaround()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
