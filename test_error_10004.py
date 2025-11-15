import os
from dotenv import load_dotenv
from opinion_trade_api import OpinionTradeAPI

load_dotenv()

print("=" * 80)
print("TEST: Diagnosing Error 10004")
print("=" * 80)

api = OpinionTradeAPI()

print("\n1. Testing Opinion.trade connection...")
result = api.get_available_events()

if result.get('success'):
    events = result.get('events', [])
    print(f"✓ Successfully fetched {len(events)} events")
    
    if events:
        print("\n2. Testing get_latest_price on first event...")
        event = events[0]
        
        print(f"   Event: {event.get('title', 'Unknown')[:60]}...")
        print(f"   Market ID: {event.get('market_id')}")
        print(f"   YES Token ID: {event.get('yes_token_id')}")
        print(f"   NO Token ID: {event.get('no_token_id')}")
        
        if event.get('yes_token_id'):
            print(f"\n3. Calling get_latest_price for YES token...")
            price_result = api.get_latest_price(event.get('yes_token_id'))
            
            print(f"\nResponse:")
            print(f"  Success: {price_result.get('success')}")
            print(f"  Error: {price_result.get('error')}")
            print(f"  Message: {price_result.get('message')}")
            
            if price_result.get('success'):
                print(f"  Price: {price_result.get('price')}")
            else:
                print(f"\n⚠️  ERROR DETAILS:")
                print(f"     Error Code: {price_result.get('error')}")
                print(f"     Error Message: {price_result.get('message')}")
                print(f"     Token ID: {price_result.get('token_id')}")
        else:
            print("✗ No YES token ID available")
    else:
        print("✗ No events returned")
else:
    print(f"✗ Failed to fetch events: {result.get('error')}")

print("\n" + "=" * 80)
