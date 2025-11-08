import os
import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import praw
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd

nltk.download('vader_lexicon', quiet=True)

class AlphaVantageCollector:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
    
    def get_technical_indicators(self, symbol: str) -> Dict:
        try:
            results = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'indicators': {}
            }
            
            rsi_data = self._get_rsi(symbol)
            if rsi_data:
                results['indicators']['RSI'] = rsi_data
            
            macd_data = self._get_macd(symbol)
            if macd_data:
                results['indicators']['MACD'] = macd_data
            
            price_data = self._get_quote(symbol)
            if price_data:
                results['quote'] = price_data
            
            return results
        except Exception as e:
            return {
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_rsi(self, symbol: str, interval: str = 'daily', time_period: int = 14) -> Optional[Dict]:
        try:
            params = {
                'function': 'RSI',
                'symbol': symbol,
                'interval': interval,
                'time_period': time_period,
                'series_type': 'close',
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if 'Technical Analysis: RSI' in data:
                technical_data = data['Technical Analysis: RSI']
                latest_date = list(technical_data.keys())[0]
                rsi_value = float(technical_data[latest_date]['RSI'])
                
                return {
                    'value': rsi_value,
                    'date': latest_date,
                    'signal': 'overbought' if rsi_value > 70 else 'oversold' if rsi_value < 30 else 'neutral'
                }
            return None
        except Exception as e:
            print(f"Error getting RSI: {e}")
            return None
    
    def _get_macd(self, symbol: str, interval: str = 'daily') -> Optional[Dict]:
        try:
            params = {
                'function': 'MACD',
                'symbol': symbol,
                'interval': interval,
                'series_type': 'close',
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if 'Technical Analysis: MACD' in data:
                technical_data = data['Technical Analysis: MACD']
                latest_date = list(technical_data.keys())[0]
                macd_data = technical_data[latest_date]
                
                macd = float(macd_data['MACD'])
                signal = float(macd_data['MACD_Signal'])
                histogram = float(macd_data['MACD_Hist'])
                
                return {
                    'MACD': macd,
                    'Signal': signal,
                    'Histogram': histogram,
                    'date': latest_date,
                    'trend': 'bullish' if histogram > 0 else 'bearish'
                }
            return None
        except Exception as e:
            print(f"Error getting MACD: {e}")
            return None
    
    def _get_quote(self, symbol: str) -> Optional[Dict]:
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if 'Global Quote' in data and data['Global Quote']:
                quote = data['Global Quote']
                return {
                    'price': float(quote.get('05. price', 0)),
                    'change': float(quote.get('09. change', 0)),
                    'change_percent': quote.get('10. change percent', '0%'),
                    'volume': int(quote.get('06. volume', 0)),
                    'latest_trading_day': quote.get('07. latest trading day', '')
                }
            return None
        except Exception as e:
            print(f"Error getting quote: {e}")
            return None
    
    def get_news_sentiment(self, symbol: str) -> Dict:
        try:
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': symbol,
                'apikey': self.api_key,
                'limit': 50
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if 'feed' in data:
                articles = data['feed'][:10]
                
                sentiments = []
                for article in articles:
                    if 'ticker_sentiment' in article:
                        for ticker in article['ticker_sentiment']:
                            if ticker['ticker'] == symbol:
                                sentiments.append({
                                    'title': article.get('title', ''),
                                    'sentiment_score': float(ticker.get('ticker_sentiment_score', 0)),
                                    'sentiment_label': ticker.get('ticker_sentiment_label', 'Neutral'),
                                    'time_published': article.get('time_published', '')
                                })
                
                if sentiments:
                    avg_sentiment = sum(s['sentiment_score'] for s in sentiments) / len(sentiments)
                    return {
                        'average_sentiment': avg_sentiment,
                        'sentiment_label': 'Bullish' if avg_sentiment > 0.15 else 'Bearish' if avg_sentiment < -0.15 else 'Neutral',
                        'article_count': len(sentiments),
                        'recent_articles': sentiments[:5]
                    }
            
            return {'average_sentiment': 0, 'sentiment_label': 'Neutral', 'article_count': 0}
        except Exception as e:
            print(f"Error getting news sentiment: {e}")
            return {'error': str(e)}


class YFinanceCollector:
    def get_fundamental_data(self, symbol: str) -> Dict:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            history = ticker.history(period="1mo")
            
            fundamental_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'company_name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'price_to_book': info.get('priceToBook', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 0),
                '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                '52_week_low': info.get('fiftyTwoWeekLow', 0),
                'current_price': info.get('currentPrice', 0),
                'target_mean_price': info.get('targetMeanPrice', 0),
                'recommendation': info.get('recommendationKey', 'none'),
                'earnings_growth': info.get('earningsQuarterlyGrowth', 0),
                'revenue_growth': info.get('revenueGrowth', 0),
                'profit_margins': info.get('profitMargins', 0),
                'price_momentum_1m': self._calculate_momentum(history, 30) if not history.empty else 0
            }
            
            return fundamental_data
        except Exception as e:
            return {
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_momentum(self, history_df: pd.DataFrame, days: int) -> float:
        try:
            if len(history_df) >= days:
                recent_price = history_df['Close'].iloc[-1]
                past_price = history_df['Close'].iloc[-days]
                return ((recent_price - past_price) / past_price) * 100
            return 0
        except:
            return 0


class RedditSentimentCollector:
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.sia = SentimentIntensityAnalyzer()
    
    def analyze_subreddit_sentiment(self, symbol: str, subreddits: List[str] = ['wallstreetbets', 'stocks', 'investing'], limit: int = 100) -> Dict:
        try:
            all_posts = []
            all_comments = []
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    for post in subreddit.search(symbol, time_filter='week', limit=limit//len(subreddits)):
                        post_sentiment = self.sia.polarity_scores(post.title + ' ' + post.selftext)
                        all_posts.append({
                            'title': post.title,
                            'score': post.score,
                            'subreddit': subreddit_name,
                            'sentiment': post_sentiment['compound'],
                            'created': datetime.fromtimestamp(post.created_utc).isoformat()
                        })
                        
                        post.comments.replace_more(limit=0)
                        for comment in list(post.comments)[:5]:
                            if len(comment.body) > 20:
                                comment_sentiment = self.sia.polarity_scores(comment.body)
                                all_comments.append({
                                    'text': comment.body[:200],
                                    'score': comment.score,
                                    'sentiment': comment_sentiment['compound']
                                })
                except Exception as e:
                    print(f"Error accessing subreddit {subreddit_name}: {e}")
                    continue
            
            if all_posts:
                avg_post_sentiment = sum(p['sentiment'] for p in all_posts) / len(all_posts)
                avg_comment_sentiment = sum(c['sentiment'] for c in all_comments) / len(all_comments) if all_comments else 0
                
                total_score = sum(p['score'] for p in all_posts)
                weighted_sentiment = sum(p['sentiment'] * p['score'] for p in all_posts) / total_score if total_score > 0 else avg_post_sentiment
                
                return {
                    'symbol': symbol,
                    'timestamp': datetime.now().isoformat(),
                    'posts_analyzed': len(all_posts),
                    'comments_analyzed': len(all_comments),
                    'average_post_sentiment': avg_post_sentiment,
                    'average_comment_sentiment': avg_comment_sentiment,
                    'weighted_sentiment': weighted_sentiment,
                    'sentiment_label': self._get_sentiment_label(weighted_sentiment),
                    'top_posts': sorted(all_posts, key=lambda x: x['score'], reverse=True)[:5],
                    'subreddits_searched': subreddits
                }
            else:
                return {
                    'symbol': symbol,
                    'timestamp': datetime.now().isoformat(),
                    'posts_analyzed': 0,
                    'error': 'No posts found'
                }
        except Exception as e:
            return {
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_sentiment_label(self, compound_score: float) -> str:
        if compound_score >= 0.05:
            return 'Positive'
        elif compound_score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
