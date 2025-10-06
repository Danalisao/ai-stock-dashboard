"""
🤖 Google Gemini AI Analyzer
Analyzes market news and trends using Google Gemini Flash 2.5
"""

import logging
import os
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

# Suppress gRPC warnings when not running on GCP
os.environ.setdefault('GRPC_PYTHON_LOG_LEVEL', 'ERROR')
os.environ.setdefault('GRPC_VERBOSITY', 'ERROR')

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
        
        # Rate limiting and quota management
        self.request_count = 0
        self.daily_limit = 50  # Free tier limit
        self.last_request_time = 0
        self.min_request_interval = 1.2  # Seconds between requests
        self.quota_exceeded = False
        self.quota_reset_time = None
        
        # Cache system
        self.cache_dir = Path('./data/gemini_cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = 3600  # 1 hour cache
        
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
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            
            self.enabled = True
            self._load_request_counter()
            self.logger.info(f"✅ Google Gemini AI analyzer initialized (Requests today: {self.request_count}/{self.daily_limit})")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini: {e}")
            self.enabled = False
    
    def _load_request_counter(self):
        """Load daily request counter from cache"""
        counter_file = self.cache_dir / 'request_counter.json'
        try:
            if counter_file.exists():
                data = json.loads(counter_file.read_text())
                today = datetime.now().date().isoformat()
                if data.get('date') == today:
                    self.request_count = data.get('count', 0)
                else:
                    # New day, reset counter
                    self.request_count = 0
                    self._save_request_counter()
        except Exception as e:
            self.logger.warning(f"Could not load request counter: {e}")
    
    def _save_request_counter(self):
        """Save daily request counter to cache"""
        counter_file = self.cache_dir / 'request_counter.json'
        try:
            data = {
                'date': datetime.now().date().isoformat(),
                'count': self.request_count
            }
            counter_file.write_text(json.dumps(data))
        except Exception as e:
            self.logger.warning(f"Could not save request counter: {e}")
    
    def _get_cache_key(self, operation: str, data: Any) -> str:
        """Generate cache key from operation and data"""
        import hashlib
        data_str = json.dumps(data, sort_keys=True, default=str)
        hash_obj = hashlib.md5(f"{operation}:{data_str}".encode())
        return hash_obj.hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            if cache_file.exists():
                data = json.loads(cache_file.read_text())
                cached_time = datetime.fromisoformat(data.get('timestamp', ''))
                if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                    self.logger.info(f"📦 Using cached result (age: {(datetime.now() - cached_time).seconds}s)")
                    return data.get('result')
        except Exception as e:
            self.logger.debug(f"Cache read error: {e}")
        return None
    
    def _save_to_cache(self, cache_key: str, result: Dict[str, Any]):
        """Save result to cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'result': result
            }
            cache_file.write_text(json.dumps(data, default=str))
        except Exception as e:
            self.logger.warning(f"Cache write error: {e}")
    
    def _check_quota_and_wait(self) -> bool:
        """Check quota and apply rate limiting"""
        # Check if quota was exceeded
        if self.quota_exceeded:
            if self.quota_reset_time and datetime.now() < self.quota_reset_time:
                remaining = (self.quota_reset_time - datetime.now()).seconds
                self.logger.warning(f"⏳ Quota exceeded. Reset in {remaining}s. Returning cached/fallback data.")
                return False
            else:
                # Reset quota flag
                self.quota_exceeded = False
                self.quota_reset_time = None
        
        # Check daily limit
        if self.request_count >= self.daily_limit:
            self.logger.warning(f"⚠️ Daily limit reached ({self.request_count}/{self.daily_limit}). Using fallback mode.")
            return False
        
        # Rate limiting - wait between requests
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            wait_time = self.min_request_interval - elapsed
            self.logger.debug(f"⏱️ Rate limiting: waiting {wait_time:.1f}s")
            time.sleep(wait_time)
        
        return True
    
    def _execute_gemini_request(self, prompt: str, cache_key: str = None) -> Optional[str]:
        """Execute Gemini request with quota management and retry logic"""
        # Check cache first
        if cache_key:
            cached = self._get_cached_result(cache_key)
            if cached:
                return json.dumps(cached) if isinstance(cached, dict) else cached
        
        # Check quota
        if not self._check_quota_and_wait():
            return None
        
        # Execute request with retry logic
        max_retries = 2
        for attempt in range(max_retries):
            try:
                self.last_request_time = time.time()
                response = self.model.generate_content(prompt)
                
                # Success - increment counter
                self.request_count += 1
                self._save_request_counter()
                self.logger.debug(f"✅ Gemini request successful ({self.request_count}/{self.daily_limit})")
                
                return response.text.strip()
                
            except Exception as e:
                error_str = str(e)
                
                # Handle quota exceeded (429)
                if '429' in error_str or 'quota' in error_str.lower():
                    self.quota_exceeded = True
                    
                    # Extract retry delay if available
                    if 'retry in' in error_str.lower():
                        try:
                            import re
                            match = re.search(r'retry in (\d+\.?\d*)s', error_str)
                            if match:
                                retry_seconds = float(match.group(1))
                                self.quota_reset_time = datetime.now() + timedelta(seconds=retry_seconds)
                                self.logger.error(f"🚫 Quota exceeded. Reset in {retry_seconds}s")
                        except:
                            pass
                    
                    self.logger.error(f"🚫 Gemini quota exceeded. Switching to fallback mode.")
                    return None
                
                # Handle rate limiting (503)
                elif '503' in error_str or 'rate' in error_str.lower():
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2
                        self.logger.warning(f"⏳ Rate limited. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                
                # Other errors
                self.logger.error(f"❌ Gemini request failed: {e}")
                return None
        
        return None
    
    def analyze_trending_stock(self, news_articles: List[Dict[str, Any]], 
                               watchlist: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Analyze news articles to discover MULTIPLE trading opportunities
        Uses AI to identify breakout opportunities across the entire market
        
        Args:
            news_articles: List of news articles from general market sources
            watchlist: Optional list to restrict analysis (None = discover any stock)
            
        Returns:
            Dictionary with top opportunities sorted by risk level (low to high)
        """
        if not self.enabled:
            self.logger.warning("Gemini not enabled - using fallback analysis")
            return self._fallback_analysis(news_articles, watchlist or [])
        
        try:
            # Prepare news summary for Gemini
            news_text = self._prepare_news_summary(news_articles[:80])  # More articles for discovery
            
            # Create advanced prompt for opportunity discovery
            watchlist_constraint = f"\n\nOPTIONAL FILTER: Prioritize these stocks if relevant: {', '.join(watchlist)}" if watchlist else "\n\nANALYZE ALL STOCKS - No restrictions."
            
            prompt = f"""You are a professional stock market analyst. Analyze the following financial news and identify the TOP 3-5 stocks with TRADING OPPORTUNITIES in the next 7-30 days.

NEWS ARTICLES FROM MULTIPLE SOURCES:
{news_text}
{watchlist_constraint}

CRITERIA FOR TRADING OPPORTUNITIES:
1. ⚡ **Catalysts**: Earnings beats, FDA approvals, product launches, M&A, partnerships
2. 📈 **Momentum**: Multiple positive articles, analyst upgrades, price action
3. 💰 **Market Impact**: Significant revenue/growth announcements
4. 🔥 **Sentiment Surge**: Bullish tone, excitement, breakthrough news
5. 🎯 **Timing**: Recent/imminent events (not old news)

IDENTIFY 3-5 stock ticker symbols with trading potential, sorted from LOWEST to HIGHEST risk:
- LOW RISK: Established companies, strong fundamentals, clear catalysts
- MEDIUM RISK: Growth stocks with good momentum, moderate volatility
- HIGH RISK: High volatility stocks, speculative plays, but strong catalysts

Respond ONLY in JSON format:
{{
    "opportunities": [
        {{
            "ticker": "TICKER_SYMBOL",
            "confidence": 0-100,
            "reasoning": "Concise explanation (2-3 sentences) of WHY this is a good trade",
            "sentiment": "bullish/neutral/bearish",
            "key_topics": ["catalyst1", "catalyst2"],
            "news_count": number_of_relevant_articles,
            "explosion_catalysts": ["specific event 1", "specific event 2"],
            "timeframe": "7-30 days estimate",
            "risk_level": "low/medium/high"
        }}
    ],
    "total_analyzed": number_of_articles,
    "market_overview": "Brief market context (1 sentence)"
}}

IMPORTANT: 
- Return 3-5 opportunities SORTED from LOWEST to HIGHEST risk
- Focus on ACTIONABLE trading opportunities with clear entry points
- Include diverse risk levels (at least 1 low risk, 1-2 medium, 1-2 high)
- Be specific about catalysts and timing
- Identify ticker even if not explicitly mentioned (use company name)

Return ONLY valid JSON, no markdown or extra text."""

            # Generate cache key
            cache_key = self._get_cache_key('trending_analysis', {
                'article_count': len(news_articles),
                'first_title': news_articles[0].get('title', '') if news_articles else '',
                'watchlist': watchlist
            })
            
            # Get response from Gemini with caching
            result_text = self._execute_gemini_request(prompt, cache_key)
            
            if not result_text:
                # Quota exceeded or error - use fallback
                self.logger.warning("Gemini unavailable - using fallback analysis")
                return self._fallback_analysis(news_articles, watchlist or [])
            
            # Parse response
            import json
            
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
            opportunities = result.get('opportunities', [])
            if not opportunities:
                self.logger.warning("Gemini did not identify opportunities - using fallback")
                fallback = self._fallback_analysis(news_articles, watchlist or [])
                # Convert fallback to new format
                return {
                    'opportunities': [fallback],
                    'total_analyzed': len(news_articles),
                    'market_overview': 'Limited market analysis available',
                    'source': 'fallback',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Log opportunities found
            self.logger.info(f"🚀 Gemini identified {len(opportunities)} trading opportunities:")
            for i, opp in enumerate(opportunities, 1):
                self.logger.info(f"  {i}. {opp.get('ticker')} (Risk: {opp.get('risk_level')}, "
                               f"Confidence: {opp.get('confidence')}%) - {opp.get('reasoning', '')[:40]}...")
            
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
                'ticker': watchlist[0] if watchlist else 'AAPL',
                'confidence': 0,
                'reasoning': 'No specific stock trending in news. Showing default.',
                'sentiment': 'neutral',
                'key_topics': [],
                'news_count': 0,
                'explosion_catalysts': [],
                'timeframe': '7-30 days',
                'risk_level': 'medium',
                'source': 'fallback',
                'timestamp': datetime.now().isoformat()
            }
        
        trending_stock = max(mentions, key=mentions.get)
        news_count = mentions[trending_stock]
        
        return {
            'ticker': trending_stock,
            'confidence': min(news_count * 10, 100),  # Simple confidence score
            'reasoning': f"Most frequently mentioned in recent news ({news_count} mentions).",
            'sentiment': 'neutral',
            'key_topics': ['news', 'mentions'],
            'news_count': news_count,
            'explosion_catalysts': ['Multiple mentions'],
            'timeframe': '7-30 days',
            'risk_level': 'medium',
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

            cache_key = self._get_cache_key('market_insight', {
                'symbol': stock_data.get('symbol'),
                'price': stock_data.get('price'),
                'news_summary': news_summary[:200]
            })
            
            result_text = self._execute_gemini_request(prompt, cache_key)
            return result_text if result_text else None
            
        except Exception as e:
            self.logger.error(f"Failed to generate insight: {e}")
            return None
    
    def analyze_sentiment_ai(self, articles: List[Dict[str, Any]], symbol: str) -> Optional[Dict[str, Any]]:
        """
        Advanced sentiment analysis using Gemini AI
        
        Args:
            articles: List of news articles
            symbol: Stock symbol
            
        Returns:
            AI-powered sentiment analysis with detailed insights
        """
        if not self.enabled or not articles:
            return None
        
        try:
            # Prepare articles summary
            news_text = self._prepare_news_summary(articles[:30])
            
            prompt = f"""Analyze the sentiment and market implications for {symbol} based on these news articles:

{news_text}

Provide a comprehensive sentiment analysis in JSON format:
{{
    "sentiment_score": -1.0 to 1.0,
    "sentiment_label": "Very Positive/Positive/Neutral/Negative/Very Negative",
    "confidence": 0-100,
    "key_themes": ["theme1", "theme2", "theme3"],
    "bullish_factors": ["factor1", "factor2"],
    "bearish_factors": ["factor1", "factor2"],
    "market_impact": "High/Medium/Low",
    "sentiment_trend": "improving/stable/deteriorating",
    "ai_summary": "2-3 sentence summary of overall sentiment and implications"
}}

Consider:
- Overall tone and emotional content
- Specific events and their implications
- Market reaction expectations
- Trend changes in sentiment over time

Return ONLY valid JSON."""

            cache_key = self._get_cache_key('sentiment_analysis', {
                'symbol': symbol,
                'news_count': len(articles),
                'first_title': articles[0].get('title', '') if articles else ''
            })
            
            result_text = self._execute_gemini_request(prompt, cache_key)
            
            if not result_text:
                self.logger.warning("Gemini unavailable for sentiment analysis")
                return None
            
            # Clean markdown
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            
            import json
            result = json.loads(result_text)
            result['source'] = 'gemini-ai'
            result['articles_analyzed'] = len(articles)
            
            self.logger.info(f"✅ Gemini sentiment analysis for {symbol}: {result.get('sentiment_label')} ({result.get('sentiment_score')})")
            return result
            
        except Exception as e:
            self.logger.error(f"Gemini sentiment analysis failed: {e}")
            return None
    
    def predict_price_movement_ai(self, symbol: str, technical_data: Dict[str, Any], 
                                  news_articles: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        AI-powered price movement prediction using Gemini
        
        Args:
            symbol: Stock symbol
            technical_data: Technical indicators and price data
            news_articles: Recent news articles
            
        Returns:
            AI prediction with rationale
        """
        if not self.enabled:
            return None
        
        try:
            # Prepare context
            news_summary = self._prepare_news_summary(news_articles[:20]) if news_articles else "No recent news"
            
            prompt = f"""As an expert quantitative analyst, predict the price movement for {symbol} over the next 30 days.

TECHNICAL DATA:
- Current Price: ${technical_data.get('current_price', 0):.2f}
- RSI: {technical_data.get('rsi', 50):.1f}
- MACD: {technical_data.get('macd_signal', 'neutral')}
- Trend: {technical_data.get('trend', 'neutral')}
- Volume: {technical_data.get('volume_status', 'normal')}
- Volatility: {technical_data.get('volatility', 0):.2f}%

RECENT NEWS:
{news_summary[:1000]}

Provide prediction in JSON format:
{{
    "predicted_direction": "bullish/neutral/bearish",
    "predicted_change_pct": -50 to 50,
    "confidence": 0-100,
    "target_price": float,
    "support_level": float,
    "resistance_level": float,
    "key_catalysts": ["catalyst1", "catalyst2"],
    "key_risks": ["risk1", "risk2"],
    "time_horizon": "7-30 days",
    "reasoning": "Detailed 2-3 sentence explanation of prediction",
    "technical_factors": ["factor1", "factor2"],
    "fundamental_factors": ["factor1", "factor2"]
}}

Base your prediction on:
1. Technical setup and momentum
2. News sentiment and catalysts
3. Market context and sector trends
4. Historical patterns

Return ONLY valid JSON."""

            cache_key = self._get_cache_key('price_prediction', {
                'symbol': symbol,
                'current_price': technical_data.get('current_price'),
                'rsi': technical_data.get('rsi')
            })
            
            result_text = self._execute_gemini_request(prompt, cache_key)
            
            if not result_text:
                self.logger.warning("Gemini unavailable for price prediction")
                return None
            
            # Clean markdown
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            
            import json
            result = json.loads(result_text)
            result['source'] = 'gemini-ai'
            result['symbol'] = symbol
            result['prediction_date'] = datetime.now().isoformat()
            
            self.logger.info(f"🔮 Gemini prediction for {symbol}: {result.get('predicted_direction')} "
                           f"{result.get('predicted_change_pct'):+.1f}% (confidence: {result.get('confidence')}%)")
            return result
            
        except Exception as e:
            self.logger.error(f"Gemini price prediction failed: {e}")
            return None
    
    def detect_late_entry_risk(self, symbol: str, price_data: Dict[str, Any], 
                               news_articles: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Detect if it's too late to enter a position (FOMO detection)
        Analyzes price momentum, technical indicators, and timing to warn against buying at peaks
        
        Args:
            symbol: Stock symbol
            price_data: Dictionary with price and technical data
            news_articles: Optional news articles for context
            
        Returns:
            Dictionary with late entry risk assessment
        """
        if not self.enabled:
            return self._fallback_late_entry_check(price_data)
        
        try:
            # Prepare context
            news_summary = self._prepare_news_summary(news_articles[:20]) if news_articles else "No recent news"
            
            prompt = f"""As a risk management expert, analyze if it's too late to enter a position on {symbol}.

TECHNICAL DATA:
- Current Price: ${price_data.get('current_price', 0):.2f}
- 1-Day Change: {price_data.get('change_1d', 0):+.2f}%
- 5-Day Change: {price_data.get('change_5d', 0):+.2f}%
- 20-Day Change: {price_data.get('change_20d', 0):+.2f}%
- RSI: {price_data.get('rsi', 50):.1f}
- Distance from 20-day MA: {price_data.get('distance_from_ma20', 0):+.2f}%
- Distance from 50-day MA: {price_data.get('distance_from_ma50', 0):+.2f}%
- Volume vs Average: {price_data.get('volume_ratio', 1):.2f}x
- 52-Week High Distance: {price_data.get('distance_from_52w_high', 0):+.2f}%

RECENT NEWS:
{news_summary[:800]}

CRITICAL ANALYSIS - Determine if entry is risky (FOMO territory):

Consider these RED FLAGS:
1. 📈 **Parabolic Move**: >15% in 5 days or >30% in 20 days = likely overextended
2. 🔥 **Overbought**: RSI > 75 = exhaustion likely
3. 📏 **Too Far from MA**: >10% above 20-day MA = pullback risk
4. 🎯 **Near 52W High**: Within 2% of high = resistance zone
5. 📰 **News Already Priced In**: Event happened >3 days ago = missed move
6. 📊 **Volume Exhaustion**: High volume without follow-through = top formation

Provide analysis in JSON format:
{{
    "late_entry_risk": "LOW/MEDIUM/HIGH/CRITICAL",
    "risk_score": 0-100,
    "is_too_late": true/false,
    "recommended_action": "ENTER/WAIT_FOR_PULLBACK/AVOID",
    "key_risks": ["risk1", "risk2", "risk3"],
    "entry_timing": "EXCELLENT/GOOD/FAIR/POOR/TERRIBLE",
    "suggested_entry_price": float or null,
    "suggested_stop_loss": float or null,
    "pullback_probability": 0-100,
    "reasoning": "2-3 sentence explanation of why entry is/isn't risky",
    "alternative_strategy": "Suggestion if entry is too late"
}}

Be CONSERVATIVE. It's better to miss a move than to buy at the top.
Return ONLY valid JSON."""

            cache_key = self._get_cache_key('late_entry_risk', {
                'symbol': symbol,
                'current_price': price_data.get('current_price'),
                'rsi': price_data.get('rsi')
            })
            
            result_text = self._execute_gemini_request(prompt, cache_key)
            
            if not result_text:
                # Fallback - basic RSI-based assessment
                rsi = price_data.get('rsi', 50)
                if rsi > 75:
                    return {'late_entry_risk': 'CRITICAL', 'risk_score': 90, 'recommended_action': 'AVOID', 'reasoning': 'Extremely overbought (RSI > 75)'}
                elif rsi > 65:
                    return {'late_entry_risk': 'HIGH', 'risk_score': 75, 'recommended_action': 'WAIT', 'reasoning': 'Overbought conditions'}
                return {'late_entry_risk': 'MEDIUM', 'risk_score': 50, 'recommended_action': 'MONITOR', 'reasoning': 'Normal conditions'}
            
            # Clean markdown
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            
            import json
            result = json.loads(result_text)
            result['source'] = 'gemini-ai'
            result['symbol'] = symbol
            result['analysis_date'] = datetime.now().isoformat()
            
            self.logger.info(f"⚠️ Late entry risk for {symbol}: {result.get('late_entry_risk')} "
                           f"(risk score: {result.get('risk_score')}%) - {result.get('recommended_action')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Late entry detection failed: {e}")
            return self._fallback_late_entry_check(price_data)
    
    def _fallback_late_entry_check(self, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simple rule-based late entry check without AI
        """
        risk_score = 0
        key_risks = []
        
        # Check RSI
        rsi = price_data.get('rsi', 50)
        if rsi > 80:
            risk_score += 35
            key_risks.append("Extreme overbought (RSI > 80)")
        elif rsi > 70:
            risk_score += 25
            key_risks.append("Overbought conditions (RSI > 70)")
        
        # Check price extension
        change_5d = price_data.get('change_5d', 0)
        if change_5d > 20:
            risk_score += 30
            key_risks.append(f"Parabolic move: +{change_5d:.1f}% in 5 days")
        elif change_5d > 10:
            risk_score += 20
            key_risks.append(f"Strong move: +{change_5d:.1f}% in 5 days")
        
        # Check distance from MA
        distance_ma20 = price_data.get('distance_from_ma20', 0)
        if distance_ma20 > 15:
            risk_score += 25
            key_risks.append(f"Far from 20-MA: +{distance_ma20:.1f}%")
        elif distance_ma20 > 10:
            risk_score += 15
            key_risks.append(f"Extended from 20-MA: +{distance_ma20:.1f}%")
        
        # Check 52-week high proximity
        distance_52w = price_data.get('distance_from_52w_high', -10)
        if distance_52w > -2:
            risk_score += 10
            key_risks.append("Near 52-week high (resistance)")
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "CRITICAL"
            is_too_late = True
            action = "AVOID"
            timing = "TERRIBLE"
        elif risk_score >= 50:
            risk_level = "HIGH"
            is_too_late = True
            action = "WAIT_FOR_PULLBACK"
            timing = "POOR"
        elif risk_score >= 30:
            risk_level = "MEDIUM"
            is_too_late = False
            action = "ENTER"
            timing = "FAIR"
        else:
            risk_level = "LOW"
            is_too_late = False
            action = "ENTER"
            timing = "GOOD"
        
        return {
            'late_entry_risk': risk_level,
            'risk_score': risk_score,
            'is_too_late': is_too_late,
            'recommended_action': action,
            'key_risks': key_risks if key_risks else ["No significant risks detected"],
            'entry_timing': timing,
            'suggested_entry_price': None,
            'suggested_stop_loss': None,
            'pullback_probability': min(risk_score, 100),
            'reasoning': f"Rule-based assessment: {risk_level} risk based on technical indicators.",
            'alternative_strategy': "Wait for pullback to support levels" if is_too_late else "Entry conditions acceptable",
            'source': 'fallback',
            'analysis_date': datetime.now().isoformat()
        }
    
    def score_opportunity_ai(self, symbol: str, full_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        AI-powered opportunity scoring using Gemini
        
        Args:
            symbol: Stock symbol
            full_analysis: Complete analysis data (technical, sentiment, news)
            
        Returns:
            AI-generated opportunity score and recommendation
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""As a professional trader, score this trading opportunity for {symbol} on a 0-100 scale.

COMPLETE ANALYSIS:
{str(full_analysis)[:3000]}

Provide comprehensive scoring in JSON format:
{{
    "opportunity_score": 0-100,
    "recommendation": "STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL",
    "conviction": "High/Medium/Low",
    "entry_quality": 0-100,
    "risk_reward_quality": 0-100,
    "timing_quality": 0-100,
    "strengths": ["strength1", "strength2", "strength3"],
    "weaknesses": ["weakness1", "weakness2"],
    "critical_factors": ["factor1", "factor2"],
    "optimal_entry": float,
    "stop_loss": float,
    "profit_target": float,
    "position_sizing": "1-5% of portfolio",
    "time_horizon": "days/weeks/months",
    "ai_recommendation": "Detailed 3-4 sentence trading recommendation"
}}

Evaluate based on:
1. Technical setup quality (trend, momentum, support/resistance)
2. Risk/reward ratio
3. Sentiment and catalyst strength
4. Entry timing and market conditions
5. Overall probability of success

Be honest and critical. Return ONLY valid JSON."""

            cache_key = self._get_cache_key('opportunity_score', {
                'symbol': symbol,
                'confidence': full_analysis.get('confidence', 0)
            })
            
            result_text = self._execute_gemini_request(prompt, cache_key)
            
            if not result_text:
                # Fallback - basic scoring
                return {
                    'opportunity_score': 50,
                    'recommendation': 'HOLD',
                    'conviction': 'Low',
                    'ai_recommendation': 'AI analysis unavailable - proceed with caution'
                }
            
            # Clean markdown
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            
            import json
            result = json.loads(result_text)
            result['source'] = 'gemini-ai'
            result['symbol'] = symbol
            result['analysis_date'] = datetime.now().isoformat()
            
            self.logger.info(f"⭐ Gemini opportunity score for {symbol}: {result.get('opportunity_score')}/100 - {result.get('recommendation')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Gemini opportunity scoring failed: {e}")
            return None
    
    def validate_opportunity(self, symbol: str, opportunity: Dict[str, Any], 
                           symbol_news: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate an identified opportunity with symbol-specific news
        
        Args:
            symbol: Stock ticker
            opportunity: Initial opportunity data from market scan
            symbol_news: Symbol-specific news articles
            
        Returns:
            Validation result with confirmed status and updated confidence
        """
        if not self.enabled:
            return None
        
        try:
            # Format news for context
            news_context = "\n\n".join([
                f"**{article.get('title', 'N/A')}**\n"
                f"Source: {article.get('source', 'N/A')}\n"
                f"Published: {article.get('published_date', 'N/A')}\n"
                f"Description: {article.get('description', 'N/A')[:300]}"
                for article in symbol_news[:15]
            ])
            
            initial_reasoning = opportunity.get('reasoning', '')
            initial_confidence = opportunity.get('confidence', 0)
            risk_level = opportunity.get('risk_level', 'medium')
            catalysts = opportunity.get('explosion_catalysts', [])
            
            prompt = f"""You are a professional trading analyst. You previously identified {symbol} as a trading opportunity with {initial_confidence}% confidence and {risk_level} risk.

INITIAL ANALYSIS:
Reasoning: {initial_reasoning}
Catalysts: {', '.join(catalysts) if catalysts else 'None'}

NOW, validate this opportunity with {len(symbol_news)} symbol-specific news articles:

{news_context}

Critically analyze:
1. Are the initial catalysts CONFIRMED by specific news?
2. Any RED FLAGS or contradicting information?
3. Has the situation improved, worsened, or stayed the same?
4. Should confidence be adjusted up or down?
5. Should the opportunity be CONFIRMED or REJECTED?

Return ONLY valid JSON:
{{
    "confirmed": true/false,
    "confidence": 0-100,
    "confidence_change": -50 to +50,
    "reasoning": "2-3 sentence validation summary",
    "red_flags": ["flag1", "flag2"] or [],
    "supporting_factors": ["factor1", "factor2"],
    "recommendation": "STRONG_CONFIRM/CONFIRM/NEUTRAL/CAUTION/REJECT",
    "news_alignment": "Strong/Moderate/Weak/Contradictory",
    "updated_risk_level": "low/medium/high"
}}

Be brutally honest. If news contradicts the thesis, say so."""

            cache_key = self._get_cache_key('validate_opportunity', {
                'symbol': symbol,
                'initial_confidence': opportunity.get('confidence', 0),
                'news_count': len(symbol_news)
            })
            
            result_text = self._execute_gemini_request(prompt, cache_key)
            
            if not result_text:
                # Fallback - assume confirmed with lower confidence
                return {
                    'confirmed': True,
                    'confidence': opportunity.get('confidence', 50) - 10,
                    'confidence_change': -10,
                    'reasoning': 'AI validation unavailable - using conservative assessment',
                    'red_flags': [],
                    'recommendation': 'NEUTRAL',
                    'news_alignment': 'Unknown'
                }
            
            # Clean markdown
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            
            import json
            validation = json.loads(result_text)
            validation['validated_at'] = datetime.now().isoformat()
            validation['news_count'] = len(symbol_news)
            
            return validation
            
        except Exception as e:
            self.logger.error(f"Gemini validation failed for {symbol}: {e}")
            return None
