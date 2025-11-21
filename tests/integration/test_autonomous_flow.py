"""
Integration test for autonomous trading flow
Tests the complete cycle: fetch markets → analyze → predict → execute
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from autonomous_engine import AutonomousEngine
from opinion_trade_api import OpinionTradeAPI

class TestAutonomousFlow:
    """
    Test suite for autonomous trading flow
    Verifies that the complete pipeline works end-to-end
    """
    
    @patch('autonomous_engine.LLMIntegration')
    @patch('autonomous_engine.OpinionTradeAPI')
    def test_autonomous_cycle_with_liquid_markets(self, mock_api_class, mock_llm_class):
        """
        Test that autonomous cycle processes liquid markets correctly
        """
        # Setup mocks
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        # Mock get_active_events to return 1 liquid market
        mock_api.get_active_events.return_value = {
            'success': True,
            'events': [{
                'event_id': 'test-123',
                'title': 'Bitcoin to $100k by Dec 2024?',
                'description': 'Will Bitcoin reach $100,000 by December 31, 2024?',
                'category': 'Crypto',
                'yes_token_id': '0xABCD1234',
                'no_token_id': '0xEF567890',
                'is_binary': True,
                'end_time': '2024-12-31T23:59:59Z',
                'liquidity_score': 0.8
            }]
        }
        
        # Mock get_balance
        mock_api.get_balance.return_value = {
            'success': True,
            'total_balance': 50.0
        }
        
        # Mock AI prediction (positive EV)
        mock_llm.generate_prediction.return_value = {
            'success': True,
            'predictions': [{
                'firm_name': 'ChatGPT-Firm',
                'probability': 0.65,
                'confidence': 0.75,
                'reasoning': 'Strong uptrend...',
                'recommended_side': 'YES',
                'expected_value': 0.15  # Positive EV
            }]
        }
        
        # Mock order placement
        mock_api.submit_prediction.return_value = {
            'success': True,
            'order_id': 'order-abc123'
        }
        
        # Create engine
        engine = AutonomousEngine(simulation_mode=False)
        
        # Run cycle
        result = engine.run_cycle()
        
        # ASSERTIONS
        assert result.get('success') == True, "Cycle should succeed"
        assert mock_api.get_active_events.called, "Should fetch markets"
        assert mock_llm.generate_prediction.called, "Should call AI for prediction"
        
        # Verify prediction was attempted (may or may not execute based on Risk Guard)
        # This test validates the FLOW, not necessarily execution
    
    @patch('autonomous_engine.LLMIntegration')
    @patch('autonomous_engine.OpinionTradeAPI')
    def test_autonomous_cycle_skips_negative_ev(self, mock_api_class, mock_llm_class):
        """
        Test that markets with negative EV are skipped
        """
        # Setup mocks
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        # Mock market
        mock_api.get_active_events.return_value = {
            'success': True,
            'events': [{
                'event_id': 'test-456',
                'title': 'Test Market',
                'category': 'Crypto',
                'yes_token_id': '0x1234',
                'no_token_id': '0x5678',
                'is_binary': True
            }]
        }
        
        mock_api.get_balance.return_value = {
            'success': True,
            'total_balance': 50.0
        }
        
        # Mock AI prediction with NEGATIVE EV
        mock_llm.generate_prediction.return_value = {
            'success': True,
            'predictions': [{
                'firm_name': 'ChatGPT-Firm',
                'probability': 0.45,
                'confidence': 0.70,
                'reasoning': 'Overpriced...',
                'recommended_side': 'NO',
                'expected_value': -0.05  # NEGATIVE EV
            }]
        }
        
        # Create engine
        engine = AutonomousEngine(simulation_mode=False)
        
        # Run cycle
        result = engine.run_cycle()
        
        # ASSERTIONS
        # Should succeed but NOT place any orders
        assert result.get('success') == True
        assert not mock_api.submit_prediction.called, \
            "Should NOT place orders for negative EV markets"
    
    @patch('autonomous_engine.OpinionTradeAPI')
    def test_cycle_handles_empty_markets_gracefully(self, mock_api_class):
        """
        Test that cycle handles zero markets without crashing
        """
        # Setup mock
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        
        # Mock EMPTY markets
        mock_api.get_active_events.return_value = {
            'success': True,
            'events': []  # No markets
        }
        
        mock_api.get_balance.return_value = {
            'success': True,
            'total_balance': 50.0
        }
        
        # Create engine
        engine = AutonomousEngine(simulation_mode=False)
        
        # Run cycle
        result = engine.run_cycle()
        
        # ASSERTIONS
        # Should succeed gracefully with zero events
        assert result.get('success') == True, "Should handle empty markets gracefully"
        assert result.get('opportunities_found', 0) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
