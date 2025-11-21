#!/usr/bin/env python3
"""
Quick test script to debug get_orderbook() and see actual SDK response structure
"""
import os
import sys
from opinion_trade_api import OpinionTradeAPI

# Use environment credentials
api = OpinionTradeAPI()

if not api.client:
    print("✗ Opinion.trade client not initialized")
    print("Make sure OPINION_TRADE_API_KEY and OPINION_WALLET_PRIVATE_KEY are set")
    sys.exit(1)

print("✓ Opinion.trade client initialized")
print(f"✓ Wallet: {api.wallet_address}")
print()

# First, get a few markets to find a token_id
print("Fetching markets to get token IDs...")
markets_response = api.get_available_events(limit=5)

if not markets_response.get('success'):
    print(f"✗ Failed to get markets: {markets_response.get('error')}")
    sys.exit(1)

events = markets_response.get('events', [])
if not events:
    print("✗ No events returned")
    sys.exit(1)

print(f"✓ Got {len(events)} events")
print()

# Test get_orderbook with first event's yes_token_id
first_event = events[0]
token_id = first_event.get('yes_token_id')

if not token_id:
    print("✗ First event has no yes_token_id")
    sys.exit(1)

print(f"Testing get_orderbook()...")
print(f"Event: {first_event['title'][:60]}...")
print(f"Token ID: {token_id}")
print()
print("=" * 80)
print("DEBUG LOGS SHOULD APPEAR BELOW:")
print("=" * 80)

# This will trigger all our debug logging
orderbook_response = api.get_orderbook(token_id)

print()
print("=" * 80)
print("RESPONSE:")
print("=" * 80)
print(f"Success: {orderbook_response.get('success')}")
print(f"Error: {orderbook_response.get('error')}")

if orderbook_response.get('success'):
    data = orderbook_response.get('data', {})
    bids = data.get('bids', [])
    asks = data.get('asks', [])
    print(f"Bids count: {len(bids)}")
    print(f"Asks count: {len(asks)}")
    
    if bids:
        print(f"First bid: {bids[0]}")
    if asks:
        print(f"First ask: {asks[0]}")
else:
    print(f"Message: {orderbook_response.get('message')}")

print()
print("=" * 80)
print("Check logs above for [ORDERBOOK DEBUG] entries to see SDK response structure")
print("=" * 80)
