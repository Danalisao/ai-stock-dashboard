"""
🤖 Google Gemini AI Analyzer
Analyzes market news and trends using Google Gemini Flash 2.5
"""

import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import google.generativeai as genai


class GeminiAnalyzer:
    """AI-powered market analysis using Google Gemini"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Gemini analyzer
        
        Args:
            config: Configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Get API key from environment
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            self.logger.warning("Gemini API key not found. AI analysis disabled.")
            self.enabled = False
            return
        
        try:
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Use Gemini Flash 2.5 (fast and cost-effective)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            self.enabled = True
            self.logger.info("✅ Google Gemini AI analyzer initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini: {e}")
            self.enabled = False
    
    def analyze_trending_stock(self, news_articles: List[Dict[str, Any]], 
                               watchlist: List[str]) -> Optional[Dict[str, Any]]:
        """
        Analyze news articles to find the most mentioned/trending stock
        
        Args:
            news_articles: List of news articles with title, description, content
            watchlist: List of stock symbols to consider
            
        Returns:
            Dictionary with trending stock info and AI analysis
        """
        if not self.enabled:
            self.logger.warning("Gemini not enabled - using fallback analysis")
            return self._fallback_analysis(news_articles, watchlist)
        
        try:
            # Prepare news summary for Gemini
            news_text = self._prepare_news_summary(news_articles[:50])  # Limit to 50 articles
            
            # Create prompt for Gemini
            prompt = f"""Analyze the following financial news articles and identify which stock from this watchlist is the MOST TRENDING today:

WATCHLIST: {', '.join(watchlist)}

NEWS ARTICLES:
{news_text}

Please respond in JSON format with:
{{
    "trending_stock": "SYMBOL",
    "confidence": 0-100,
    "reasoning": "brief explanation (2-3 sentences)",
    "sentiment": "bullish/neutral/bearish",
    "key_topics": ["topic1", "topic2", "topic3"],
    "news_count": number of articles mentioning this stock
}}

Focus on:
1. Frequency of mentions across articles
2. Significance of the news (earnings, product launches, regulatory, etc.)
3. Sentiment and market impact
4. Recent price movements or analyst upgrades

Return only the JSON, no additional text."""

            # Get response from Gemini
            response = self.model.generate_content(prompt)
            
            # Parse response
            import json
            result_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            
            result = json.loads(result_text)
            
            # Add metadata
            result['source'] = 'gemini-2.0-flash-exp'
            result['timestamp'] = datetime.now().isoformat()
            result['articles_analyzed'] = len(news_articles)
            
            self.logger.info(f"✅ Gemini identified trending stock: {result.get('trending_stock')} "
                           f"(confidence: {result.get('confidence')}%)")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Gemini analysis failed: {e}")
            return self._fallback_analysis(news_articles, watchlist)
    
    def _prepare_news_summary(self, articles: List[Dict[str, Any]]) -> str:
        """Prepare news articles summary for Gemini"""
        summary = []
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'N/A')
            description = article.get('description', '')
            source = article.get('source', 'Unknown')
            published = article.get('published', '')
            
            summary.append(f"{i}. [{source}] {title}")
            if description:
                summary.append(f"   {description[:200]}...")
            summary.append("")  # Empty line
        
        return '\n'.join(summary)
    
    def _fallback_analysis(self, news_articles: List[Dict[str, Any]], 
                          watchlist: List[str]) -> Dict[str, Any]:
        """
        Fallback analysis without AI (simple keyword counting)
        Used when Gemini is not available
        """
        self.logger.info("Using fallback analysis (keyword counting)")
        
        # Count mentions of each stock symbol
        mentions = {symbol: 0 for symbol in watchlist}
        
        for article in news_articles:
            text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}".upper()
            
            for symbol in watchlist:
                # Count occurrences
                count = text.count(symbol)
                if count > 0:
                    mentions[symbol] += count
        
        # Find most mentioned
        if not mentions or max(mentions.values()) == 0:
            return {
                'trending_stock': watchlist[0] if watchlist else 'AAPL',
                'confidence': 0,
                'reasoning': 'No specific stock trending in news. Showing default.',
                'sentiment': 'neutral',
                'key_topics': [],
                'news_count': 0,
                'source': 'fallback',
                'timestamp': datetime.now().isoformat()
            }
        
        trending_stock = max(mentions, key=mentions.get)
        news_count = mentions[trending_stock]
        
        return {
            'trending_stock': trending_stock,
            'confidence': min(news_count * 10, 100),  # Simple confidence score
            'reasoning': f"Most frequently mentioned in recent news ({news_count} mentions).",
            'sentiment': 'neutral',
            'key_topics': ['news', 'mentions'],
            'news_count': news_count,
            'source': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'articles_analyzed': len(news_articles)
        }
    
    def generate_market_insight(self, stock_data: Dict[str, Any], 
                               news_summary: str) -> Optional[str]:
        """
        Generate AI-powered market insight for a specific stock
        
        Args:
            stock_data: Stock price data and technical indicators
            news_summary: Summary of recent news
            
        Returns:
            AI-generated insight text
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""As a professional market analyst, provide a concise market insight (3-4 sentences) for this stock:

STOCK: {stock_data.get('symbol', 'Unknown')}
CURRENT PRICE: ${stock_data.get('price', 0):.2f}
CHANGE: {stock_data.get('change_pct', 0):+.2f}%
RSI: {stock_data.get('rsi', 0):.1f}
RECENT NEWS: {news_summary[:500]}

Focus on:
1. Key price action and technical setup
2. News impact and sentiment
3. Short-term outlook (bullish/bearish/neutral)

Keep it professional, concise, and actionable. No investment advice disclaimers."""

            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            self.logger.error(f"Failed to generate insight: {e}")
            return None
