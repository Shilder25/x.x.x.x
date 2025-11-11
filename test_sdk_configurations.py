#!/usr/bin/env python3
"""
Test script to try different Opinion.trade SDK configurations.
This tests 3 different multi_sig_addr values to see which (if any) resolves error 10403.
"""

import os
import sys
from datetime import datetime
from opinion_clob_sdk import Client, CHAIN_ID_BNB_MAINNET
from opinion_clob_sdk.model import TopicType, TopicStatusFilter

def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_section(title):
    print(f"\n{'─'*80}")
    print(f"  {title}")
    print(f"{'─'*80}\n")

def test_configuration(config_name, multi_sig_addr_value, description):
    """Test a specific SDK configuration"""
    print_section(f"Testing {config_name}: {description}")
    
    api_key = os.environ.get("OPINION_TRADE_API_KEY", "")
    private_key = os.environ.get("OPINION_WALLET_PRIVATE_KEY", "")
    
    if not api_key or not private_key:
        print("❌ ERROR: Missing OPINION_TRADE_API_KEY or OPINION_WALLET_PRIVATE_KEY")
        return False
    
    try:
        # Initialize client with this configuration
        print(f"Initializing SDK with multi_sig_addr = '{multi_sig_addr_value}'")
        
        client = Client(
            host='https://proxy.opinion.trade:8443',
            apikey=api_key,
            chain_id=CHAIN_ID_BNB_MAINNET,
            rpc_url='https://bsc-dataseed.binance.org/',
            private_key=private_key,
            multi_sig_addr=multi_sig_addr_value,
            conditional_tokens_addr='0xAD1a38cEc043e70E83a3eC30443dB285ED10D774',
            multisend_addr='0x998739BFdAAdde7C933B942a68053933098f9EDa',
            enable_trading_check_interval=3600,
            quote_tokens_cache_ttl=3600,
            market_cache_ttl=300
        )
        
        print("✓ SDK client initialized successfully")
        
        # Try to get markets
        print("\nAttempting to call get_markets()...")
        
        response = client.get_markets(
            topic_type=TopicType.BINARY,
            status=TopicStatusFilter.ACTIVATED,
            page=1,
            limit=1
        )
        
        # Check response
        if hasattr(response, 'errno'):
            if response.errno == 0:
                print(f"✅ SUCCESS! API call worked!")
                print(f"   Response errno: {response.errno}")
                if hasattr(response, 'result') and hasattr(response.result, 'list'):
                    markets_count = len(response.result.list)
                    print(f"   Markets retrieved: {markets_count}")
                    if markets_count > 0:
                        market = response.result.list[0]
                        print(f"   First market: {getattr(market, 'marketTitle', 'N/A')}")
                print(f"\n🎉 Configuration {config_name} WORKS! This resolves error 10403.")
                return True
            else:
                error_msg = getattr(response, 'errmsg', 'Unknown error')
                print(f"❌ FAILED: errno = {response.errno}")
                print(f"   Error message: {error_msg}")
                
                if response.errno == 10403:
                    print(f"\n⚠️  Configuration {config_name} still gets error 10403 (geo-blocking)")
                
                return False
        else:
            print(f"❌ Unexpected response format: {response}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        return False

def main():
    """Run all configuration tests"""
    print_header("OPINION.TRADE SDK CONFIGURATION TESTER")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Environment: Railway (EU West region expected)")
    print(f"Python version: {sys.version}")
    
    # Define configurations to test
    configurations = [
        {
            'name': 'Configuration A',
            'multi_sig_addr': '',
            'description': 'Empty multi_sig_addr (let SDK handle it automatically)'
        },
        {
            'name': 'Configuration B',
            'multi_sig_addr': '0x43C9bAd451ed65b5268cec681FCe42AdA00Fc675',
            'description': 'Login wallet (current configuration)'
        },
        {
            'name': 'Configuration C',
            'multi_sig_addr': '0x15c1a1d8ed9838c92f420e45ac064710aebf9268',
            'description': 'Trading wallet (Balance Spot wallet created by Opinion.trade)'
        }
    ]
    
    results = {}
    
    # Test each configuration
    for config in configurations:
        success = test_configuration(
            config['name'],
            config['multi_sig_addr'],
            config['description']
        )
        results[config['name']] = success
    
    # Summary
    print_header("TEST RESULTS SUMMARY")
    
    working_configs = []
    failed_configs = []
    
    for config_name, success in results.items():
        status = "✅ WORKS" if success else "❌ FAILED"
        print(f"{status} │ {config_name}")
        
        if success:
            working_configs.append(config_name)
        else:
            failed_configs.append(config_name)
    
    print("\n" + "="*80)
    
    if working_configs:
        print(f"\n🎉 GOOD NEWS: {len(working_configs)} configuration(s) resolved the error 10403:")
        for config in working_configs:
            print(f"   • {config}")
        print("\nRecommendation: Update opinion_trade_api.py to use the working configuration.")
    else:
        print("\n⚠️  BAD NEWS: All configurations still get error 10403")
        print("\nThis confirms that the error is caused by Opinion.trade geo-blocking,")
        print("not by incorrect SDK configuration.")
        print("\nNext steps:")
        print("1. Contact Opinion.trade support")
        print("2. Request IP whitelist for Railway deployment")
        print("3. Provide Railway outbound IPs and API credentials")
        print("\nSee PROBLEMA_OPINION_TRADE_GEO_BLOCK.md for detailed instructions.")
    
    print("="*80 + "\n")
    
    return 0 if working_configs else 1

if __name__ == "__main__":
    exit(main())
