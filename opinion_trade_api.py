import os
from typing import Dict, Optional, List
from datetime import datetime
from eth_account import Account

from opinion_clob_sdk import Client, CHAIN_ID_BNB_MAINNET
from opinion_clob_sdk.model import TopicType, TopicStatusFilter
from opinion_clob_sdk.chain.py_order_utils.model.order import PlaceOrderDataInput
from opinion_clob_sdk.chain.py_order_utils.model.sides import OrderSide
from opinion_clob_sdk.chain.py_order_utils.model.order_type import LIMIT_ORDER


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
            
            if response.errno == 0:
                markets = response.result.list
                
                # Convert SDK market objects to our event format
                events = []
                for market in markets:
                    events.append({
                        'event_id': str(market.market_id),
                        'market_id': market.market_id,
                        'title': market.market_title,
                        'description': getattr(market, 'market_description', ''),
                        'category': getattr(market, 'category', 'Unknown'),
                        'condition_id': market.condition_id,
                        'status': market.status,
                        'quote_token': market.quote_token,
                        'chain_id': market.chain_id,
                        'topic_id': market.topic_id,
                        'options': getattr(market, 'options', [])
                    })
                
                print(f"[INFO] Opinion.trade API: Retrieved {len(events)} active markets")
                return {
                    'success': True,
                    'count': len(events),
                    'events': events,
                    'message': f'Retrieved {len(events)} available markets from Opinion.trade'
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
                book = response.result.data
                return {
                    'success': True,
                    'data': {
                        'bids': getattr(book, 'bids', []),
                        'asks': getattr(book, 'asks', []),
                        'best_bid': book.bids[0] if book.bids else None,
                        'best_ask': book.asks[0] if book.asks else None
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
