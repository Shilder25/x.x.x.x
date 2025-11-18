import os
import time
from typing import Dict, Optional, List
from datetime import datetime
from eth_account import Account
from functools import wraps

from opinion_clob_sdk import Client, CHAIN_ID_BNB_MAINNET
from opinion_clob_sdk.model import TopicType, TopicStatusFilter
from opinion_clob_sdk.chain.py_order_utils.model.order import PlaceOrderDataInput
from opinion_clob_sdk.chain.py_order_utils.model.sides import OrderSide
from opinion_clob_sdk.chain.py_order_utils.model.order_type import LIMIT_ORDER
from logger import autonomous_logger as logger


def retry_with_exponential_backoff(max_retries=3, initial_delay=1.0, max_delay=32.0, backoff_factor=2.0):
    """
    Decorator for retrying functions with exponential backoff on failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds between retries
        max_delay: Maximum delay in seconds between retries
        backoff_factor: Multiplier for delay after each retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    
                    # Don't retry on the last attempt
                    if attempt == max_retries:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts: {e}")
                        raise
                    
                    # Check if it's a rate limit error
                    error_msg = str(e).lower()
                    if 'rate limit' in error_msg or 'too many requests' in error_msg or '429' in error_msg:
                        # For rate limits, use longer backoff
                        delay = min(delay * backoff_factor * 2, max_delay)
                        logger.warning(f"{func.__name__} hit rate limit. Waiting {delay:.1f}s before retry {attempt + 1}/{max_retries}...")
                    else:
                        logger.warning(f"{func.__name__} failed: {e}. Retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})...")
                    
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
                    
            # This shouldn't be reached but just in case
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


class OpinionTradeAPI:
    """
    Official Opinion.trade SDK integration for autonomous AI trading.
    Uses opinion-clob-sdk v0.2.5 with BNB Chain mainnet.
    """
    
    def __init__(self, api_key: Optional[str] = None, private_key: Optional[str] = None):
        """
        Initialize Opinion.trade client with SDK.
        
        Args:
            api_key: Opinion.trade API key (defaults to OPINION_TRADE_API_KEY env var)
            private_key: Wallet private key for signing (defaults to OPINION_WALLET_PRIVATE_KEY env var)
        """
        # Get credentials from parameters or environment
        env_api_key = os.environ.get("OPINION_TRADE_API_KEY", "")
        env_private_key = os.environ.get("OPINION_WALLET_PRIVATE_KEY", "")
        
        self.api_key = api_key or env_api_key
        raw_private_key = private_key or env_private_key
        
        # Normalize private key: add 0x prefix if missing (required by eth_account)
        if raw_private_key and not raw_private_key.startswith('0x'):
            self.private_key = '0x' + raw_private_key
        else:
            self.private_key = raw_private_key
        
        # Derive wallet address from private key
        self.wallet_address = None
        if self.private_key:
            try:
                account = Account.from_key(self.private_key)
                self.wallet_address = account.address
            except Exception as e:
                logger.warning(f"Warning: Could not derive wallet address: {e}")
        
        # Initialize SDK client
        self.client = None
        self._initialize_client()
        
        # Fee cache (1 hour TTL)
        self._cached_fees: Optional[Dict] = None
        self._fees_cache_timestamp: Optional[datetime] = None
        self._fees_cache_ttl_seconds = 3600  # 1 hour
    
    def _initialize_client(self):
        """Initialize Opinion.trade SDK client with production configuration."""
        if not self.api_key or not self.private_key or not self.wallet_address:
            logger.warning("Warning: OpinionTradeAPI initialized without full credentials (read-only mode)")
            return
        
        try:
            # NOTE: multi_sig_addr is set to zero address as a workaround for SDK bug
            # The SDK's default value is empty string '' which causes ValueError in fast_to_checksum_address()
            # TODO: Replace with actual Opinion.trade multi-sig contract address when available from official docs
            # Current workaround allows SDK initialization and basic operations (fetch markets, place orders)
            # If multi-sig-specific operations fail, this address will need to be updated
            self.client = Client(
                host='https://proxy.opinion.trade:8443',
                apikey=self.api_key,
                chain_id=CHAIN_ID_BNB_MAINNET,  # 56
                rpc_url='https://bsc-dataseed.binance.org/',
                private_key=self.private_key,
                multi_sig_addr='0x0000000000000000000000000000000000000000',
                conditional_tokens_addr='0xAD1a38cEc043e70E83a3eC30443dB285ED10D774',
                multisend_addr='0x998739BFdAAdde7C933B942a68053933098f9EDa',
                enable_trading_check_interval=3600,
                quote_tokens_cache_ttl=3600,
                market_cache_ttl=300
            )
            logger.info(f"✓ Opinion.trade SDK initialized (wallet: {self.wallet_address})")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Opinion.trade SDK: {e}")
            self.client = None
    
    @retry_with_exponential_backoff(max_retries=3, initial_delay=2.0, max_delay=30.0)
    def get_available_events(self, limit: int = 200, category: Optional[str] = None) -> Dict:
        """
        Fetch ALL available markets from Opinion.trade using pagination with automatic retry on failure.
        
        Args:
            limit: Maximum total markets to retrieve (default 200, fetched in batches of 20)
            category: Optional category filter (currently not supported by SDK)
        
        Returns:
            Dictionary with success status and list of markets
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Opinion.trade client not initialized',
                'message': 'Please configure OPINION_TRADE_API_KEY and OPINION_WALLET_PRIVATE_KEY'
            }
        
        try:
            all_markets = []
            batch_size = 20  # SDK enforces max 20 per request
            last_error = None
            
            logger.info(f"[PAGINATION] Starting pagination: target={limit} markets, batch_size={batch_size}")
            logger.info(f"[PAGINATION] Fetching BOTH binary and multi-choice markets for maximum coverage")
            
            # Fetch BOTH BINARY and CATEGORICAL markets to get 100-200+ markets
            # Binary: Simple YES/NO markets (e.g., "Will BTC hit $100k?")
            # Categorical: Markets with multiple options (e.g., "Fed Rate Dec" with 4 rate options)
            for topic_type in [TopicType.BINARY, TopicType.CATEGORICAL]:
                page = 1
                topic_type_name = "BINARY" if topic_type == TopicType.BINARY else "CATEGORICAL"
                logger.info(f"[PAGINATION] Fetching {topic_type_name} markets...")
                
                # Fetch markets in batches until we reach the limit or no more markets
                while len(all_markets) < limit:
                    response = self.client.get_markets(
                        topic_type=topic_type,
                        status=TopicStatusFilter.ALL,
                        page=page,
                        limit=batch_size
                    )
                    
                    logger.info(f"[PAGINATION] {topic_type_name} Page {page}: errno={response.errno}, has_result={hasattr(response, 'result')}")
                    
                    if response.errno != 0:
                        logger.warning(f"[PAGINATION] {topic_type_name} error on page {page}: {response.errmsg}")
                        last_error = response.errmsg
                        break
                    
                    markets = response.result.list
                    logger.info(f"[PAGINATION] {topic_type_name} Page {page} returned {len(markets)} markets")
                    
                    if not markets:
                        # No more markets available
                        logger.info(f"[PAGINATION] {topic_type_name} - No more markets found on page {page}, stopping")
                        break
                    
                    # Filter out RESOLVED markets (we can only bet on active markets)
                    # Note: status is an enum, use getattr to get the name (e.g., "RESOLVED" instead of "TopicStatus.RESOLVED")
                    active_markets = [m for m in markets if getattr(m.status, "name", str(m.status)).upper() not in ['RESOLVED', 'CLOSED', 'CANCELLED']]
                    logger.info(f"[PAGINATION] {topic_type_name} Page {page}: {len(active_markets)}/{len(markets)} markets are active (filtered out resolved/closed)")
                    
                    all_markets.extend(active_markets)
                    
                    # If we got fewer than batch_size, we've reached the end
                    if len(markets) < batch_size:
                        logger.info(f"[PAGINATION] {topic_type_name} - Got {len(markets)} < {batch_size}, reached end of markets")
                        break
                    
                    # Stop if we've reached the limit
                    if len(all_markets) >= limit:
                        logger.info(f"[PAGINATION] {topic_type_name} - Reached target limit of {limit} markets")
                        break
                    
                    page += 1
                
                logger.info(f"[PAGINATION] {topic_type_name} complete: collected {len([m for m in all_markets if getattr(m, 'topic_type', None) == topic_type])} markets")
            
            # Check if we got any markets at all
            if not all_markets:
                return {
                    'success': False,
                    'error': last_error or 'No markets available',
                    'events': []
                }
            
            markets = all_markets[:limit]  # Respect the limit
            logger.info(f"[PAGINATION] Pagination complete: fetched {len(all_markets)} markets, returning {len(markets)} (after limit)")
            
            # Convert SDK market objects to our event format
            events = []
            skipped_count = 0
            
            for market in markets:
                try:
                    # Fetch full market details to get options/tokens
                    # NOTE: get_markets() returns markets WITHOUT options field
                    # We need to call get_market(id) for each market to get tokens
                    market_details_response = self.client.get_market(market.market_id)
                    
                    if market_details_response.errno != 0:
                        logger.warning(f"[WARNING] Failed to get details for market {market.market_id}: {market_details_response.errmsg}")
                        skipped_count += 1
                        continue
                    
                    market_full = market_details_response.result.data
                    
                    # Determine market type (BINARY vs MULTIPLE_CHOICE)
                    market_type = getattr(market, 'topic_type', TopicType.BINARY)
                    topic_type_name = getattr(market_type, 'name', str(market_type)) if hasattr(market_type, 'name') else str(market_type)
                    
                    # Derive category from market title (comprehensive keyword matching)
                    title_lower = market.market_title.lower()
                    
                    # Crypto currencies
                    if any(keyword in title_lower for keyword in ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency']):
                        category = 'Crypto'
                    
                    # Interest Rates & Monetary Policy
                    elif any(keyword in title_lower for keyword in ['fomc', 'ecb', 'boj', 'fed', 'federal reserve', 'interest rate', 'rate decision', 'rates decision', 'monetary policy', 'central bank']):
                        category = 'Rates'
                    
                    # Commodities
                    elif any(keyword in title_lower for keyword in ['gold', 'comex', 'silver', 'oil', 'commodity', 'commodities', 'wti', 'brent']):
                        category = 'Commodities'
                    
                    # Inflation & CPI
                    elif any(keyword in title_lower for keyword in ['inflation', 'cpi', 'consumer price', 'pce', 'deflation']):
                        category = 'Inflation'
                    
                    # Employment & Jobs
                    elif any(keyword in title_lower for keyword in ['unemployment', 'jobs', 'payroll', 'employment', 'jobless', 'labor market']):
                        category = 'Employment'
                    
                    # Stock Markets & Finance
                    elif any(keyword in title_lower for keyword in ['stock', 'nasdaq', 's&p', 'dow', 'equity', 'market', 'shares']):
                        category = 'Finance'
                    
                    # Politics & Elections
                    elif any(keyword in title_lower for keyword in ['election', 'vote', 'president', 'congress', 'senate', 'political']):
                        category = 'Politics'
                    
                    # Sports (filtered out later)
                    elif any(keyword in title_lower for keyword in ['sports', 'nfl', 'nba', 'mlb', 'nhl', 'soccer', 'football', 'basketball']):
                        category = 'Sports'
                    
                    # Fallback
                    else:
                        category = 'Other'
                    
                    # Skip Sports category early - we don't want AI agents betting on sports
                    if category == 'Sports':
                        skipped_count += 1
                        logger.info(f"[FILTER] Skipping Sports market: '{market.market_title[:50]}...'")
                        continue
                    
                    # Handle BINARY vs CATEGORICAL markets differently
                    if 'CATEGORICAL' in topic_type_name.upper():
                        # CATEGORICAL market: e.g., "Fed Rate Dec" with 4 options
                        # Each option is a separate YES/NO bet (e.g., "50+ bps decrease" → YES or NO)
                        options = getattr(market_full, 'options', [])
                        
                        if not options:
                            skipped_count += 1
                            logger.warning(f"[WARNING] Skipping CATEGORICAL market {market.market_id} - no options found")
                            continue
                        
                        logger.info(f"[CATEGORICAL] Market '{market.market_title[:40]}...' has {len(options)} options")
                        
                        # Create a separate event for each option
                        for option in options:
                            option_title = getattr(option, 'option_name', getattr(option, 'name', 'Unknown'))
                            yes_token_id = getattr(option, 'yes_token_id', None)
                            no_token_id = getattr(option, 'no_token_id', None)
                            
                            if not yes_token_id or not no_token_id:
                                logger.warning(f"[WARNING] Option '{option_title}' missing tokens, skipping")
                                skipped_count += 1
                                continue
                            
                            # Create event for this specific option
                            events.append({
                                'event_id': f"{market.market_id}_{option_title.replace(' ', '_')}",
                                'market_id': market.market_id,
                                'title': f"{market.market_title} → {option_title}",
                                'description': f"Option: {option_title} | {market.rules if hasattr(market, 'rules') and market.rules else market.market_title}",
                                'category': category,
                                'condition_id': market.condition_id,
                                'status': str(market.status),
                                'quote_token': market.quote_token,
                                'chain_id': market.chain_id,
                                'yes_label': f"YES ({option_title})",
                                'no_label': f"NO ({option_title})",
                                'yes_token_id': yes_token_id,
                                'no_token_id': no_token_id,
                                'volume': getattr(market, 'volume', '0'),
                                'created_at': getattr(market, 'created_at', 0),
                                'cutoff_at': getattr(market, 'cutoff_at', 0)
                            })
                    else:
                        # BINARY market: Simple YES/NO (e.g., "Will BTC hit $100k?")
                        # Opinion.trade SDK stores tokens as direct attributes
                        yes_token_id = getattr(market_full, 'yes_token_id', None)
                        no_token_id = getattr(market_full, 'no_token_id', None)
                        yes_label = getattr(market_full, 'yes_label', 'YES')
                        no_label = getattr(market_full, 'no_label', 'NO')
                        
                        # Skip markets without binary YES/NO tokens
                        if not yes_token_id or not no_token_id:
                            skipped_count += 1
                            logger.warning(f"[WARNING] Skipping BINARY market {market.market_id} '{market.market_title[:50]}...' - missing binary tokens")
                            continue
                        
                        events.append({
                            'event_id': str(market.market_id),
                            'market_id': market.market_id,
                            'title': market.market_title,
                            'description': market.rules if hasattr(market, 'rules') and market.rules else market.market_title,
                            'category': category,
                            'condition_id': market.condition_id,
                            'status': str(market.status),
                            'quote_token': market.quote_token,
                            'chain_id': market.chain_id,
                            'yes_label': yes_label,
                            'no_label': no_label,
                            'yes_token_id': yes_token_id,
                            'no_token_id': no_token_id,
                            'volume': getattr(market, 'volume', '0'),
                            'created_at': getattr(market, 'created_at', 0),
                            'cutoff_at': getattr(market, 'cutoff_at', 0)
                        })
                except Exception as e:
                    logger.error(f"[ERROR] Failed to convert market {getattr(market, 'market_id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"[INFO] Opinion.trade API: Retrieved {len(events)} active markets (skipped {skipped_count} markets - missing tokens or Sports category)")
            return {
                'success': True,
                'count': len(events),
                'events': events,
                'message': f'Retrieved {len(events)} available markets from Opinion.trade (skipped {skipped_count})'
            }
        
        except Exception as e:
            logger.exception(f"[EXCEPTION] Unexpected error in get_available_events: {str(e)}")
            return {
                'success': False,
                'error': 'Unexpected error',
                'message': f'Failed to fetch markets: {str(e)}'
            }
    
    def submit_prediction(self, prediction_data: Dict) -> Dict:
        """
        Submit a prediction to Opinion.trade by placing a limit order.
        
        Args:
            prediction_data: Dictionary containing:
                - market_id: The Opinion.trade market ID
                - token_id: The outcome token ID to buy/sell
                - probability: Float between 0 and 1 (converted to price)
                - amount: Bet amount in USDT
                - side: 'BUY' or 'SELL' (defaults to BUY)
                - metadata: Additional info (firm_name, reasoning, etc.)
        
        Returns:
            Response dictionary with status and order details
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Opinion.trade client not initialized',
                'message': 'Please configure OPINION_TRADE_API_KEY and OPINION_WALLET_PRIVATE_KEY'
            }
        
        try:
            market_id = prediction_data.get('market_id')
            token_id = prediction_data.get('token_id')
            probability = float(prediction_data.get('probability', 0.5))
            amount = float(prediction_data.get('amount', 10))
            side_str = prediction_data.get('side', 'BUY').upper()
            
            # Validate inputs
            if not market_id or not token_id:
                return {
                    'success': False,
                    'error': 'Missing required fields',
                    'message': 'market_id and token_id are required'
                }
            
            # Convert probability to price (probability is the limit price)
            price = str(round(probability, 4))
            
            # Convert side string to OrderSide enum
            side = OrderSide.BUY if side_str == 'BUY' else OrderSide.SELL
            
            # Validate amount is reasonable (min 1 USDT, max based on available balance)
            if amount < 1:
                return {
                    'success': False,
                    'error': 'Invalid amount',
                    'message': 'Minimum bet amount is 1 USDT'
                }
            
            # SDK expects makerAmountInQuoteToken as STRING with USDT value (not wei)
            # Example: "5" for 5 USDT, "10.5" for 10.5 USDT
            # The SDK handles conversion to wei internally
            amount_str = str(amount)
            
            # Create order
            order_data = PlaceOrderDataInput(
                marketId=int(market_id),
                tokenId=str(token_id),
                side=side,
                orderType=LIMIT_ORDER,
                price=price,
                makerAmountInQuoteToken=amount_str  # Amount in USDT as string
            )
            
            # Place order with check_approval=True to ensure trading permissions are enabled
            logger.info(f"[ORDER DEBUG] Placing order: market_id={market_id}, token_id={token_id}, price={price}, amount={amount_str} USDT, side={side_str}")
            result = self.client.place_order(order_data, check_approval=True)
            
            # Check if order was successful
            if hasattr(result, 'errno') and result.errno == 0:
                order_info = result.result if hasattr(result, 'result') else {}
                logger.info(f"[ORDER SUCCESS] Order placed: orderId={getattr(order_info, 'orderId', 'unknown')}")
                return {
                    'success': True,
                    'prediction_id': getattr(order_info, 'orderId', 'unknown'),
                    'message': 'Order placed successfully on Opinion.trade',
                    'data': {
                        'market_id': market_id,
                        'token_id': token_id,
                        'price': price,
                        'amount': amount,
                        'side': side_str,
                        'timestamp': datetime.now().isoformat(),
                        'metadata': prediction_data.get('metadata', {})
                    }
                }
            else:
                error_msg = getattr(result, 'errmsg', str(result))
                error_code = getattr(result, 'errno', 'unknown')
                logger.error(f"[ORDER FAILED] Opinion.trade SDK Error: errno={error_code}, errmsg={error_msg}")
                logger.error(f"[ORDER FAILED] Full result object: {result}")
                return {
                    'success': False,
                    'error': 'Order placement failed',
                    'message': f"SDK Error {error_code}: {error_msg}"
                }
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"[ORDER EXCEPTION] Failed to place order: {str(e)}")
            logger.error(f"[ORDER EXCEPTION] Full traceback:\n{error_trace}")
            return {
                'success': False,
                'error': 'Unexpected error',
                'message': f'Failed to place order: {str(e)}'
            }
    
    def get_account_balance(self) -> Dict:
        """
        Get current account balance from Opinion.trade.
        
        Returns:
            Dictionary with balance information
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Opinion.trade client not initialized'
            }
        
        try:
            balances_response = self.client.get_my_balances()
            
            if balances_response.errno == 0:
                balances = balances_response.result.list
                
                # Sum all balances (typically USDT)
                total_balance = 0
                available_balance = 0
                
                for balance in balances:
                    # Balance amounts are in wei (18 decimals for USDT on BNB Chain)
                    balance_amount = float(getattr(balance, 'balance', 0)) / 1e18
                    available_amount = float(getattr(balance, 'availableBalance', 0)) / 1e18
                    
                    total_balance += balance_amount
                    available_balance += available_amount
                
                return {
                    'success': True,
                    'total_balance': total_balance,
                    'available_balance': available_balance,
                    'locked_balance': total_balance - available_balance,
                    'currency': 'USDT',
                    'wallet_address': self.wallet_address,
                    'data': {
                        'balances': [
                            {
                                'token': getattr(b, 'token', 'USDT'),
                                'balance': float(getattr(b, 'balance', 0)) / 1e18,
                                'available': float(getattr(b, 'availableBalance', 0)) / 1e18
                            }
                            for b in balances
                        ]
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'API error {balances_response.errno}',
                    'message': balances_response.errmsg
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': 'Unexpected error',
                'message': f'Failed to fetch balance: {str(e)}'
            }
    
    def get_active_positions(self) -> Dict:
        """
        Get all active trading positions from Opinion.trade.
        
        Returns:
            Dictionary with list of active positions
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Opinion.trade client not initialized'
            }
        
        try:
            positions_response = self.client.get_my_positions(limit=100)
            
            if positions_response.errno == 0:
                positions = positions_response.result.list
                
                # Convert positions to our format
                formatted_positions = []
                total_exposure = 0
                
                for position in positions:
                    amount = float(getattr(position, 'amount', 0)) / 1e18
                    total_exposure += amount
                    
                    formatted_positions.append({
                        'market_id': getattr(position, 'marketId', None),
                        'token_id': getattr(position, 'tokenId', None),
                        'amount': amount,
                        'outcome': getattr(position, 'outcome', None),
                        'status': getattr(position, 'status', 'active')
                    })
                
                return {
                    'success': True,
                    'count': len(formatted_positions),
                    'positions': formatted_positions,
                    'total_exposure': total_exposure
                }
            else:
                return {
                    'success': False,
                    'error': f'API error {positions_response.errno}',
                    'message': positions_response.errmsg
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': 'Unexpected error',
                'message': f'Failed to fetch positions: {str(e)}'
            }
    
    def get_market_details(self, market_id: int) -> Dict:
        """
        Get detailed information about a specific market.
        
        Args:
            market_id: The Opinion.trade market ID
        
        Returns:
            Market details or error dictionary
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Opinion.trade client not initialized'
            }
        
        try:
            response = self.client.get_market(market_id)
            
            if response.errno == 0:
                market = response.result.data
                return {
                    'success': True,
                    'data': {
                        'market_id': market.marketId,
                        'title': market.marketTitle,
                        'description': getattr(market, 'marketDescription', ''),
                        'condition_id': market.conditionId,
                        'status': market.status,
                        'quote_token': market.quoteToken,
                        'chain_id': market.chainId,
                        'options': getattr(market, 'options', [])
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'API error {response.errno}',
                    'message': response.errmsg
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': 'Unexpected error',
                'message': str(e)
            }
    
    def get_orderbook(self, token_id: str) -> Dict:
        """
        Get orderbook for a specific outcome token.
        
        Args:
            token_id: The outcome token ID
        
        Returns:
            Orderbook data or error dictionary
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Opinion.trade client not initialized'
            }
        
        try:
            response = self.client.get_orderbook(token_id)
            
            if response.errno == 0:
                # SDK returns response.result directly (not response.result.data)
                book = response.result if hasattr(response, 'result') else None
                
                if not book:
                    logger.warning(f"get_orderbook: No result data for token_id={token_id}")
                    return {
                        'success': False,
                        'error': 'No orderbook data',
                        'message': 'SDK returned success but no orderbook result'
                    }
                
                # Extract bids and asks - handle both dict and object responses
                if isinstance(book, dict):
                    raw_bids = book.get('bids', []) or []
                    raw_asks = book.get('asks', []) or []
                else:
                    raw_bids = getattr(book, 'bids', []) or []
                    raw_asks = getattr(book, 'asks', []) or []
                
                # Normalize each bid/ask entry to consistent dict format
                def normalize_order_entry(entry):
                    """Convert SDK order entry (dict or object) to normalized dict."""
                    if not entry:
                        return None
                    
                    normalized = {}
                    
                    # Extract price
                    if isinstance(entry, dict):
                        normalized['price'] = entry.get('price', 0)
                        normalized['amount'] = entry.get('amount', 0)
                    else:
                        normalized['price'] = getattr(entry, 'price', 0)
                        normalized['amount'] = getattr(entry, 'amount', 0)
                    
                    # Ensure price is numeric
                    try:
                        normalized['price'] = float(normalized['price']) if normalized['price'] else 0.0
                        normalized['amount'] = float(normalized['amount']) if normalized['amount'] else 0.0
                    except (ValueError, TypeError):
                        normalized['price'] = 0.0
                        normalized['amount'] = 0.0
                    
                    return normalized
                
                # Normalize all bids and asks
                bids = [normalize_order_entry(bid) for bid in raw_bids]
                asks = [normalize_order_entry(ask) for ask in raw_asks]
                
                # Filter out invalid entries (price = 0)
                bids = [b for b in bids if b and b.get('price', 0) > 0]
                asks = [a for a in asks if a and a.get('price', 0) > 0]
                
                logger.info(f"get_orderbook: token_id={token_id}, bids_count={len(bids)}, asks_count={len(asks)}")
                
                return {
                    'success': True,
                    'data': {
                        'bids': bids,
                        'asks': asks,
                        'best_bid': bids[0] if bids else None,
                        'best_ask': asks[0] if asks else None
                    }
                }
            else:
                logger.warning(f"get_orderbook: API error for token_id={token_id}: errno={response.errno}, errmsg={response.errmsg}")
                return {
                    'success': False,
                    'error': f'API error {response.errno}',
                    'message': response.errmsg
                }
        
        except Exception as e:
            logger.error(f"get_orderbook: Exception for token_id={token_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Unexpected error',
                'message': str(e)
            }
    
    def get_fee_rates(self, use_cache: bool = True) -> Dict:
        """
        Get current trading fee rates from Opinion.trade with caching.
        
        Args:
            use_cache: Whether to use cached fees (default True)
        
        Returns:
            Dictionary with maker and taker fees
        """
        # Check cache if enabled
        if use_cache and self._cached_fees and self._fees_cache_timestamp:
            cache_age = (datetime.now() - self._fees_cache_timestamp).total_seconds()
            if cache_age < self._fees_cache_ttl_seconds:
                return self._cached_fees
        
        if not self.client:
            return {
                'success': False,
                'error': 'Opinion.trade client not initialized'
            }
        
        try:
            response = self.client.get_fee_rates()
            
            if response.errno == 0:
                fees = response.result.data
                result = {
                    'success': True,
                    'maker_fee': float(getattr(fees, 'makerFee', 0)) / 10000,  # Convert basis points to decimal
                    'taker_fee': float(getattr(fees, 'takerFee', 0)) / 10000,
                    'data': fees
                }
                
                # Update cache
                self._cached_fees = result
                self._fees_cache_timestamp = datetime.now()
                
                return result
            else:
                return {
                    'success': False,
                    'error': f'API error {response.errno}',
                    'message': response.errmsg
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': 'Unexpected error',
                'message': str(e)
            }
    
    def _extract_price(self, order_entry) -> float:
        """
        Helper to extract price from orderbook entry with defensive error handling.
        
        Note: get_orderbook() now normalizes entries to dicts, so this handles
        the normalized format while being defensive against any edge cases.
        
        Args:
            order_entry: Normalized bid/ask entry from orderbook (should be dict with 'price' key)
        
        Returns:
            Price as float, or 0.0 if invalid/missing
        """
        if not order_entry:
            return 0.0
        
        try:
            # Handle normalized dict format (primary path)
            if isinstance(order_entry, dict):
                price = order_entry.get('price', 0)
            else:
                # Fallback for object attributes (shouldn't happen after normalization)
                price = getattr(order_entry, 'price', 0)
            
            # Defensive conversion to float
            if price is None or price == '':
                return 0.0
            
            return float(price)
        
        except (ValueError, TypeError, AttributeError) as e:
            # Log anomaly for observability but don't crash
            logger.warning(f"_extract_price: Could not extract price from {type(order_entry)}: {e}")
            return 0.0
    
    def get_latest_price(self, token_id: str) -> Dict:
        """
        Get the latest price for a specific outcome token.
        
        WORKAROUND: SDK's get_latest_price() has bug (error 10004: "needs a pointer to a slice or a map")
        Using get_orderbook() instead to fetch best bid/ask and calculate mid-price.
        This is actually better as it shows current market state rather than last trade.
        
        Args:
            token_id: The outcome token ID
        
        Returns:
            Latest price data or error dictionary
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Opinion.trade client not initialized'
            }
        
        try:
            # WORKAROUND: Use orderbook instead of buggy get_latest_price SDK method
            orderbook_response = self.get_orderbook(token_id)
            
            if not orderbook_response.get('success'):
                logger.warning(f"get_latest_price: orderbook fetch failed for token_id={token_id}: {orderbook_response.get('message', 'Unknown error')}")
                return {
                    'success': False,
                    'error': orderbook_response.get('error', 'Orderbook fetch failed'),
                    'message': orderbook_response.get('message', 'Could not fetch orderbook'),
                    'token_id': token_id
                }
            
            orderbook = orderbook_response.get('data', {})
            best_bid = orderbook.get('best_bid')
            best_ask = orderbook.get('best_ask')
            
            # Calculate mid-price from best bid/ask (handle both dict and object)
            if best_bid and best_ask:
                bid_price = self._extract_price(best_bid)
                ask_price = self._extract_price(best_ask)
                
                if bid_price > 0 and ask_price > 0:
                    mid_price = (bid_price + ask_price) / 2.0
                    logger.info(f"get_latest_price: token_id={token_id}, bid={bid_price}, ask={ask_price}, mid={mid_price}")
                    return {
                        'success': True,
                        'price': mid_price,
                        'bid_price': bid_price,
                        'ask_price': ask_price,
                        'spread': ask_price - bid_price,
                        'timestamp': int(datetime.now().timestamp()),
                        'data': {'source': 'orderbook', 'bid': best_bid, 'ask': best_ask}
                    }
            
            # Fallback: if only bid or only ask available
            if best_bid:
                bid_price = self._extract_price(best_bid)
                if bid_price > 0:
                    logger.info(f"get_latest_price: token_id={token_id}, using bid_price={bid_price} (no ask available)")
                    return {
                        'success': True,
                        'price': bid_price,
                        'bid_price': bid_price,
                        'timestamp': int(datetime.now().timestamp()),
                        'data': {'source': 'orderbook_bid_only', 'bid': best_bid}
                    }
            
            if best_ask:
                ask_price = self._extract_price(best_ask)
                if ask_price > 0:
                    logger.info(f"get_latest_price: token_id={token_id}, using ask_price={ask_price} (no bid available)")
                    return {
                        'success': True,
                        'price': ask_price,
                        'ask_price': ask_price,
                        'timestamp': int(datetime.now().timestamp()),
                        'data': {'source': 'orderbook_ask_only', 'ask': best_ask}
                    }
            
            # No valid prices found
            logger.warning(f"get_latest_price: token_id={token_id} - No valid bid/ask prices in orderbook")
            return {
                'success': False,
                'error': 'No market price available',
                'message': 'Orderbook has no valid bid or ask prices',
                'token_id': token_id
            }
        
        except Exception as e:
            logger.error(f"get_latest_price exception for token_id={token_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Unexpected error',
                'message': str(e),
                'token_id': token_id
            }
    
    def get_my_orders(self, market_id: Optional[int] = None) -> Dict:
        """
        Get active/pending orders from Opinion.trade.
        
        Args:
            market_id: Optional market ID to filter orders
        
        Returns:
            Dictionary with list of active orders
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Opinion.trade client not initialized'
            }
        
        try:
            response = self.client.get_my_orders()
            
            if response.errno == 0:
                orders = response.result.list
                
                # Filter by market_id if provided
                if market_id is not None:
                    orders = [o for o in orders if getattr(o, 'marketId', None) == market_id]
                
                formatted_orders = []
                for order in orders:
                    formatted_orders.append({
                        'order_id': getattr(order, 'orderId', None),
                        'market_id': getattr(order, 'marketId', None),
                        'token_id': getattr(order, 'tokenId', None),
                        'side': getattr(order, 'side', None),
                        'price': float(getattr(order, 'price', 0)),
                        'amount': float(getattr(order, 'amount', 0)) / 1e18,
                        'status': getattr(order, 'status', 'unknown'),
                        'created_at': getattr(order, 'createdAt', 0)
                    })
                
                return {
                    'success': True,
                    'count': len(formatted_orders),
                    'orders': formatted_orders
                }
            else:
                return {
                    'success': False,
                    'error': f'API error {response.errno}',
                    'message': response.errmsg
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': 'Unexpected error',
                'message': str(e)
            }
    
    def get_price_history(self, market_id: int, timeframe: str = '24h') -> Dict:
        """
        Get historical price data for a market.
        
        Args:
            market_id: The Opinion.trade market ID
            timeframe: Time range (e.g., '1h', '24h', '7d')
        
        Returns:
            Price history data or error dictionary
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Opinion.trade client not initialized'
            }
        
        try:
            # Get market details to get token IDs
            market_response = self.get_market_details(market_id)
            if not market_response.get('success'):
                return market_response
            
            options = market_response['data'].get('options', [])
            if not options:
                return {
                    'success': False,
                    'error': 'No options found',
                    'message': 'Market has no outcome tokens'
                }
            
            # Get price history for first token (YES token typically)
            token_id = getattr(options[0], 'token_id', None) if options else None
            if not token_id:
                return {
                    'success': False,
                    'error': 'No token ID',
                    'message': 'Could not extract token ID from market options'
                }
            
            response = self.client.get_price_history(token_id)
            
            if response.errno == 0:
                history = response.result.list
                
                formatted_history = []
                for point in history:
                    formatted_history.append({
                        'timestamp': getattr(point, 'timestamp', 0),
                        'price': float(getattr(point, 'price', 0)),
                        'volume': float(getattr(point, 'volume', 0)) / 1e18
                    })
                
                return {
                    'success': True,
                    'market_id': market_id,
                    'token_id': token_id,
                    'timeframe': timeframe,
                    'history': formatted_history
                }
            else:
                return {
                    'success': False,
                    'error': f'API error {response.errno}',
                    'message': response.errmsg
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': 'Unexpected error',
                'message': str(e)
            }
    
    def get_my_trades(self, limit: int = 50, market_id: Optional[int] = None) -> Dict:
        """
        Get historical trades executed by this account.
        
        Args:
            limit: Maximum number of trades to return (default 50)
            market_id: Optional market ID to filter trades
        
        Returns:
            Dictionary with list of historical trades
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Opinion.trade client not initialized'
            }
        
        try:
            response = self.client.get_my_trades(limit=limit)
            
            if response.errno == 0:
                trades = response.result.list
                
                # Filter by market_id if provided
                if market_id is not None:
                    trades = [t for t in trades if getattr(t, 'marketId', None) == market_id]
                
                formatted_trades = []
                for trade in trades:
                    formatted_trades.append({
                        'trade_id': getattr(trade, 'tradeId', None),
                        'order_id': getattr(trade, 'orderId', None),
                        'market_id': getattr(trade, 'marketId', None),
                        'token_id': getattr(trade, 'tokenId', None),
                        'side': getattr(trade, 'side', None),
                        'price': float(getattr(trade, 'price', 0)),
                        'amount': float(getattr(trade, 'amount', 0)) / 1e18,
                        'fee': float(getattr(trade, 'fee', 0)) / 1e18,
                        'timestamp': getattr(trade, 'timestamp', 0),
                        'status': getattr(trade, 'status', 'unknown')
                    })
                
                return {
                    'success': True,
                    'count': len(formatted_trades),
                    'trades': formatted_trades
                }
            else:
                return {
                    'success': False,
                    'errno': response.errno,
                    'error': f'API error {response.errno}',
                    'message': response.errmsg
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': 'Unexpected error',
                'message': str(e)
            }
    
    def redeem(self, token_ids: List[str]) -> Dict:
        """
        Redeem winning tokens from resolved markets.
        
        Args:
            token_ids: List of token IDs to redeem
        
        Returns:
            Redemption result or error dictionary
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Opinion.trade client not initialized'
            }
        
        try:
            response = self.client.redeem(token_ids)
            
            if response.errno == 0:
                return {
                    'success': True,
                    'message': 'Tokens redeemed successfully',
                    'data': response.result
                }
            else:
                return {
                    'success': False,
                    'error': f'API error {response.errno}',
                    'message': response.errmsg
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': 'Unexpected error',
                'message': str(e)
            }
    
    def cancel_order(self, order_id: str) -> Dict:
        """
        Cancel a specific pending order.
        
        Args:
            order_id: The order ID to cancel
        
        Returns:
            Cancellation result or error dictionary
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Opinion.trade client not initialized'
            }
        
        try:
            response = self.client.cancel_order(order_id)
            
            if response.errno == 0:
                return {
                    'success': True,
                    'message': f'Order {order_id} cancelled successfully',
                    'data': response.result
                }
            else:
                return {
                    'success': False,
                    'error': f'API error {response.errno}',
                    'message': response.errmsg
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': 'Unexpected error',
                'message': str(e)
            }
    
    def cancel_all_orders(self, market_id: Optional[int] = None) -> Dict:
        """
        Cancel all pending orders, optionally filtered by market.
        
        Args:
            market_id: Optional market ID to cancel only orders in that market
        
        Returns:
            Cancellation result or error dictionary
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Opinion.trade client not initialized'
            }
        
        try:
            response = self.client.cancel_all_orders()
            
            if response.errno == 0:
                cancelled_count = getattr(response.result, 'cancelledCount', 0)
                return {
                    'success': True,
                    'message': f'Cancelled {cancelled_count} orders',
                    'cancelled_count': cancelled_count,
                    'data': response.result
                }
            else:
                return {
                    'success': False,
                    'error': f'API error {response.errno}',
                    'message': response.errmsg
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': 'Unexpected error',
                'message': str(e)
            }


# Backward compatibility aliases
def get_event_details(event_id: str) -> Dict:
    """Legacy method - use get_market_details instead."""
    api = OpinionTradeAPI()
    try:
        market_id = int(event_id)
        return api.get_market_details(market_id)
    except ValueError:
        return {
            'success': False,
            'error': 'Invalid market_id',
            'message': 'market_id must be a valid integer'
        }


def get_prediction_result(prediction_id: str) -> Dict:
    """
    Legacy method - Opinion.trade SDK does not have direct prediction result lookup.
    Use get_my_trades() or get_my_positions() instead.
    """
    return {
        'success': False,
        'error': 'Method not supported',
        'message': 'Use get_my_positions() or get_my_trades() to track outcomes'
    }
