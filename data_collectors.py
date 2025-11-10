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

class NewsCollector:
    """
    Recolecta noticias financieras de múltiples fuentes para análisis de eventos.
    Usa Alpha Vantage NEWS_SENTIMENT API y Finnhub como backup.
    """
    
    def __init__(self, alpha_vantage_key: str = "", finnhub_key: str = ""):
        self.alpha_vantage_key = alpha_vantage_key
        self.finnhub_key = finnhub_key
        self.alpha_base_url = "https://www.alphavantage.co/query"
        self.finnhub_base_url = "https://finnhub.io/api/v1"
    
    def get_news_analysis(self, symbol: str, event_description: str = "") -> Dict:
        """
        Obtiene y analiza noticias relevantes para un símbolo o evento.
        
        Args:
            symbol: Ticker symbol (e.g., 'BTC', 'AAPL')
            event_description: Descripción del evento para búsqueda contextual
        
        Returns:
            Dict con noticias, sentiment score y análisis
        """
        try:
            results = {
                'symbol': symbol,
                'event_description': event_description,
                'timestamp': datetime.now().isoformat(),
                'news_items': [],
                'sentiment_score': 0.0,
                'sentiment_label': 'Neutral',
                'news_count': 0
            }
            
            alpha_news = self._get_alpha_vantage_news(symbol)
            if alpha_news and 'feed' in alpha_news:
                results['news_items'].extend(alpha_news['feed'][:5])
                results['sentiment_score'] = alpha_news.get('sentiment_score', 0.0)
                results['sentiment_label'] = alpha_news.get('sentiment_label', 'Neutral')
            
            if len(results['news_items']) < 3 and self.finnhub_key:
                finnhub_news = self._get_finnhub_news(symbol)
                if finnhub_news:
                    results['news_items'].extend(finnhub_news[:3])
            
            results['news_count'] = len(results['news_items'])
            
            if not results['news_items']:
                results['fallback'] = True
                results['analysis'] = f"No recent news found for {symbol}. Event analysis based on description: {event_description[:100]}"
            else:
                results['analysis'] = self._generate_news_summary(results['news_items'], event_description)
            
            return results
            
        except Exception as e:
            return {
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'news_count': 0,
                'sentiment_score': 0.0
            }
    
    def _get_alpha_vantage_news(self, symbol: str) -> Optional[Dict]:
        """Obtiene noticias y sentiment de Alpha Vantage"""
        if not self.alpha_vantage_key:
            return None
            
        try:
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': symbol,
                'limit': 10,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(self.alpha_base_url, params=params, timeout=10)
            data = response.json()
            
            if 'feed' in data and data['feed']:
                news_items = []
                total_sentiment = 0.0
                
                for item in data['feed'][:5]:
                    ticker_sentiments = item.get('ticker_sentiment', [])
                    relevant_sentiment = next(
                        (ts for ts in ticker_sentiments if ts.get('ticker') == symbol),
                        None
                    )
                    
                    sentiment_score = float(relevant_sentiment['ticker_sentiment_score']) if relevant_sentiment else 0.0
                    total_sentiment += sentiment_score
                    
                    news_items.append({
                        'title': item.get('title', ''),
                        'summary': item.get('summary', '')[:200],
                        'url': item.get('url', ''),
                        'time_published': item.get('time_published', ''),
                        'source': item.get('source', 'Unknown'),
                        'sentiment_score': sentiment_score,
                        'sentiment_label': item.get('overall_sentiment_label', 'Neutral')
                    })
                
                avg_sentiment = total_sentiment / len(news_items) if news_items else 0.0
                
                return {
                    'feed': news_items,
                    'sentiment_score': avg_sentiment,
                    'sentiment_label': self._sentiment_to_label(avg_sentiment)
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting Alpha Vantage news: {e}")
            return None
    
    def _get_finnhub_news(self, symbol: str) -> Optional[List[Dict]]:
        """Obtiene noticias de Finnhub como backup"""
        if not self.finnhub_key:
            return None
            
        try:
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            url = f"{self.finnhub_base_url}/company-news"
            params = {
                'symbol': symbol,
                'from': from_date,
                'to': to_date,
                'token': self.finnhub_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data and isinstance(data, list):
                return [{
                    'title': item.get('headline', ''),
                    'summary': item.get('summary', '')[:200],
                    'url': item.get('url', ''),
                    'time_published': datetime.fromtimestamp(item.get('datetime', 0)).isoformat(),
                    'source': item.get('source', 'Finnhub'),
                    'sentiment_score': 0.0,
                    'sentiment_label': 'Neutral'
                } for item in data[:5]]
            
            return None
            
        except Exception as e:
            print(f"Error getting Finnhub news: {e}")
            return None
    
    def _sentiment_to_label(self, score: float) -> str:
        """Convierte sentiment score a label"""
        if score > 0.15:
            return 'Bullish'
        elif score > 0.05:
            return 'Somewhat-Bullish'
        elif score < -0.15:
            return 'Bearish'
        elif score < -0.05:
            return 'Somewhat-Bearish'
        else:
            return 'Neutral'
    
    def _generate_news_summary(self, news_items: List[Dict], event_description: str) -> str:
        """Genera un resumen del análisis de noticias"""
        if not news_items:
            return "No news available for analysis"
        
        sentiment_counts = {}
        sources = set()
        
        for item in news_items:
            label = item.get('sentiment_label', 'Neutral')
            sentiment_counts[label] = sentiment_counts.get(label, 0) + 1
            sources.add(item.get('source', 'Unknown'))
        
        dominant_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0] if sentiment_counts else 'Neutral'
        
        summary = f"Analyzed {len(news_items)} recent news from {len(sources)} sources. "
        summary += f"Dominant sentiment: {dominant_sentiment}. "
        
        if event_description:
            summary += f"Context: {event_description[:100]}..."
        
        return summary


class VolatilityCollector:
    """
    Calcula métricas de volatilidad histórica para análisis de riesgo.
    Usa datos de YFinance para calcular volatilidad y métricas relacionadas.
    """
    
    def __init__(self):
        self.default_periods = [7, 14, 30]
    
    def get_volatility_metrics(self, symbol: str) -> Dict:
        """
        Calcula métricas de volatilidad para un símbolo.
        
        Args:
            symbol: Ticker symbol (e.g., 'BTC-USD', 'AAPL')
        
        Returns:
            Dict con volatilidad histórica, ATR, beta y otras métricas
        """
        try:
            results = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'volatility': {}
            }
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='3mo', interval='1d')
            
            if hist.empty:
                return {
                    'symbol': symbol,
                    'error': 'No historical data available',
                    'timestamp': datetime.now().isoformat()
                }
            
            hist['returns'] = hist['Close'].pct_change()
            
            for period in self.default_periods:
                if len(hist) >= period:
                    period_returns = hist['returns'].tail(period)
                    volatility = period_returns.std() * (252 ** 0.5)
                    
                    results['volatility'][f'{period}d'] = {
                        'value': float(volatility),
                        'annualized': float(volatility),
                        'label': self._volatility_label(volatility)
                    }
            
            results['current_volatility'] = results['volatility'].get('14d', {}).get('value', 0.0)
            
            atr = self._calculate_atr(hist)
            if atr:
                results['atr'] = atr
            
            price_range = self._calculate_price_range(hist)
            if price_range:
                results['price_range'] = price_range
            
            trend_strength = self._calculate_trend_strength(hist)
            if trend_strength:
                results['trend_strength'] = trend_strength
            
            results['risk_level'] = self._assess_risk_level(results)
            
            return results
            
        except Exception as e:
            return {
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_atr(self, hist: pd.DataFrame, period: int = 14) -> Optional[Dict]:
        """Calcula Average True Range"""
        try:
            if len(hist) < period:
                return None
            
            high_low = hist['High'] - hist['Low']
            high_close = abs(hist['High'] - hist['Close'].shift())
            low_close = abs(hist['Low'] - hist['Close'].shift())
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean().iloc[-1]
            
            current_price = hist['Close'].iloc[-1]
            atr_percent = (atr / current_price) * 100 if current_price > 0 else 0
            
            return {
                'value': float(atr),
                'percent': float(atr_percent),
                'interpretation': 'High volatility' if atr_percent > 3 else 'Low volatility' if atr_percent < 1 else 'Moderate volatility'
            }
        except Exception as e:
            print(f"Error calculating ATR: {e}")
            return None
    
    def _calculate_price_range(self, hist: pd.DataFrame) -> Optional[Dict]:
        """Calcula rango de precios reciente"""
        try:
            recent = hist.tail(30)
            high = recent['High'].max()
            low = recent['Low'].min()
            current = recent['Close'].iloc[-1]
            
            range_pct = ((high - low) / low) * 100 if low > 0 else 0
            position_in_range = ((current - low) / (high - low)) * 100 if (high - low) > 0 else 50
            
            return {
                'high_30d': float(high),
                'low_30d': float(low),
                'current': float(current),
                'range_percent': float(range_pct),
                'position_in_range': float(position_in_range),
                'near_high': position_in_range > 80,
                'near_low': position_in_range < 20
            }
        except Exception as e:
            print(f"Error calculating price range: {e}")
            return None
    
    def _calculate_trend_strength(self, hist: pd.DataFrame) -> Optional[Dict]:
        """Calcula fuerza de tendencia usando ADX simplificado"""
        try:
            returns = hist['Close'].pct_change()
            positive_moves = returns[returns > 0].sum()
            negative_moves = abs(returns[returns < 0].sum())
            
            total_moves = positive_moves + negative_moves
            if total_moves == 0:
                return None
            
            directional_movement = abs(positive_moves - negative_moves) / total_moves
            
            return {
                'value': float(directional_movement),
                'label': 'Strong trend' if directional_movement > 0.6 else 'Weak trend' if directional_movement < 0.3 else 'Moderate trend',
                'direction': 'Bullish' if positive_moves > negative_moves else 'Bearish'
            }
        except Exception as e:
            print(f"Error calculating trend strength: {e}")
            return None
    
    def _volatility_label(self, volatility: float) -> str:
        """Convierte volatilidad numérica a label"""
        if volatility > 0.5:
            return 'Extremely High'
        elif volatility > 0.3:
            return 'High'
        elif volatility > 0.15:
            return 'Moderate'
        else:
            return 'Low'
    
    def _assess_risk_level(self, results: Dict) -> str:
        """Evalúa el nivel de riesgo general basado en métricas"""
        current_vol = results.get('current_volatility', 0)
        atr_pct = results.get('atr', {}).get('percent', 0)
        
        if current_vol > 0.4 or atr_pct > 4:
            return 'HIGH'
        elif current_vol > 0.2 or atr_pct > 2:
            return 'MODERATE'
        else:
            return 'LOW'
