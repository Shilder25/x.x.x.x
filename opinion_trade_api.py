import requests
import os
from typing import Dict, Optional
from datetime import datetime

class OpinionTradeAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPINION_TRADE_API_KEY", "")
        self.base_url = "https://api.opinion.trade/v1"
    
    def submit_prediction(self, prediction_data: Dict) -> Dict:
        """
        Submit a prediction to Opinion.trade API.
        
        Args:
            prediction_data: Dictionary containing:
                - event_id: The Opinion.trade event ID
                - probability: Float between 0 and 1
                - amount: Bet amount (optional, defaults to min bet)
                - metadata: Additional info about the prediction
        
        Returns:
            Response dictionary with status and any error messages
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'Opinion.trade API key not configured',
                'message': 'Please set OPINION_TRADE_API_KEY in secrets'
            }
        
        endpoint = f"{self.base_url}/predictions"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'event_id': prediction_data.get('event_id'),
            'probability': float(prediction_data.get('probability', 0.5)),
            'amount': prediction_data.get('amount', 10),
            'metadata': {
                'firm_name': prediction_data.get('firm_name', 'Unknown'),
                'timestamp': datetime.now().isoformat(),
                'reasoning': prediction_data.get('reasoning', ''),
                'risk_posture': prediction_data.get('risk_posture', 'NEUTRAL')
            }
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                return {
                    'success': True,
                    'prediction_id': result.get('id'),
                    'message': 'Prediction submitted successfully',
                    'data': result
                }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'error': 'Authentication failed',
                    'message': 'Invalid API key'
                }
            elif response.status_code == 400:
                return {
                    'success': False,
                    'error': 'Bad request',
                    'message': response.json().get('message', 'Invalid prediction data')
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout',
                'message': 'API request timed out after 30 seconds'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Connection error',
                'message': 'Could not connect to Opinion.trade API'
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Unexpected error',
                'message': str(e)
            }
    
    def get_event_details(self, event_id: str) -> Dict:
        """
        Fetch details about a specific event from Opinion.trade.
        
        Args:
            event_id: The Opinion.trade event ID
        
        Returns:
            Event details or error dictionary
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'Opinion.trade API key not configured'
            }
        
        endpoint = f"{self.base_url}/events/{event_id}"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(endpoint, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_prediction_result(self, prediction_id: str) -> Dict:
        """
        Check if a prediction has been resolved and get the result.
        
        Args:
            prediction_id: The Opinion.trade prediction ID
        
        Returns:
            Result dictionary with resolution status
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'Opinion.trade API key not configured'
            }
        
        endpoint = f"{self.base_url}/predictions/{prediction_id}"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(endpoint, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'resolved': data.get('resolved', False),
                    'outcome': data.get('outcome'),
                    'profit_loss': data.get('profit_loss', 0),
                    'data': data
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_available_events(self, limit: int = 50, category: Optional[str] = None) -> Dict:
        """
        Fetch list of available events from Opinion.trade for autonomous betting.
        
        Args:
            limit: Maximum number of events to retrieve (default 50)
            category: Optional category filter (e.g., 'crypto', 'sports', 'politics')
        
        Returns:
            Dictionary with success status and list of events
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'Opinion.trade API key not configured'
            }
        
        endpoint = f"{self.base_url}/events"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'limit': limit,
            'status': 'active'
        }
        
        if category:
            params['category'] = category
        
        try:
            response = requests.get(endpoint, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                events = data.get('events', [])
                
                return {
                    'success': True,
                    'count': len(events),
                    'events': events,
                    'message': f'Retrieved {len(events)} available events'
                }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'error': 'Authentication failed',
                    'message': 'Invalid API key'
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout',
                'message': 'API request timed out after 30 seconds'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Connection error',
                'message': 'Could not connect to Opinion.trade API'
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Unexpected error',
                'message': str(e)
            }
    
    def get_account_balance(self) -> Dict:
        """
        Get current account balance and available funds for betting.
        
        Returns:
            Dictionary with balance information
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'Opinion.trade API key not configured'
            }
        
        endpoint = f"{self.base_url}/account/balance"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(endpoint, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'total_balance': data.get('total_balance', 0),
                    'available_balance': data.get('available_balance', 0),
                    'locked_balance': data.get('locked_balance', 0),
                    'currency': data.get('currency', 'USD'),
                    'data': data
                }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'error': 'Authentication failed',
                    'message': 'Invalid API key'
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_active_positions(self) -> Dict:
        """
        Get all active betting positions.
        
        Returns:
            Dictionary with list of active positions
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'Opinion.trade API key not configured'
            }
        
        endpoint = f"{self.base_url}/positions"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'status': 'active'
        }
        
        try:
            response = requests.get(endpoint, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                positions = data.get('positions', [])
                
                return {
                    'success': True,
                    'count': len(positions),
                    'positions': positions,
                    'total_exposure': sum(p.get('amount', 0) for p in positions)
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
