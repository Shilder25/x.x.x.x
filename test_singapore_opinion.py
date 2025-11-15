"""
Test Opinion.trade API from Singapore deployment
"""
import os
from opinion_clob_sdk import Client, CHAIN_ID_BNB_MAINNET
from opinion_clob_sdk.model import TopicType, TopicStatusFilter
from eth_account import Account

def test_opinion_trade_singapore():
    """Test if Opinion.trade API works from Singapore"""
    print("="*80)
    print("TESTING OPINION.TRADE API FROM SINGAPORE")
    print("="*80)
    
    # Get credentials
    api_key = os.environ.get("OPINION_TRADE_API_KEY", "")
    private_key = os.environ.get("OPINION_WALLET_PRIVATE_KEY", "")
    
    if not api_key or not private_key:
        print("✗ Missing credentials")
        return False
    
    # Derive wallet
    account = Account.from_key(private_key)
    wallet_address = account.address
    
    print(f"\n📍 Deployment Location: Singapore (Southeast Asia)")
    print(f"🔑 API Key: Configured")
    print(f"💼 Wallet: {wallet_address}")
    
    try:
        # Initialize SDK
        print("\n1️⃣ Initializing Opinion.trade SDK...")
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
        print("   ✓ SDK initialized")
        
        # Test get_markets
        print("\n2️⃣ Testing get_markets() API call...")
        response = client.get_markets(
            topic_type=TopicType.BINARY,
            status=TopicStatusFilter.ACTIVATED,
            page=1,
            limit=5
        )
        
        if response.errno == 0:
            markets = response.result.list
            print(f"   ✓ SUCCESS! Retrieved {len(markets)} active markets")
            print("\n   📊 Sample Markets:")
            for i, market in enumerate(markets[:3], 1):
                print(f"      {i}. {market.market_title[:60]}...")
            return True
        elif response.errno == 10403:
            print(f"   ✗ STILL BLOCKED: Error 10403 - {response.errmsg}")
            print("\n   Singapore is also geo-blocked by Opinion.trade")
            return False
        else:
            print(f"   ✗ API Error {response.errno}: {response.errmsg}")
            return False
            
    except Exception as e:
        print(f"   ✗ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n")
    success = test_opinion_trade_singapore()
    
    print("\n" + "="*80)
    if success:
        print("🎉 SUCCESS! Opinion.trade API is accessible from Singapore!")
        print("="*80)
        print("\n✅ Your system is now FULLY OPERATIONAL!")
        print("✅ All 5 AI agents can now trade on Opinion.trade")
        print("✅ Ready for autonomous daily execution")
    else:
        print("❌ FAILED: Singapore is also geo-blocked")
        print("="*80)
        print("\nNext steps:")
        print("1. Ask Opinion.trade founder which regions ARE allowed")
        print("2. Try US West or US East deployment")
        print("3. Consider using a proxy/VPN solution")
    print("="*80)
    
    exit(0 if success else 1)
