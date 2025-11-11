"""
Advanced HTTP Interceptor for Opinion.trade SDK
Logs all HTTP requests/responses and injects browser-like headers
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import time
from datetime import datetime
import logging
from typing import Dict, Any, Optional
import os

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OpinionTradeInterceptor:
    """HTTP interceptor to debug and enhance Opinion.trade API requests"""
    
    def __init__(self, log_file: str = "opinion_trade_requests.log"):
        self.log_file = log_file
        self.session = self._create_session()
        self.request_count = 0
        
    def _create_session(self) -> requests.Session:
        """Create enhanced session with retry logic and browser headers"""
        session = requests.Session()
        
        # Add retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set browser-like headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'DNT': '1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"'
        })
        
        return session
    
    def log_request(self, method: str, url: str, headers: Dict, data: Any = None):
        """Log detailed request information"""
        self.request_count += 1
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": self.request_count,
            "method": method,
            "url": url,
            "headers": dict(headers),
            "data": data if isinstance(data, dict) else str(data)[:500]  # Limit data size
        }
        
        # Console logging
        logger.info(f"REQUEST #{self.request_count}: {method} {url}")
        logger.debug(f"Headers: {json.dumps(dict(headers), indent=2)}")
        if data:
            logger.debug(f"Data: {json.dumps(data if isinstance(data, dict) else str(data)[:200], indent=2)}")
        
        # File logging
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def log_response(self, response: requests.Response):
        """Log detailed response information"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": self.request_count,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "response_time_ms": response.elapsed.total_seconds() * 1000,
            "content_length": len(response.content),
            "content": response.text[:1000] if response.text else None  # First 1000 chars
        }
        
        # Console logging
        logger.info(f"RESPONSE #{self.request_count}: {response.status_code} in {response.elapsed.total_seconds():.2f}s")
        logger.debug(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
        
        # Log full response for errors
        if response.status_code >= 400:
            logger.error(f"ERROR Response: {response.text}")
        else:
            logger.debug(f"Response Body: {response.text[:500]}")
        
        # File logging
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def make_request(self, method: str, url: str, headers: Optional[Dict] = None, 
                    data: Optional[Any] = None, json_data: Optional[Dict] = None,
                    params: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with full logging and enhanced headers"""
        
        # Merge headers with session headers
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Add additional tracking headers
        request_headers['X-Request-ID'] = f"debug-{self.request_count}-{int(time.time())}"
        request_headers['X-Client-Version'] = "opinion-trade-debug-1.0"
        
        # Log the request
        self.log_request(method, url, request_headers, data or json_data)
        
        try:
            # Make the actual request
            response = self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                data=data,
                json=json_data,
                params=params,
                timeout=30,
                verify=True
            )
            
            # Log the response
            self.log_response(response)
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise
    
    def test_direct_api(self, api_key: str, wallet_address: str) -> Dict:
        """Test direct API call to Opinion.trade with enhanced headers"""
        
        # Test 1: Get markets endpoint
        url = "https://proxy.opinion.trade:8443/markets"
        
        # Add Opinion.trade specific headers
        headers = {
            'X-API-Key': api_key,
            'X-Wallet-Address': wallet_address,
            'Origin': 'https://app.opinion.trade',
            'Referer': 'https://app.opinion.trade/',
        }
        
        logger.info("=" * 80)
        logger.info("Testing Direct API Call to Opinion.trade")
        logger.info("=" * 80)
        
        try:
            response = self.make_request(
                method="GET",
                url=url,
                headers=headers,
                params={
                    'topicType': 'BINARY',
                    'status': 'ACTIVATED',
                    'page': 1,
                    'limit': 10
                }
            )
            
            result = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response.json() if response.status_code == 200 else response.text
            }
            
            logger.info(f"Direct API Test Result: {'SUCCESS' if result['success'] else 'FAILED'}")
            return result
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'type': type(e).__name__
            }
            logger.error(f"Direct API Test Failed: {error_result}")
            return error_result

def test_interceptor():
    """Test the interceptor with various configurations"""
    
    # Get environment variables
    api_key = os.environ.get("OPINION_TRADE_API_KEY", "")
    private_key = os.environ.get("OPINION_WALLET_PRIVATE_KEY", "")
    
    if not api_key or not private_key:
        logger.error("Missing OPINION_TRADE_API_KEY or OPINION_WALLET_PRIVATE_KEY")
        return
    
    # Derive wallet address from private key
    from eth_account import Account
    account = Account.from_key(private_key)
    wallet_address = account.address
    
    logger.info(f"Testing with wallet: {wallet_address}")
    
    # Create interceptor
    interceptor = OpinionTradeInterceptor()
    
    # Test direct API
    result = interceptor.test_direct_api(api_key, wallet_address)
    
    print("\n" + "=" * 80)
    print("INTERCEPTOR TEST RESULTS")
    print("=" * 80)
    print(f"Direct API Test: {'✓ PASSED' if result['success'] else '✗ FAILED'}")
    if not result['success']:
        print(f"Error: {result.get('error', result.get('data', 'Unknown error'))}")
    print(f"\nFull logs written to: opinion_trade_requests.log")
    print("=" * 80)

if __name__ == "__main__":
    test_interceptor()