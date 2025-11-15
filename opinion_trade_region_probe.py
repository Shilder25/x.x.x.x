#!/usr/bin/env python3
"""
Quick Opinion.trade API region probe
Tests if Opinion.trade API is accessible from current deployment location
"""
import os
import sys
import time
from opinion_clob_sdk import Client, CHAIN_ID_BNB_MAINNET
from opinion_clob_sdk.model import TopicType, TopicStatusFilter
from eth_account import Account

def probe_opinion_trade(region_name="Unknown"):
    """
    Probe Opinion.trade API accessibility
    
    Args:
        region_name: Human-readable name of deployment region
        
    Returns:
        bool: True if accessible, False if blocked
    """
    print(f"\n{'='*70}")
    print(f"Opinion.trade API Probe")
    print(f"Region: {region_name}")
    print(f"{'='*70}")
    
    # Get credentials
    api_key = os.environ.get("OPINION_TRADE_API_KEY", "")
    private_key = os.environ.get("OPINION_WALLET_PRIVATE_KEY", "")
    
    if not api_key or not private_key:
        print("❌ Missing OPINION_TRADE_API_KEY or OPINION_WALLET_PRIVATE_KEY")
        return False
    
    try:
        # Derive wallet
        account = Account.from_key(private_key)
        wallet_address = account.address
        
        print(f"📍 Testing from: {region_name}")
        print(f"💼 Wallet: {wallet_address}")
        print(f"🔑 API Key: Configured")
        
        # Initialize SDK
        print("\n⏳ Initializing SDK...")
        start_time = time.time()
        
        client = Client(
            host='https://proxy.opinion.trade:8443',
            apikey=api_key,
            chain_id=CHAIN_ID_BNB_MAINNET,
            rpc_url='https://bsc-dataseed.binance.org/',
            private_key=private_key,
            multi_sig_addr=wallet_address,
            conditional_tokens_addr='0xAD1a38cEc043e70E83a3eC30443dB285ED10D774',
            multisend_addr='0x998739BFdAAdde7C933B942a68053933098f9EDa',
        )
        
        init_time = time.time() - start_time
        print(f"✓ SDK initialized ({init_time:.2f}s)")
        
        # Test API call
        print("\n⏳ Testing get_markets()...")
        start_time = time.time()
        
        response = client.get_markets(
            topic_type=TopicType.BINARY,
            status=TopicStatusFilter.ACTIVATED,
            page=1,
            limit=5
        )
        
        api_time = time.time() - start_time
        
        # Check result
        if response.errno == 0:
            markets = response.result.list
            print(f"\n{'='*70}")
            print(f"✅ SUCCESS - Region {region_name} is ALLOWED")
            print(f"{'='*70}")
            print(f"Retrieved: {len(markets)} active markets")
            print(f"Latency: {api_time:.2f}s")
            print(f"\nSample markets:")
            for i, market in enumerate(markets[:3], 1):
                print(f"  {i}. {market.market_title[:60]}")
            return True
            
        elif response.errno == 10403:
            print(f"\n{'='*70}")
            print(f"❌ BLOCKED - Region {region_name} is GEO-BLOCKED")
            print(f"{'='*70}")
            print(f"Error: {response.errmsg}")
            return False
            
        else:
            print(f"\n{'='*70}")
            print(f"⚠️  API Error {response.errno}")
            print(f"{'='*70}")
            print(f"Error: {response.errmsg}")
            return False
            
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ EXCEPTION")
        print(f"{'='*70}")
        print(f"Error: {str(e)}")
        return False

def main():
    """Main entry point"""
    # Get region from environment or argument
    region = os.environ.get("RAILWAY_REGION", "Unknown")
    
    if len(sys.argv) > 1:
        region = sys.argv[1]
    
    # Run probe
    success = probe_opinion_trade(region)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
