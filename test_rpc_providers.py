"""
Test multiple RPC providers to verify if error 10403 is RPC-related
"""
import os
import time
from typing import Dict, List
from opinion_trade_api import OpinionTradeAPI

# List of public BNB Chain RPC endpoints
RPC_PROVIDERS = {
    'Binance Official': 'https://bsc-dataseed.binance.org/',
    'Binance Official 1': 'https://bsc-dataseed1.binance.org/',
    'Binance Official 2': 'https://bsc-dataseed2.binance.org/',
    'Nodereal (Public)': 'https://bsc-dataseed.nodereal.io/',
    'Nodereal Alt': 'https://bsc-dataseed1.nodereal.io/',
    'Ankr (Public)': 'https://rpc.ankr.com/bsc',
    'dRPC (Public)': 'https://bsc.drpc.org',
    'PublicNode': 'https://bsc-rpc.publicnode.com',
    'LlamaNodes': 'https://binance.llamarpc.com',
    'Blockpi': 'https://bsc.blockpi.network/v1/rpc/public',
}

def test_rpc_connection(name: str, rpc_url: str) -> Dict:
    """Test RPC connection and basic functionality"""
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"URL: {rpc_url}")
    print('='*80)
    
    result = {
        'name': name,
        'url': rpc_url,
        'rpc_connected': False,
        'opinion_api_works': False,
        'error': None,
        'latency_ms': None
    }
    
    try:
        # Test RPC connection
        from web3 import Web3
        start = time.time()
        w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 10}))
        
        # Try to get chain ID
        chain_id = w3.eth.chain_id
        latency = (time.time() - start) * 1000
        
        if chain_id == 56:
            result['rpc_connected'] = True
            result['latency_ms'] = round(latency, 2)
            print(f"✓ RPC Connected (Chain ID: {chain_id}, Latency: {latency:.2f}ms)")
        else:
            result['error'] = f"Wrong chain ID: {chain_id}"
            print(f"✗ Wrong chain ID: {chain_id} (expected 56)")
            return result
            
    except Exception as e:
        result['error'] = f"RPC connection failed: {str(e)}"
        print(f"✗ RPC Connection Failed: {str(e)}")
        return result
    
    # Test Opinion.trade API with this RPC
    try:
        print(f"\nTesting Opinion.trade API with {name}...")
        
        # Create temporary opinion_trade_api.py client with custom RPC
        from opinion_clob_sdk import Client, CHAIN_ID_BNB_MAINNET
        from opinion_clob_sdk.model import TopicType, TopicStatusFilter
        from eth_account import Account
        
        api_key = os.environ.get("OPINION_TRADE_API_KEY", "")
        private_key = os.environ.get("OPINION_WALLET_PRIVATE_KEY", "")
        
        if not api_key or not private_key:
            result['error'] = "Missing API credentials"
            print("✗ Missing API credentials")
            return result
        
        # Derive wallet address
        account = Account.from_key(private_key)
        wallet_address = account.address
        
        # Initialize SDK with this RPC
        client = Client(
            host='https://proxy.opinion.trade:8443',
            apikey=api_key,
            chain_id=CHAIN_ID_BNB_MAINNET,
            rpc_url=rpc_url,  # Use this RPC
            private_key=private_key,
            multi_sig_addr=wallet_address,
            conditional_tokens_addr='0xAD1a38cEc043e70E83a3eC30443dB285ED10D774',
            multisend_addr='0x998739BFdAAdde7C933B942a68053933098f9EDa',
        )
        
        print(f"  SDK initialized with {name}")
        
        # Test get_markets
        response = client.get_markets(
            topic_type=TopicType.BINARY,
            status=TopicStatusFilter.ACTIVATED,
            page=1,
            limit=5
        )
        
        if response.errno == 0:
            result['opinion_api_works'] = True
            markets_count = len(response.result.list) if hasattr(response.result, 'list') else 0
            print(f"✓ Opinion.trade API SUCCESS - Retrieved {markets_count} markets")
        else:
            result['error'] = f"API error {response.errno}: {response.errmsg}"
            if response.errno == 10403:
                print(f"✗ Error 10403: {response.errmsg}")
            else:
                print(f"✗ API Error {response.errno}: {response.errmsg}")
                
    except Exception as e:
        result['error'] = f"Opinion API test failed: {str(e)}"
        print(f"✗ Opinion API Test Failed: {str(e)}")
    
    return result

def main():
    """Test all RPC providers"""
    print("\n" + "="*80)
    print("BNB CHAIN RPC PROVIDER TESTING")
    print("Testing multiple RPC providers to diagnose Opinion.trade error 10403")
    print("="*80)
    
    results: List[Dict] = []
    
    for name, url in RPC_PROVIDERS.items():
        result = test_rpc_connection(name, url)
        results.append(result)
        time.sleep(1)  # Small delay between tests
    
    # Print summary
    print("\n\n" + "="*80)
    print("SUMMARY REPORT")
    print("="*80)
    
    print(f"\n{'Provider':<25} {'RPC':<8} {'Opinion API':<12} {'Latency':<12} {'Error'}")
    print("-" * 100)
    
    working_providers = []
    
    for r in results:
        rpc_status = "✓ OK" if r['rpc_connected'] else "✗ FAIL"
        api_status = "✓ WORKS" if r['opinion_api_works'] else "✗ BLOCKED"
        latency = f"{r['latency_ms']}ms" if r['latency_ms'] else "N/A"
        error = (r['error'][:40] + "...") if r['error'] and len(r['error']) > 40 else (r['error'] or "")
        
        print(f"{r['name']:<25} {rpc_status:<8} {api_status:<12} {latency:<12} {error}")
        
        if r['opinion_api_works']:
            working_providers.append(r['name'])
    
    print("\n" + "="*80)
    
    if working_providers:
        print("✓ GOOD NEWS: The following RPCs work with Opinion.trade API:")
        for provider in working_providers:
            print(f"  - {provider}")
        print("\nRecommendation: Update opinion_trade_api.py to use one of these RPCs")
    else:
        print("✗ NO RPC WORKED: Error 10403 persists across all RPC providers")
        print("\nConclusion: The error is NOT RPC-related. It's purely Opinion.trade")
        print("API geo-blocking based on your IP address (Replit/Railway location).")
        print("\nNext Steps:")
        print("  1. Contact Opinion.trade support for IP whitelist")
        print("  2. Request access from EU West region (Amsterdam)")
        print("  3. Provide your API key from environment variables")
    
    print("="*80)
    
    return len(working_providers) > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
