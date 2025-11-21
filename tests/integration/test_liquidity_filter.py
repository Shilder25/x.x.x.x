"""
Integration test for liquidity filter bug fix
Tests that markets without yes_token_id are properly skipped BEFORE liquidity check
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock

# Set dummy env vars to avoid real SDK initialization
os.environ['OPINION_TRADE_API_KEY'] = 'test_key_123'
os.environ['OPINION_WALLET_PRIVATE_KEY'] = '0x' + '1' * 64

from opinion_trade_api import OpinionTradeAPI

class TestLiquidityFilterFix:
    """
    Test suite for the critical liquidity filter bug fix
    
    BUG: Binary markets without yes_token_id were passing the liquidity filter
         but failing later when trying to create events
    
    FIX: Skip markets without yes_token_id BEFORE checking liquidity
    """
    
    @patch('opinion_trade_api.OpinionTradeAPI._initialize_client')
    def test_binary_market_without_token_is_skipped_early(self, mock_init):
        """
        Verify that binary markets without yes_token_id are skipped
        BEFORE attempting to check orderbook liquidity
        """
        # Initialize API (bypasses real SDK init via patch)
        api = OpinionTradeAPI()
        
        # Setup mock client manually
        mock_client = Mock()
        api.client = mock_client
        
        # Mock get_markets response (pagination disabled for test)
        mock_markets_response = Mock()
        mock_markets_response.errno = 0
        mock_markets_response.result.data = []  # Empty first page to disable pagination
        mock_client.get_markets.return_value = mock_markets_response
        
        # Create a binary market WITHOUT yes_token_id
        mock_market = Mock()
        mock_market.market_id = 12345
        mock_market.market_title = "Test Binary Market Without Token"
        mock_market.topic_type = Mock()
        mock_market.topic_type.name = "BINARY"
        
        # Mock get_market response for details (no yes_token_id)
        mock_details_response = Mock()
        mock_details_response.errno = 0
        mock_market_full = Mock()
        mock_market_full.yes_token_id = None  # CRITICAL: No token
        mock_market_full.options = None
        mock_details_response.result.data = mock_market_full
        mock_client.get_market.return_value = mock_details_response
        
        # Override the empty markets list for this test
        mock_markets_response.result.data = [mock_market]
        
        # Call get_active_events
        response = api.get_active_events(limit=10)
        
        # ASSERTIONS
        # 1. Should succeed (no crashes)
        assert response.get('success') == True
        
        # 2. Should return empty events (market was skipped)
        assert len(response.get('events', [])) == 0
        
        # 3. Should have logged skip reason
        # (Check that get_orderbook was NEVER called - market skipped before liquidity check)
        assert not mock_client.get_orderbook.called, \
            "get_orderbook should NOT be called for markets without yes_token_id"
    
    @patch('opinion_trade_api.OpinionTradeAPI._initialize_client')
    def test_binary_market_with_token_checks_liquidity(self, mock_init):
        """
        Verify that binary markets WITH yes_token_id proceed to liquidity check
        """
        # Initialize API
        api = OpinionTradeAPI()
        
        # Setup mock client
        mock_client = Mock()
        api.client = mock_client
        
        # Mock get_markets response (pagination disabled)
        mock_markets_response = Mock()
        mock_markets_response.errno = 0
        mock_markets_response.result.data = []
        mock_client.get_markets.return_value = mock_markets_response
        
        # Create a binary market WITH yes_token_id
        mock_market = Mock()
        mock_market.market_id = 12346
        mock_market.market_title = "Test Binary Market With Token"
        mock_market.topic_type = Mock()
        mock_market.topic_type.name = "BINARY"
        
        # Mock get_market response for details (HAS yes_token_id)
        mock_details_response = Mock()
        mock_details_response.errno = 0
        mock_market_full = Mock()
        mock_market_full.yes_token_id = "0xABCD1234"  # CRITICAL: Has token
        mock_market_full.no_token_id = "0xEF567890"
        mock_market_full.options = None
        mock_details_response.result.data = mock_market_full
        mock_client.get_market.return_value = mock_details_response
        
        # Mock orderbook response (has liquidity)
        mock_orderbook_response = Mock()
        mock_orderbook_response.errno = 0
        mock_orderbook_response.result.data.bids = [{"price": "0.5", "amount": "100"}]
        mock_orderbook_response.result.data.asks = []
        mock_client.get_orderbook.return_value = mock_orderbook_response
        
        # Override markets list
        mock_markets_response.result.data = [mock_market]
        
        # Call get_active_events
        response = api.get_active_events(limit=10)
        
        # ASSERTIONS
        # 1. Should succeed
        assert response.get('success') == True
        
        # 2. Should call get_orderbook (liquidity check happened)
        assert mock_client.get_orderbook.called, \
            "get_orderbook SHOULD be called for markets with yes_token_id"
        
        # 3. Market should pass through (has liquidity)
        events = response.get('events', [])
        assert len(events) == 1, "Market with token and liquidity should not be skipped"
        assert events[0]['yes_token_id'] == "0xABCD1234"
    
    @patch('opinion_trade_api.OpinionTradeAPI._initialize_client')
    def test_categorical_market_without_options_is_skipped(self, mock_init):
        """
        Verify that categorical markets without options are skipped
        """
        # Initialize API
        api = OpinionTradeAPI()
        
        # Setup mock client
        mock_client = Mock()
        api.client = mock_client
        
        # Mock responses
        mock_markets_response = Mock()
        mock_markets_response.errno = 0
        mock_markets_response.result.data = []
        mock_client.get_markets.return_value = mock_markets_response
        
        # Create categorical market without options
        mock_market = Mock()
        mock_market.market_id = 12347
        mock_market.market_title = "Test Categorical Market Without Options"
        mock_market.topic_type = Mock()
        mock_market.topic_type.name = "CATEGORICAL"
        
        mock_details_response = Mock()
        mock_details_response.errno = 0
        mock_market_full = Mock()
        mock_market_full.options = []  # Empty options
        mock_details_response.result.data = mock_market_full
        mock_client.get_market.return_value = mock_details_response
        
        mock_markets_response.result.data = [mock_market]
        
        # Call get_active_events
        response = api.get_active_events(limit=10)
        
        # ASSERTIONS
        assert response.get('success') == True
        assert len(response.get('events', [])) == 0, \
            "Categorical market without options should be skipped"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
