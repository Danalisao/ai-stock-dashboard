"""
🔍 Opportunity Scanner - Détection automatique des pépites du mois
Scanne automatiquement des centaines d'actions pour détecter uniquement les meilleures opportunités
"""

import logging
import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from modules.technical_indicators import TechnicalIndicators
from modules.monthly_signals import MonthlySignals
from modules.sentiment_analyzer import SentimentAnalyzer
from modules.news_aggregator import NewsAggregator


class OpportunityScanner:
    """Scanner automatique des meilleures opportunités de trading du mois"""
    
    # Critères stricts pour qualifier une opportunité comme "pépite"
    MIN_SCORE = 85.0  # Score minimum pour être considéré comme pépite
    MIN_RISK_REWARD = 2.5  # Ratio risque/récompense minimum
    MIN_CONFIDENCE = 0.7  # Confiance minimum
    MIN_VOLUME_RATIO = 1.3  # Volume minimum vs moyenne
    
    # Watchlist étendue - Actions liquides et volatiles (meilleures pour le trading)
    EXTENDED_WATCHLIST = {
        # MEGA CAPS (Liquidité extrême)
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'GOOGL': 'Alphabet Inc.',
        'AMZN': 'Amazon.com Inc.',
        'NVDA': 'NVIDIA Corporation',
        'META': 'Meta Platforms Inc.',
        'TSLA': 'Tesla Inc.',
        'BRK.B': 'Berkshire Hathaway',
        'V': 'Visa Inc.',
        'JNJ': 'Johnson & Johnson',
        'WMT': 'Walmart Inc.',
        'JPM': 'JPMorgan Chase',
        'MA': 'Mastercard Inc.',
        'PG': 'Procter & Gamble',
        'UNH': 'UnitedHealth Group',
        'HD': 'Home Depot',
        'DIS': 'Walt Disney',
        'BAC': 'Bank of America',
        'NFLX': 'Netflix Inc.',
        'CRM': 'Salesforce Inc.',
        
        # TECH & GROWTH
        'AMD': 'Advanced Micro Devices',
        'INTC': 'Intel Corporation',
        'CSCO': 'Cisco Systems',
        'ORCL': 'Oracle Corporation',
        'ADBE': 'Adobe Inc.',
        'AVGO': 'Broadcom Inc.',
        'QCOM': 'QUALCOMM Inc.',
        'TXN': 'Texas Instruments',
        'IBM': 'IBM',
        'SNOW': 'Snowflake Inc.',
        'PLTR': 'Palantir Technologies',
        'COIN': 'Coinbase Global',
        'SQ': 'Block Inc.',
        'PYPL': 'PayPal Holdings',
        'SHOP': 'Shopify Inc.',
        'ZM': 'Zoom Video',
        'UBER': 'Uber Technologies',
        'LYFT': 'Lyft Inc.',
        'ABNB': 'Airbnb Inc.',
        'DASH': 'DoorDash Inc.',
        
        # SEMICONDUCTORS (Très volatils)
        'TSM': 'Taiwan Semiconductor',
        'ASML': 'ASML Holding',
        'MU': 'Micron Technology',
        'AMAT': 'Applied Materials',
        'LRCX': 'Lam Research',
        'KLAC': 'KLA Corporation',
        'MRVL': 'Marvell Technology',
        'ON': 'ON Semiconductor',
        
        # ENERGY (Momentum stocks)
        'XOM': 'Exxon Mobil',
        'CVX': 'Chevron Corporation',
        'COP': 'ConocoPhillips',
        'SLB': 'Schlumberger',
        'EOG': 'EOG Resources',
        'MPC': 'Marathon Petroleum',
        'PSX': 'Phillips 66',
        
        # FINANCE
        'GS': 'Goldman Sachs',
        'MS': 'Morgan Stanley',
        'C': 'Citigroup',
        'WFC': 'Wells Fargo',
        'AXP': 'American Express',
        'BLK': 'BlackRock Inc.',
        'SCHW': 'Charles Schwab',
        
        # CONSUMER & RETAIL
        'AMGN': 'Amgen Inc.',
        'COST': 'Costco Wholesale',
        'NKE': 'Nike Inc.',
        'SBUX': 'Starbucks Corporation',
        'MCD': 'McDonald\'s Corporation',
        'TGT': 'Target Corporation',
        'LOW': 'Lowe\'s Companies',
        'TJX': 'TJX Companies',
        
        # HEALTHCARE & BIOTECH
        'PFE': 'Pfizer Inc.',
        'ABBV': 'AbbVie Inc.',
        'TMO': 'Thermo Fisher Scientific',
        'ABT': 'Abbott Laboratories',
        'DHR': 'Danaher Corporation',
        'BMY': 'Bristol-Myers Squibb',
        'LLY': 'Eli Lilly',
        'GILD': 'Gilead Sciences',
        'MRNA': 'Moderna Inc.',
        'BIIB': 'Biogen Inc.',
        
        # INDUSTRIAL & AEROSPACE
        'BA': 'Boeing Company',
        'CAT': 'Caterpillar Inc.',
        'HON': 'Honeywell International',
        'LMT': 'Lockheed Martin',
        'RTX': 'Raytheon Technologies',
        'GE': 'General Electric',
        'DE': 'Deere & Company',
        
        # TELECOM & MEDIA
        'T': 'AT&T Inc.',
        'VZ': 'Verizon Communications',
        'CMCSA': 'Comcast Corporation',
        'TMUS': 'T-Mobile US',
        
        # AUTOMOTIVE & EV
        'F': 'Ford Motor Company',
        'GM': 'General Motors',
        'RIVN': 'Rivian Automotive',
        'LCID': 'Lucid Group',
        'NIO': 'NIO Inc.',
        
        # ETFS (Momentum et secteurs)
        'SPY': 'S&P 500 ETF',
        'QQQ': 'NASDAQ-100 ETF',
        'IWM': 'Russell 2000 ETF',
        'DIA': 'Dow Jones ETF',
        'XLF': 'Financial Sector ETF',
        'XLE': 'Energy Sector ETF',
        'XLK': 'Technology Sector ETF',
        'XLV': 'Healthcare Sector ETF',
        'XLI': 'Industrial Sector ETF',
        'XLP': 'Consumer Staples ETF',
        'XLY': 'Consumer Discretionary ETF',
    }
    
    def __init__(self, config: Dict[str, Any], gemini_analyzer=None):
        """
        Initialize opportunity scanner
        
        Args:
            config: Configuration dictionary
            gemini_analyzer: Optional GeminiAnalyzer for AI-powered opportunity detection
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.gemini_analyzer = gemini_analyzer
        
        # Initialize components (with Gemini integration)
        self.technical_indicators = TechnicalIndicators()
        self.sentiment_analyzer = SentimentAnalyzer(config, gemini_analyzer)
        self.news_aggregator = NewsAggregator(config)
        self.monthly_signals = MonthlySignals(
            config,
            self.sentiment_analyzer,
            self.technical_indicators
        )
        
        # Scanner settings
        self.watchlist = list(self.EXTENDED_WATCHLIST.keys())
        self.max_workers = 10  # Parallel processing
        self.scan_period = '3mo'  # 3 mois de données historiques
        
        if gemini_analyzer and gemini_analyzer.enabled:
            self.logger.info(f"🤖 Opportunity Scanner initialized with Gemini AI ({len(self.watchlist)} stocks)")
        else:
            self.logger.info(f"Opportunity Scanner initialized ({len(self.watchlist)} stocks)")
    
    def scan_all_opportunities(self, custom_watchlist: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Scan all stocks in watchlist and return only top opportunities
        
        Args:
            custom_watchlist: Optional custom list of symbols to scan
            
        Returns:
            List of opportunity dictionaries, sorted by score (descending)
        """
        watchlist = custom_watchlist or self.watchlist
        opportunities = []
        
        self.logger.info(f"Starting scan of {len(watchlist)} stocks...")
        start_time = time.time()
        
        # Parallel scanning for speed
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_symbol = {
                executor.submit(self._analyze_stock, symbol): symbol 
                for symbol in watchlist
            }
            
            completed = 0
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                completed += 1
                
                try:
                    result = future.result()
                    if result and self._is_golden_opportunity(result):
                        opportunities.append(result)
                        self.logger.info(
                            f"🌟 PÉPITE DÉTECTÉE: {symbol} - Score: {result['score']:.1f} "
                            f"(R/R: {result['risk_reward']:.2f})"
                        )
                except Exception as e:
                    self.logger.error(f"Error analyzing {symbol}: {e}")
                
                # Progress logging every 10 stocks
                if completed % 10 == 0:
                    self.logger.info(f"Progress: {completed}/{len(watchlist)} stocks analyzed")
        
        # Sort by score (descending)
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        elapsed = time.time() - start_time
        self.logger.info(
            f"Scan completed in {elapsed:.1f}s - Found {len(opportunities)} opportunities "
            f"out of {len(watchlist)} stocks analyzed"
        )
        
        return opportunities
    
    def _analyze_stock(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a single stock for trading opportunities
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Opportunity dictionary if meets criteria, None otherwise
        """
        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=self.scan_period)
            
            if data.empty or len(data) < 50:
                return None
            
            # Calculate technical indicators
            indicators = self.technical_indicators.calculate_all_indicators(data)
            
            # Fetch sentiment data
            news_sentiment = self._get_quick_sentiment(symbol)
            
            # Calculate monthly score
            score_data = self.monthly_signals.calculate_monthly_score(
                data, 
                symbol,
                news_sentiment,
                None  # social_sentiment
            )
            
            # Get current market data
            current_price = data['Close'].iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            avg_volume = data['Volume'].tail(20).mean()
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            # Calculate volatility
            returns = data['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) * 100  # Annualized volatility %
            
            # Build opportunity object
            opportunity = {
                'symbol': symbol,
                'name': self.EXTENDED_WATCHLIST.get(symbol, symbol),
                'scan_date': datetime.now().isoformat(),
                'score': score_data['total_score'],
                'recommendation': score_data['recommendation']['action'],
                'conviction': score_data['recommendation']['conviction'],
                
                # Trading parameters
                'current_price': round(current_price, 2),
                'entry_price': score_data['entry_price'],
                'stop_loss': score_data['stop_loss'],
                'target_price': score_data['target_price'],
                'risk_reward': score_data['risk_reward_ratio'],
                
                # Risk metrics
                'stop_loss_pct': round(((score_data['entry_price'] - score_data['stop_loss']) / score_data['entry_price']) * 100, 2),
                'target_pct': round(((score_data['target_price'] - score_data['entry_price']) / score_data['entry_price']) * 100, 2),
                
                # Market context
                'volume_ratio': round(volume_ratio, 2),
                'volatility': round(volatility, 2),
                'confidence': score_data['confidence'],
                
                # Score breakdown
                'trend_score': score_data['trend_score'],
                'momentum_score': score_data['momentum_score'],
                'sentiment_score': score_data['sentiment_score'],
                'divergence_score': score_data['divergence_score'],
                'volume_score': score_data['volume_score'],
                
                # Additional context
                'position_size': score_data['recommendation']['position_size'],
                'description': score_data['recommendation']['description'],
            }
            
            # 🤖 ENHANCE WITH GEMINI AI if available
            if self.gemini_analyzer and self.gemini_analyzer.enabled:
                try:
                    # Prepare full analysis for Gemini
                    full_analysis = {
                        'symbol': symbol,
                        'price_data': {
                            'current': current_price,
                            'entry': score_data['entry_price'],
                            'target': score_data['target_price'],
                            'stop_loss': score_data['stop_loss']
                        },
                        'technical_scores': {
                            'trend': score_data['trend_score'],
                            'momentum': score_data['momentum_score'],
                            'volume': score_data['volume_score'],
                            'divergence': score_data['divergence_score']
                        },
                        'sentiment': {
                            'score': score_data['sentiment_score'],
                            'news': news_sentiment
                        },
                        'risk_metrics': {
                            'risk_reward': score_data['risk_reward_ratio'],
                            'volatility': volatility,
                            'volume_ratio': volume_ratio
                        },
                        'overall_score': score_data['total_score']
                    }
                    
                    gemini_score = self.gemini_analyzer.score_opportunity_ai(symbol, full_analysis)
                    
                    if gemini_score:
                        # Blend traditional and AI scores
                        ai_opportunity_score = gemini_score.get('opportunity_score', score_data['total_score'])
                        blended_score = (score_data['total_score'] * 0.6) + (ai_opportunity_score * 0.4)
                        
                        opportunity['score'] = round(blended_score, 1)
                        opportunity['ai_score'] = ai_opportunity_score
                        opportunity['ai_recommendation'] = gemini_score.get('ai_recommendation')
                        opportunity['ai_strengths'] = gemini_score.get('strengths', [])
                        opportunity['ai_weaknesses'] = gemini_score.get('weaknesses', [])
                        opportunity['ai_conviction'] = gemini_score.get('conviction')
                        opportunity['source'] = 'hybrid-gemini'
                        
                        self.logger.debug(f"✅ Enhanced {symbol} with Gemini: {blended_score:.1f}")
                except Exception as e:
                    self.logger.debug(f"Gemini enhancement failed for {symbol}: {e}")
            
            return opportunity
            
        except Exception as e:
            self.logger.debug(f"Could not analyze {symbol}: {e}")
            return None
    
    def _is_golden_opportunity(self, opportunity: Dict[str, Any]) -> bool:
        """
        Determine if this is a golden opportunity (pépite) worth alerting on
        
        Strict criteria:
        - Score >= 85 (Strong Buy territory)
        - Risk/Reward >= 2.5
        - Confidence >= 0.7
        - Volume ratio >= 1.3
        - All component scores > 70 (no weak areas)
        
        Args:
            opportunity: Opportunity dictionary
            
        Returns:
            True if meets all criteria
        """
        # Core criteria
        if opportunity['score'] < self.MIN_SCORE:
            return False
        
        if opportunity['risk_reward'] < self.MIN_RISK_REWARD:
            return False
        
        if opportunity['confidence'] < self.MIN_CONFIDENCE:
            return False
        
        if opportunity['volume_ratio'] < self.MIN_VOLUME_RATIO:
            return False
        
        # All components must be strong (no weak link)
        component_scores = [
            opportunity['trend_score'],
            opportunity['momentum_score'],
            opportunity['sentiment_score'],
            opportunity['divergence_score'],
            opportunity['volume_score']
        ]
        
        if min(component_scores) < 70:
            return False
        
        # Volatility check (not too high, not too low)
        volatility = opportunity['volatility']
        if volatility < 15 or volatility > 80:
            return False
        
        return True
    
    def _get_quick_sentiment(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get quick sentiment analysis for a symbol
        Returns None if not available (to avoid slowing down scan)
        """
        try:
            # Quick sentiment check (use cached if available)
            news = self.news_aggregator.fetch_yahoo_finance_news(symbol, max_articles=5)
            if news:
                sentiment = self.sentiment_analyzer.analyze_batch_sentiment(news)
                return sentiment
        except:
            pass
        
        return None
    
    def get_top_opportunities(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get top N opportunities
        
        Args:
            n: Number of top opportunities to return
            
        Returns:
            List of top N opportunities
        """
        all_opportunities = self.scan_all_opportunities()
        return all_opportunities[:n]
    
    def generate_alert_message(self, opportunity: Dict[str, Any]) -> str:
        """
        Generate formatted alert message for an opportunity
        
        Args:
            opportunity: Opportunity dictionary
            
        Returns:
            Formatted alert message
        """
        msg = f"""
🚨 PÉPITE DÉTECTÉE - {opportunity['symbol']} 🚨

📊 {opportunity['name']}
🎯 Score: {opportunity['score']:.1f}/100 - {opportunity['recommendation']}
💪 Conviction: {opportunity['conviction']}

📈 PARAMÈTRES DE TRADING:
• Prix actuel: ${opportunity['current_price']:.2f}
• 🟢 Entrée: ${opportunity['entry_price']:.2f}
• 🎯 Take Profit: ${opportunity['target_price']:.2f} (+{opportunity['target_pct']:.1f}%)
• 🛑 Stop Loss: ${opportunity['stop_loss']:.2f} (-{opportunity['stop_loss_pct']:.1f}%)
• ⚖️ Risk/Reward: 1:{opportunity['risk_reward']:.2f}

📊 ANALYSE:
• Trend: {opportunity['trend_score']:.0f}/100
• Momentum: {opportunity['momentum_score']:.0f}/100
• Sentiment: {opportunity['sentiment_score']:.0f}/100
• Volume: {opportunity['volume_ratio']:.1f}x normal
• Volatilité: {opportunity['volatility']:.1f}%

💼 POSITION:
• Taille recommandée: {opportunity['position_size']}
• Confiance: {opportunity['confidence']*100:.0f}%

📝 {opportunity['description']}

⏰ Détecté le: {datetime.fromisoformat(opportunity['scan_date']).strftime('%Y-%m-%d %H:%M')}
"""
        return msg.strip()
    
    def export_opportunities_to_dataframe(self, opportunities: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Export opportunities to pandas DataFrame for easy viewing
        
        Args:
            opportunities: List of opportunity dictionaries
            
        Returns:
            DataFrame with key metrics
        """
        if not opportunities:
            return pd.DataFrame()
        
        # Select key columns
        df = pd.DataFrame(opportunities)
        
        # Reorder columns for readability
        columns = [
            'symbol', 'name', 'score', 'recommendation',
            'current_price', 'entry_price', 'target_price', 'stop_loss',
            'target_pct', 'stop_loss_pct', 'risk_reward',
            'volume_ratio', 'confidence', 'scan_date'
        ]
        
        # Only include columns that exist
        columns = [col for col in columns if col in df.columns]
        
        return df[columns]
    
    def save_opportunities_to_csv(self, opportunities: List[Dict[str, Any]], 
                                   filename: str = 'opportunities.csv'):
        """
        Save opportunities to CSV file
        
        Args:
            opportunities: List of opportunity dictionaries
            filename: Output filename
        """
        df = self.export_opportunities_to_dataframe(opportunities)
        
        if not df.empty:
            filepath = f"data/{filename}"
            df.to_csv(filepath, index=False)
            self.logger.info(f"Saved {len(opportunities)} opportunities to {filepath}")
        else:
            self.logger.warning("No opportunities to save")
