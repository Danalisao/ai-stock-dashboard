"""
💬 Social Media Aggregator
Collect and analyze stock mentions from Reddit and other social platforms
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import praw
import os


class SocialAggregator:
    """Aggregate social media mentions and sentiment"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize social media aggregator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config.get('news', {})
        self.logger = logging.getLogger(__name__)
        
        # Initialize Reddit API
        self.reddit = None
        self._init_reddit()
    
    def _init_reddit(self):
        """Initialize Reddit API client"""
        try:
            client_id = os.getenv('REDDIT_CLIENT_ID')
            client_secret = os.getenv('REDDIT_CLIENT_SECRET')
            user_agent = os.getenv('REDDIT_USER_AGENT', 'StockDashboard/1.0')
            
            if client_id and client_secret:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent,
                    check_for_async=False
                )
                self.logger.info("Reddit API initialized successfully")
            else:
                self.logger.warning("Reddit API credentials not found. Social features disabled.")
                
        except Exception as e:
            self.logger.error(f"Error initializing Reddit API: {e}")
            self.reddit = None
    
    def fetch_reddit_mentions(self, symbol: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        Fetch stock mentions from Reddit
        
        Args:
            symbol: Stock ticker symbol
            days: Number of days to look back
            
        Returns:
            List of mention dictionaries
        """
        if not self.reddit:
            self.logger.warning("Reddit API not initialized - skipping social data")
            return []
        
        self.logger.info(f"🔍 Searching Reddit for {symbol} mentions...")
        mentions = []
        subreddits = self.config.get('reddit_subs', ['stocks', 'investing', 'wallstreetbets'])
        
        try:
            # Search across multiple subreddits
            for sub_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(sub_name)
                    
                    # Search for symbol mentions
                    query = f"${symbol} OR {symbol}"
                    self.logger.debug(f"Searching r/{sub_name} for: {query}")
                    
                    # Search recent posts
                    found_count = 0
                    for submission in subreddit.search(query, time_filter='week', limit=50):
                        # Check if recent enough
                        post_date = datetime.fromtimestamp(submission.created_utc)
                        if datetime.now() - post_date > timedelta(days=days):
                            continue
                        
                        mentions.append({
                            'platform': 'Reddit',
                            'subreddit': sub_name,
                            'type': 'submission',
                            'title': submission.title,
                            'content': submission.selftext[:500] if submission.selftext else '',
                            'author': str(submission.author),
                            'url': f"https://reddit.com{submission.permalink}",
                            'score': submission.score,
                            'num_comments': submission.num_comments,
                            'posted_date': post_date.isoformat(),
                            'fetched_at': datetime.now().isoformat()
                        })
                        found_count += 1
                    
                    self.logger.info(f"  💬 r/{sub_name}: {found_count} mentions")
                    
                except Exception as e:
                    self.logger.error(f"  ❌ Error fetching from r/{sub_name}: {e}")
                    continue
            
            self.logger.info(f"✅ Total Reddit mentions for {symbol}: {len(mentions)}")
            
        except Exception as e:
            self.logger.error(f"Error fetching Reddit mentions: {e}")
        
        return mentions
    
    def get_trending_tickers(self, subreddit: str = 'wallstreetbets', limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending stock tickers from subreddit
        
        Args:
            subreddit: Subreddit name
            limit: Number of top posts to analyze
            
        Returns:
            List of trending ticker dictionaries
        """
        if not self.reddit:
            return []
        
        import re
        from collections import Counter
        
        try:
            sub = self.reddit.subreddit(subreddit)
            ticker_pattern = r'\$?[A-Z]{1,5}\b'
            
            tickers = []
            
            # Analyze hot posts
            for submission in sub.hot(limit=limit):
                # Extract tickers from title and text
                text = f"{submission.title} {submission.selftext}"
                found_tickers = re.findall(ticker_pattern, text)
                
                # Clean up
                found_tickers = [t.replace('$', '').upper() for t in found_tickers]
                
                # Filter common words
                common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW', 'MAN', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO', 'BOY', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE'}
                found_tickers = [t for t in found_tickers if t not in common_words and len(t) <= 5]
                
                tickers.extend(found_tickers)
            
            # Count occurrences
            ticker_counts = Counter(tickers)
            
            # Return top tickers
            trending = [
                {
                    'symbol': ticker,
                    'mentions': count,
                    'subreddit': subreddit
                }
                for ticker, count in ticker_counts.most_common(20)
            ]
            
            self.logger.info(f"Found {len(trending)} trending tickers in r/{subreddit}")
            return trending
            
        except Exception as e:
            self.logger.error(f"Error getting trending tickers: {e}")
            return []
    
    def calculate_social_sentiment(self, mentions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate aggregate social sentiment from mentions
        
        Args:
            mentions: List of mention dictionaries
            
        Returns:
            Dictionary with sentiment metrics
        """
        if not mentions:
            return {
                'total_mentions': 0,
                'average_score': 0,
                'sentiment': 'neutral',
                'buzz_level': 'low',
                'confidence': 0.0
            }
        
        # Calculate metrics
        total_mentions = len(mentions)
        total_score = sum(m.get('score', 0) for m in mentions)
        average_score = total_score / total_mentions if total_mentions > 0 else 0
        
        # Calculate engagement
        total_comments = sum(m.get('num_comments', 0) for m in mentions)
        avg_comments = total_comments / total_mentions if total_mentions > 0 else 0
        
        # Determine buzz level
        if total_mentions >= 50:
            buzz_level = 'very_high'
        elif total_mentions >= 20:
            buzz_level = 'high'
        elif total_mentions >= 10:
            buzz_level = 'medium'
        else:
            buzz_level = 'low'
        
        # Simple sentiment based on scores
        if average_score > 50:
            sentiment = 'very_positive'
        elif average_score > 10:
            sentiment = 'positive'
        elif average_score > -10:
            sentiment = 'neutral'
        elif average_score > -50:
            sentiment = 'negative'
        else:
            sentiment = 'very_negative'
        
        # Confidence based on sample size
        confidence = min(1.0, total_mentions / 30.0)
        
        return {
            'total_mentions': total_mentions,
            'average_score': round(average_score, 2),
            'total_score': total_score,
            'average_comments': round(avg_comments, 2),
            'sentiment': sentiment,
            'buzz_level': buzz_level,
            'confidence': round(confidence, 3)
        }
    
    def get_top_posts(self, symbol: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get top Reddit posts mentioning a symbol
        
        Args:
            symbol: Stock ticker
            limit: Number of posts to return
            
        Returns:
            List of top post dictionaries
        """
        mentions = self.fetch_reddit_mentions(symbol, days=7)
        
        # Sort by score
        sorted_mentions = sorted(mentions, key=lambda x: x.get('score', 0), reverse=True)
        
        return sorted_mentions[:limit]
    
    def detect_unusual_activity(self, symbol: str, baseline_days: int = 30) -> Dict[str, Any]:
        """
        Detect unusual social media activity for a symbol
        
        Args:
            symbol: Stock ticker
            baseline_days: Days to use for baseline
            
        Returns:
            Dictionary with activity analysis
        """
        # Fetch recent mentions
        recent_mentions = self.fetch_reddit_mentions(symbol, days=1)
        baseline_mentions = self.fetch_reddit_mentions(symbol, days=baseline_days)
        
        # Calculate daily averages
        recent_count = len(recent_mentions)
        baseline_avg = len(baseline_mentions) / baseline_days
        
        # Detect spike
        if baseline_avg > 0:
            spike_ratio = recent_count / baseline_avg
        else:
            spike_ratio = recent_count if recent_count > 0 else 0
        
        is_unusual = spike_ratio > 3.0  # 3x baseline
        
        return {
            'symbol': symbol,
            'recent_mentions_24h': recent_count,
            'baseline_daily_avg': round(baseline_avg, 2),
            'spike_ratio': round(spike_ratio, 2),
            'is_unusual': is_unusual,
            'alert_level': 'high' if spike_ratio > 5 else 'medium' if spike_ratio > 3 else 'normal'
        }
    
    def get_sentiment_score(self, mentions: List[Dict[str, Any]]) -> float:
        """
        Convert social metrics to sentiment score (-1 to +1)
        
        Args:
            mentions: List of mentions
            
        Returns:
            Sentiment score
        """
        if not mentions:
            return 0.0
        
        # Use average score as proxy
        total_score = sum(m.get('score', 0) for m in mentions)
        
        # Normalize to -1 to +1 range
        # Reddit scores typically range from -100 to +1000
        normalized_score = total_score / (len(mentions) * 100)
        
        # Clamp to -1 to +1
        return max(-1.0, min(1.0, normalized_score))
