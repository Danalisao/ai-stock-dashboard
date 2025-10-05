"""
😊 Sentiment Analyzer
Analyze sentiment of financial news using VADER and TextBlob
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import re


class SentimentAnalyzer:
    """Analyze sentiment of financial text"""
    
    # Financial keyword dictionaries
    BULLISH_KEYWORDS = {
        'breakout': 2.0, 'rally': 2.0, 'surge': 2.0, 'soar': 2.0,
        'upgrade': 1.8, 'beat': 1.8, 'exceed': 1.5, 'growth': 1.5,
        'profit': 1.5, 'gain': 1.3, 'jump': 1.3, 'rise': 1.2,
        'up': 1.0, 'positive': 1.0, 'bullish': 2.0, 'buy': 1.5,
        'outperform': 1.8, 'strong': 1.3, 'robust': 1.5,
        'momentum': 1.2, 'accelerating': 1.5, 'expansion': 1.3,
        'innovative': 1.2, 'breakthrough': 1.8, 'record': 1.5,
        'boom': 1.8, 'promising': 1.3, 'optimistic': 1.5
    }
    
    BEARISH_KEYWORDS = {
        'crash': -2.0, 'plunge': -2.0, 'collapse': -2.0, 'tumble': -1.8,
        'downgrade': -1.8, 'miss': -1.5, 'decline': -1.3, 'fall': -1.3,
        'drop': -1.3, 'down': -1.0, 'negative': -1.0, 'bearish': -2.0,
        'sell': -1.5, 'underperform': -1.8, 'weak': -1.3, 'loss': -1.5,
        'lawsuit': -1.8, 'investigation': -1.5, 'scandal': -2.0,
        'bankruptcy': -2.5, 'fraud': -2.5, 'concern': -1.2,
        'risk': -1.0, 'warning': -1.3, 'disappointing': -1.5,
        'slowing': -1.3, 'contraction': -1.5, 'recession': -1.8
    }
    
    NEUTRAL_KEYWORDS = {
        'report', 'announce', 'update', 'statement', 'release',
        'trading', 'market', 'price', 'stock', 'shares',
        'company', 'earnings', 'revenue', 'quarter', 'fiscal'
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize sentiment analyzer
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config.get('news', {}).get('sentiment', {}) if config else {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize sentiment analyzers
        try:
            self.vader = SentimentIntensityAnalyzer()
            self.logger.info("VADER sentiment analyzer initialized")
        except Exception as e:
            self.logger.error(f"Error initializing VADER: {e}")
            self.vader = None
        
        # Get weights from config
        self.vader_weight = self.config.get('vader_weight', 0.4)
        self.textblob_weight = self.config.get('textblob_weight', 0.3)
        self.keyword_weight = self.config.get('keyword_weight', 0.2)
        self.social_weight = self.config.get('social_weight', 0.1)
    
    def analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment of a news article
        
        Args:
            article: Article dictionary with title and description
            
        Returns:
            Article with sentiment scores added
        """
        # Combine title and description for analysis
        text = f"{article.get('title', '')} {article.get('description', '')}"
        
        # Calculate sentiment scores
        vader_score = self._vader_sentiment(text)
        textblob_score = self._textblob_sentiment(text)
        keyword_score = self._keyword_sentiment(text)
        
        # Weighted average
        sentiment_score = (
            vader_score * self.vader_weight +
            textblob_score * self.textblob_weight +
            keyword_score * self.keyword_weight
        )
        
        # Determine sentiment label
        sentiment_label = self._get_sentiment_label(sentiment_score)
        
        # Add to article
        article['sentiment_score'] = round(sentiment_score, 3)
        article['sentiment_label'] = sentiment_label
        article['vader_score'] = round(vader_score, 3)
        article['textblob_score'] = round(textblob_score, 3)
        article['keyword_score'] = round(keyword_score, 3)
        
        return article
    
    def _vader_sentiment(self, text: str) -> float:
        """
        Calculate VADER sentiment score
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment score from -1 (negative) to +1 (positive)
        """
        if not self.vader:
            return 0.0
        
        try:
            scores = self.vader.polarity_scores(text)
            # Compound score is already -1 to +1
            return scores['compound']
        except Exception as e:
            self.logger.error(f"Error in VADER analysis: {e}")
            return 0.0
    
    def _textblob_sentiment(self, text: str) -> float:
        """
        Calculate TextBlob sentiment score
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment score from -1 (negative) to +1 (positive)
        """
        try:
            blob = TextBlob(text)
            # Polarity is already -1 to +1
            return blob.sentiment.polarity
        except Exception as e:
            self.logger.error(f"Error in TextBlob analysis: {e}")
            return 0.0
    
    def _keyword_sentiment(self, text: str) -> float:
        """
        Calculate keyword-based sentiment score
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment score from -1 (negative) to +1 (positive)
        """
        text_lower = text.lower()
        
        # Count keyword occurrences and apply weights
        bullish_score = 0
        bearish_score = 0
        
        # Bullish keywords
        for keyword, weight in self.BULLISH_KEYWORDS.items():
            count = len(re.findall(r'\b' + keyword + r'\b', text_lower))
            bullish_score += count * weight
        
        # Bearish keywords
        for keyword, weight in self.BEARISH_KEYWORDS.items():
            count = len(re.findall(r'\b' + keyword + r'\b', text_lower))
            bearish_score += abs(count * weight)  # Make positive for calculation
        
        # Calculate net sentiment
        total = bullish_score + bearish_score
        if total == 0:
            return 0.0
        
        net_score = (bullish_score - bearish_score) / total
        
        # Normalize to -1 to +1 range
        return max(-1.0, min(1.0, net_score))
    
    def _get_sentiment_label(self, score: float) -> str:
        """
        Get sentiment label from score
        
        Args:
            score: Sentiment score
            
        Returns:
            Label string
        """
        if score >= 0.5:
            return "Very Positive"
        elif score >= 0.2:
            return "Positive"
        elif score >= -0.2:
            return "Neutral"
        elif score >= -0.5:
            return "Negative"
        else:
            return "Very Negative"
    
    def analyze_news_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for multiple articles
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Articles with sentiment scores
        """
        analyzed_articles = []
        
        for article in articles:
            try:
                analyzed_article = self.analyze_article(article)
                analyzed_articles.append(analyzed_article)
            except Exception as e:
                self.logger.error(f"Error analyzing article: {e}")
                # Add with neutral sentiment
                article['sentiment_score'] = 0.0
                article['sentiment_label'] = "Neutral"
                analyzed_articles.append(article)
        
        return analyzed_articles
    
    def calculate_aggregate_sentiment(self, articles: List[Dict[str, Any]], 
                                      days: int = 7) -> Dict[str, Any]:
        """
        Calculate aggregate sentiment from multiple articles
        
        Args:
            articles: List of analyzed articles
            days: Number of days to consider
            
        Returns:
            Dictionary with aggregate metrics
        """
        from datetime import datetime, timedelta
        
        if not articles:
            return {
                'average_sentiment': 0.0,
                'weighted_sentiment': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_articles': 0,
                'sentiment_trend': 'neutral',
                'confidence': 0.0
            }
        
        # Filter by date range
        cutoff = datetime.now() - timedelta(days=days)
        recent_articles = []
        
        for article in articles:
            try:
                pub_date = datetime.fromisoformat(article.get('published_date', ''))
                if pub_date >= cutoff:
                    recent_articles.append(article)
            except:
                # If can't parse date, include it
                recent_articles.append(article)
        
        if not recent_articles:
            recent_articles = articles  # Use all if filtering fails
        
        # Calculate metrics
        sentiments = [a.get('sentiment_score', 0.0) for a in recent_articles]
        average_sentiment = sum(sentiments) / len(sentiments)
        
        # Weight recent articles more heavily
        weighted_sum = 0
        weight_sum = 0
        for i, article in enumerate(reversed(recent_articles)):
            # More recent = higher weight
            weight = 1.0 + (i / len(recent_articles))
            sentiment = article.get('sentiment_score', 0.0)
            weighted_sum += sentiment * weight
            weight_sum += weight
        
        weighted_sentiment = weighted_sum / weight_sum if weight_sum > 0 else 0.0
        
        # Count by sentiment
        positive_count = sum(1 for s in sentiments if s > 0.2)
        negative_count = sum(1 for s in sentiments if s < -0.2)
        neutral_count = len(sentiments) - positive_count - negative_count
        
        # Determine trend
        if weighted_sentiment > 0.3:
            trend = 'bullish'
        elif weighted_sentiment < -0.3:
            trend = 'bearish'
        else:
            trend = 'neutral'
        
        # Confidence based on number of articles and agreement
        article_confidence = min(1.0, len(recent_articles) / 20.0)  # More articles = higher confidence
        agreement = (max(positive_count, negative_count, neutral_count) / len(sentiments)) if sentiments else 0.0
        confidence = (article_confidence + agreement) / 2.0
        
        return {
            'average_sentiment': round(average_sentiment, 3),
            'weighted_sentiment': round(weighted_sentiment, 3),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_articles': len(recent_articles),
            'sentiment_trend': trend,
            'confidence': round(confidence, 3)
        }
    
    def get_sentiment_emoji(self, score: float) -> str:
        """
        Get emoji for sentiment score
        
        Args:
            score: Sentiment score
            
        Returns:
            Emoji string
        """
        if score >= 0.5:
            return "😊"  # Very positive
        elif score >= 0.2:
            return "🙂"  # Positive
        elif score >= -0.2:
            return "😐"  # Neutral
        elif score >= -0.5:
            return "😟"  # Negative
        else:
            return "😞"  # Very negative
    
    def detect_sentiment_shift(self, old_sentiment: float, new_sentiment: float, 
                               threshold: float = 0.3) -> Optional[Dict[str, Any]]:
        """
        Detect significant sentiment shifts
        
        Args:
            old_sentiment: Previous sentiment score
            new_sentiment: Current sentiment score
            threshold: Minimum change to consider significant
            
        Returns:
            Dictionary with shift details or None
        """
        change = new_sentiment - old_sentiment
        
        if abs(change) >= threshold:
            direction = "improved" if change > 0 else "deteriorated"
            magnitude = "significant" if abs(change) >= 0.5 else "moderate"
            
            return {
                'old_sentiment': round(old_sentiment, 3),
                'new_sentiment': round(new_sentiment, 3),
                'change': round(change, 3),
                'direction': direction,
                'magnitude': magnitude,
                'alert': True
            }
        
        return None
    
    def extract_key_phrases(self, articles: List[Dict[str, Any]], top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Extract most common key phrases from articles
        
        Args:
            articles: List of articles
            top_n: Number of top phrases to return
            
        Returns:
            List of (phrase, count) tuples
        """
        from collections import Counter
        
        # Combine all text
        all_text = ' '.join([f"{a.get('title', '')} {a.get('description', '')}" for a in articles])
        
        # Extract noun phrases using TextBlob
        try:
            blob = TextBlob(all_text)
            phrases = [phrase.lower() for phrase in blob.noun_phrases]
            
            # Count frequency
            phrase_counts = Counter(phrases)
            
            # Return top N
            return phrase_counts.most_common(top_n)
            
        except Exception as e:
            self.logger.error(f"Error extracting key phrases: {e}")
            return []
