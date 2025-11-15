#!/usr/bin/env python3
"""
Test autonomous trading flow components individually
"""
import os
import sys

# Test 1: Can we fetch markets from Opinion.trade?
print("="*80)
print("TEST 1: Fetching markets from Opinion.trade")
print("="*80)

from opinion_trade_api import OpinionTradeAPI

api = OpinionTradeAPI()
markets_result = api.get_available_events(limit=5)

if markets_result['success']:
    print(f"✅ SUCCESS: Retrieved {markets_result['count']} markets")
    if markets_result['count'] > 0:
        first_market = markets_result['events'][0]
        print(f"\nFirst market:")
        print(f"  Title: {first_market['title']}")
        print(f"  Market ID: {first_market['market_id']}")
        print(f"  YES Token: {first_market['yes_token_id'][:20]}...")
        print(f"  NO Token: {first_market['no_token_id'][:20]}...")
else:
    print(f"❌ FAILED: {markets_result.get('message', 'Unknown error')}")
    sys.exit(1)

# Test 2: Can we call one AI to analyze a market?
print("\n" + "="*80)
print("TEST 2: AI Analysis (ChatGPT)")
print("="*80)

from llm_clients import LLMOrchestrator

orchestrator = LLMOrchestrator()

# Get first market
market = markets_result['events'][0]

try:
    print(f"Analyzing market: {market['title'][:50]}...")
    
    # Simple analysis with ChatGPT
    analysis_prompt = f"""
Analyze this prediction market and provide a quick YES/NO prediction:

Market: {market['title']}
Description: {market.get('description', market['title'])}

Respond with JSON:
{{
    "prediction": "YES" or "NO",
    "confidence": 0.0 to 1.0,
    "reasoning": "brief explanation"
}}
"""
    
    response = orchestrator.call_chatgpt(analysis_prompt, "chatgpt-firm")
    
    if response['success']:
        print(f"✅ SUCCESS: ChatGPT analyzed the market")
        print(f"  Response length: {len(response['response'])} chars")
        print(f"  Preview: {response['response'][:200]}...")
    else:
        print(f"❌ FAILED: {response.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Check database connection
print("\n" + "="*80)
print("TEST 3: Database Connection")
print("="*80)

from database import db

try:
    # Try to query recent predictions
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM predictions")
    count = cursor.fetchone()[0]
    print(f"✅ SUCCESS: Database connected")
    print(f"  Total predictions in DB: {count}")
    cursor.close()
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("Market fetching: ✅")
print("AI analysis: Check output above")
print("Database: Check output above")
print("\nIf all tests passed, the autonomous system should work end-to-end!")
