import os
from typing import Dict, Optional, List
from datetime import datetime
from eth_account import Account

from opinion_clob_sdk import Client, CHAIN_ID_BNB_MAINNET
from opinion_clob_sdk.model import TopicType, TopicStatusFilter
from opinion_clob_sdk.chain.py_order_utils.model.order import PlaceOrderDataInput
from opinion_clob_sdk.chain.py_order_utils.model.sides import OrderSide
from opinion_clob_sdk.chain.py_order_utils.model.order_type import LIMIT_ORDER
from logger import autonomous_logger as logger


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
        self.api_key = api_key or os.environ.get("OPINION_TRADE_API_KEY", "")
        self.private_key = private_key or os.environ.get("OPINION_WALLET_PRIVATE_KEY", "")
        
        # Derive wallet address from private key
        self.wallet_address = None
        if self.private_key:
            try:
                account = Account.from_key(self.private_key)
                self.wallet_address = account.address
            except Exception as e:
                print(f"Warning: Could not derive wallet address: {e}")
        
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
            print("Warning: OpinionTradeAPI initialized without full credentials (read-only mode)")
            return
        
        try:
            self.client = Client(
                host='https://proxy.opinion.trade:8443',
                apikey=self.api_key,
                chain_id=CHAIN_ID_BNB_MAINNET,  # 56
                rpc_url='https://bsc-dataseed.binance.org/',
                private_key=self.private_key,
                multi_sig_addr=self.wallet_address,
                conditional_tokens_addr='0xAD1a38cEc043e70E83a3eC30443dB285ED10D774',
                multisend_addr='0x998739BFdAAdde7C933B942a68053933098f9EDa',
                enable_trading_check_interval=3600,
                quote_tokens_cache_ttl=3600,
                market_cache_ttl=300
            )
            print(f"✓ Opinion.trade SDK initialized (wallet: {self.wallet_address})")
        except Exception as e:
            print(f"✗ Failed to initialize Opinion.trade SDK: {e}")
            self.client = None
    
    def get_available_events(self, limit: int = 20, category: Optional[str] = None) -> Dict:
        """
        Fetch list of available markets from Opinion.trade for autonomous betting.
        
        Args:
            limit: Maximum number of markets to retrieve (default 20, max 20 per SDK limit)
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
            # Get active binary markets (SDK max limit: 20)
            response = self.client.get_markets(
                topic_type=TopicType.BINARY,
                status=TopicStatusFilter.ACTIVATED,
                page=1,
                limit=min(limit, 20)  # SDK enforces max 20
            )
            
            print(f"[DEBUG] Opinion.trade API response - errno: {response.errno}, has result: {hasattr(response, 'result')}")
            
            if response.errno == 0:
                markets = response.result.list
                print(f"[DEBUG] Opinion.trade returned {len(markets)} raw markets from API")
                
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
                            print(f"[WARNING] Failed to get details for market {market.market_id}: {market_details_response.errmsg}")
                            skipped_count += 1
                            continue
                        
                        market_full = market_details_response.result.data
                        
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
                        
                        # Extract token IDs directly from market attributes
                        # Opinion.trade SDK stores tokens as direct attributes, not in an options array
                        yes_token_id = getattr(market_full, 'yes_token_id', None)
                        no_token_id = getattr(market_full, 'no_token_id', None)
                        yes_label = getattr(market_full, 'yes_label', 'YES')
                        no_label = getattr(market_full, 'no_label', 'NO')
                        
                        # Skip markets without binary YES/NO tokens
                        if not yes_token_id or not no_token_id:
                            skipped_count += 1
                            print(f"[WARNING] Skipping market {market.market_id} '{market.market_title[:50]}...' - missing binary tokens (yes={yes_token_id}, no={no_token_id})")
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
                            'yes_label': getattr(market, 'yes_label', 'YES'),
                            'no_label': getattr(market, 'no_label', 'NO'),
                            'yes_token_id': yes_token_id,
                            'no_token_id': no_token_id,
                            'volume': getattr(market, 'volume', '0'),
                            'created_at': getattr(market, 'created_at', 0),
                            'cutoff_at': getattr(market, 'cutoff_at', 0)
                        })
                    except Exception as e:
                        print(f"[ERROR] Failed to convert market {getattr(market, 'market_id', 'unknown')}: {e}")
                        continue
                
                print(f"[INFO] Opinion.trade API: Retrieved {len(events)} active markets (skipped {skipped_count} without YES/NO tokens)")
                return {
                    'success': True,
                    'count': len(events),
                    'events': events,
                    'message': f'Retrieved {len(events)} available markets from Opinion.trade (skipped {skipped_count})'
                }
            else:
                # Handle specific error codes
                error_msg = response.errmsg
                if response.errno == 10403 and "Invalid area" in error_msg:
                    error_msg = (
                        "Geographic restriction detected. Opinion.trade API blocked this request. "
                        "This code must run from Railway deployment in US West region (not from Replit). "
                        "Please ensure you're running this from the Railway production environment."
                    )
                
                return {
                    'success': False,
                    'error': f'API error {response.errno}',
                    'message': error_msg
                }
        
        except Exception as e:
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
            
            # Convert USDT amount to base units (wei) - USDT on BNB Chain uses 18 decimals
            # Example: 10 USDT → 10000000000000000000 wei
            amount_in_wei = int(amount * 1e18)
            
            # Validate amount is reasonable (min 1 USDT, max based on available balance)
            if amount < 1:
                return {
                    'success': False,
                    'error': 'Invalid amount',
                    'message': 'Minimum bet amount is 1 USDT'
                }
            
            # Enable trading if not already enabled (required before first order)
            try:
                self.client.enable_trading()
            except Exception as e:
                # Already enabled or error - continue anyway
                print(f"Note: enable_trading() response: {e}")
            
            # Create order
            order_data = PlaceOrderDataInput(
                marketId=int(market_id),
                tokenId=str(token_id),
                side=side,
                orderType=LIMIT_ORDER,
                price=price,
                makerAmountInQuoteToken=amount_in_wei  # Amount in wei (base units)
            )
            
            # Place order
            result = self.client.place_order(order_data)
            
            # Check if order was successful
            if hasattr(result, 'errno') and result.errno == 0:
                order_info = result.result if hasattr(result, 'result') else {}
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
                return {
                    'success': False,
                    'error': 'Order placement failed',
                    'message': error_msg
                }
        
        except Exception as e:
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
