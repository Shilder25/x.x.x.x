"""
Monkey-patch for Opinion.trade SDK to inject browser headers and bypass geo-blocking
"""
import sys
import os
import logging
import json
from typing import Dict, Any, Optional
from unittest.mock import patch
import requests
from requests import Session

logger = logging.getLogger(__name__)

# Browser headers that mimic a real user
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cache-Control': 'no-cache',
    'DNT': '1',
    'Origin': 'https://app.opinion.trade',
    'Referer': 'https://app.opinion.trade/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
}

# VPN/Proxy detection bypass headers
PROXY_BYPASS_HEADERS = {
    'X-Forwarded-For': '185.28.23.45',  # Netherlands IP
    'X-Real-IP': '185.28.23.45',
    'X-Originating-IP': '185.28.23.45',
    'CF-Connecting-IP': '185.28.23.45',
    'True-Client-IP': '185.28.23.45',
}

class PatchedSession(Session):
    """Enhanced session that injects browser headers into all requests"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default browser headers
        self.headers.update(BROWSER_HEADERS)
        self.headers.update(PROXY_BYPASS_HEADERS)
        logger.info("PatchedSession initialized with browser headers")
    
    def request(self, method, url, **kwargs):
        """Override request to log and inject headers"""
        # Ensure our headers are always included
        if 'headers' in kwargs:
            combined_headers = self.headers.copy()
            combined_headers.update(kwargs['headers'])
            kwargs['headers'] = combined_headers
        
        # Log the request
        logger.debug(f"Patched Request: {method} {url}")
        logger.debug(f"Headers: {json.dumps(dict(kwargs.get('headers', self.headers)), indent=2)}")
        
        # Make the request
        response = super().request(method, url, **kwargs)
        
        # Log the response
        logger.debug(f"Response: {response.status_code}")
        if response.status_code >= 400:
            logger.error(f"Error Response: {response.text}")
        
        return response

def patch_opinion_sdk():
    """Apply monkey-patches to Opinion.trade SDK"""
    logger.info("Applying patches to Opinion.trade SDK...")
    
    # Patch requests.Session globally
    original_session = requests.Session
    
    def patched_session_constructor(*args, **kwargs):
        """Replace Session with PatchedSession"""
        return PatchedSession(*args, **kwargs)
    
    requests.Session = patched_session_constructor
    
    # Also patch the opinion_clob_sdk if it's using requests internally
    try:
        import opinion_clob_sdk
        # Find and patch any Session usage in the SDK
        if hasattr(opinion_clob_sdk, 'Client'):
            original_client_init = opinion_clob_sdk.Client.__init__
            
            def patched_client_init(self, *args, **kwargs):
                """Patch Client initialization"""
                logger.info("Patching Opinion.trade Client initialization")
                result = original_client_init(self, *args, **kwargs)
                
                # If the client has a session attribute, replace it
                if hasattr(self, 'session'):
                    self.session = PatchedSession()
                    logger.info("Replaced client.session with PatchedSession")
                
                # If the client has a _session attribute (private), replace it too
                if hasattr(self, '_session'):
                    self._session = PatchedSession()
                    logger.info("Replaced client._session with PatchedSession")
                    
                return result
            
            opinion_clob_sdk.Client.__init__ = patched_client_init
            
    except ImportError:
        logger.warning("opinion_clob_sdk not found, skipping SDK-specific patches")
    
    logger.info("Patches applied successfully")

def test_patched_sdk():
    """Test the patched SDK"""
    # Apply patches
    patch_opinion_sdk()
    
    # Import after patching
    from opinion_trade_api import OpinionTradeAPI
    
    logger.info("=" * 80)
    logger.info("Testing Patched Opinion.trade SDK")
    logger.info("=" * 80)
    
    # Initialize API
    api = OpinionTradeAPI()
    
    # Test getting events
    logger.info("\nTest 1: Get Available Events")
    result = api.get_available_events(limit=5)
    
    print("\n" + "=" * 80)
    print("PATCHED SDK TEST RESULTS")
    print("=" * 80)
    print(f"Get Events: {'✓ PASSED' if result['success'] else '✗ FAILED'}")
    if not result['success']:
        print(f"Error: {result.get('error', 'Unknown')}")
        print(f"Message: {result.get('message', '')}")
    else:
        print(f"Retrieved {result.get('count', 0)} events")
    
    # Test balance check
    logger.info("\nTest 2: Get Account Balance")
    balance_result = api.get_account_balance()
    print(f"\nGet Balance: {'✓ PASSED' if balance_result['success'] else '✗ FAILED'}")
    if not balance_result['success']:
        print(f"Error: {balance_result.get('error', 'Unknown')}")
        print(f"Message: {balance_result.get('message', '')}")
    
    print("=" * 80)
    
    return result['success']

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test the patched SDK
    success = test_patched_sdk()
    sys.exit(0 if success else 1)