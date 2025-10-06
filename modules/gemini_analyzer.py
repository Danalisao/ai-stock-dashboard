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
                               watchlist: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Analyze news articles to discover the stock most likely to EXPLODE
        Uses AI to identify breakout opportunities across the entire market
        
        Args:
            news_articles: List of news articles from general market sources
            watchlist: Optional list to restrict analysis (None = discover any stock)
            
        Returns:
            Dictionary with explosive opportunity stock info and AI analysis
        """
        if not self.enabled:
            self.logger.warning("Gemini not enabled - using fallback analysis")
            return self._fallback_analysis(news_articles, watchlist or [])
        
        try:
            # Prepare news summary for Gemini
            news_text = self._prepare_news_summary(news_articles[:80])  # More articles for discovery
            
            # Create advanced prompt for opportunity discovery
            watchlist_constraint = f"\n\nOPTIONAL FILTER: Prioritize these stocks if relevant: {', '.join(watchlist)}" if watchlist else "\n\nANALYZE ALL STOCKS - No restrictions."
            
            prompt = f"""You are a professional stock market analyst. Analyze the following financial news and identify the ONE stock with the HIGHEST EXPLOSIVE POTENTIAL in the next 7-30 days.

NEWS ARTICLES FROM MULTIPLE SOURCES:
{news_text}
{watchlist_constraint}

CRITERIA FOR EXPLOSIVE POTENTIAL:
1. ⚡ **Catalysts**: Earnings beats, FDA approvals, product launches, M&A, partnerships
2. 📈 **Momentum**: Multiple positive articles, analyst upgrades, price action
3. 💰 **Market Impact**: Significant revenue/growth announcements
4. 🔥 **Sentiment Surge**: Bullish tone, excitement, breakthrough news
5. 🎯 **Timing**: Recent/imminent events (not old news)

IDENTIFY the stock ticker symbol (e.g., AAPL, TSLA, NVDA) that has:
- The STRONGEST catalyst(s) for explosive growth
- The MOST BULLISH sentiment shift
- The HIGHEST probability of significant price movement

Respond ONLY in JSON format:
{{
    "trending_stock": "TICKER_SYMBOL",
    "confidence": 0-100,
    "reasoning": "Concise explanation (2-3 sentences) of WHY this will explode",
    "sentiment": "bullish/neutral/bearish",
    "key_topics": ["catalyst1", "catalyst2", "catalyst3"],
    "news_count": number_of_relevant_articles,
    "explosion_catalysts": ["specific event 1", "specific event 2"],
    "timeframe": "7-30 days estimate",
    "risk_level": "low/medium/high"
}}

IMPORTANT: 
- Focus on ACTIONABLE explosive opportunities, not general trending
- Identify the ticker symbol even if not explicitly mentioned (use company name)
- Prioritize stocks with MULTIPLE positive catalysts
- Be specific about what will drive the explosion

Return ONLY valid JSON, no markdown or extra text."""

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
            result['source'] = 'gemini-2.5-flash'
            result['timestamp'] = datetime.now().isoformat()
            result['articles_analyzed'] = len(news_articles)
            
            # Ensure required fields
            if not result.get('trending_stock'):
                self.logger.warning("Gemini did not identify a stock - using fallback")
                return self._fallback_analysis(news_articles, watchlist or [])
            
            self.logger.info(f"🚀 Gemini identified EXPLOSIVE opportunity: {result.get('trending_stock')} "
                           f"(confidence: {result.get('confidence')}%) - {result.get('reasoning', '')[:50]}...")
            
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
