#!/usr/bin/env python3
"""
📅 Daily Update Script
Automated daily data updates for stock dashboard
Run via cron: 0 18 * * 1-5  (6 PM EST, Mon-Fri)
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.utils import load_config, setup_logging, is_market_open
from modules.database_manager import DatabaseManager
from modules.news_aggregator import NewsAggregator
from modules.social_aggregator import SocialAggregator
from modules.sentiment_analyzer import SentimentAnalyzer
from modules.monthly_signals import MonthlySignals
from modules.technical_indicators import TechnicalIndicators
from modules.alert_manager import AlertManager
import yfinance as yf


class DailyUpdater:
    """Automated daily update orchestrator"""
    
    def __init__(self):
        """Initialize updater"""
        self.config = load_config()
        setup_logging(self.config.get('logging', {}))
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.db = DatabaseManager(self.config.get('database', {}))
        self.news_aggregator = NewsAggregator(self.config)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.social_aggregator = SocialAggregator(self.config)
        self.technical_indicators = TechnicalIndicators()
        self.monthly_signals = MonthlySignals(
            self.config,
            self.sentiment_analyzer,
            self.technical_indicators
        )
        self.alert_manager = AlertManager(self.config)
        
        self.logger.info("Daily Updater initialized")
    
    def run(self):
        """Run complete daily update"""
        self.logger.info("=" * 60)
        self.logger.info("🚀 Starting Daily Update")
        self.logger.info(f"Timestamp: {datetime.now()}")
        self.logger.info("=" * 60)
        
        try:
            # Get watchlist
            watchlist = self._get_watchlist()
            self.logger.info(f"Processing {len(watchlist)} stocks: {', '.join(watchlist)}")
            
            # Process each stock
            for symbol in watchlist:
                self.logger.info(f"\n📊 Processing {symbol}...")
                try:
                    self._process_stock(symbol)
                    self.logger.info(f"✅ {symbol} completed")
                except Exception as e:
                    self.logger.error(f"❌ Error processing {symbol}: {e}", exc_info=True)
                    continue
            
            # Cleanup old data
            self._cleanup_old_data()
            
            # Generate summary
            self._generate_summary(watchlist)
            
            self.logger.info("\n" + "=" * 60)
            self.logger.info("✅ Daily Update Completed Successfully")
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.critical(f"💥 Daily update failed: {e}", exc_info=True)
            self.alert_manager.send_alert(
                "CRITICAL: Daily update failed",
                f"Error: {str(e)}",
                priority="CRITICAL"
            )
    
    def _get_watchlist(self):
        """Get stocks to process"""
        # Get from database
        db_watchlist = self.db.get_watchlist()
        if db_watchlist:
            return [item['symbol'] for item in db_watchlist]
        
        # Fallback to config
        watchlist_config = self.config.get('watchlist', {})
        if isinstance(watchlist_config, dict):
            return watchlist_config.get('stocks', [])
        elif isinstance(watchlist_config, list):
            return watchlist_config
        return []
    
    def _process_stock(self, symbol: str):
        """Complete processing for one stock"""
        
        # 1. Update price data
        self.logger.info(f"  1️⃣ Fetching price data...")
        price_data = self._fetch_price_data(symbol)
        
        if price_data is None or len(price_data) < 100:
            self.logger.warning(f"  ⚠️ Insufficient price data for {symbol}")
            return
        
        # Save to database
        self._save_price_data(symbol, price_data)
        
        # 2. Fetch news
        self.logger.info(f"  2️⃣ Fetching news...")
        news_articles = self.news_aggregator.fetch_all_news(symbol)
        self.logger.info(f"  📰 Found {len(news_articles)} articles")
        
        # 3. Analyze sentiment
        self.logger.info(f"  3️⃣ Analyzing sentiment...")
        news_sentiment = None
        if news_articles:
            news_sentiment = self.sentiment_analyzer.calculate_aggregate_sentiment(
                news_articles, 
                time_weight=True
            )
            self.logger.info(f"  💬 News sentiment: {news_sentiment.get('score', 0):.2f}")
        
        # 4. Fetch social mentions
        self.logger.info(f"  4️⃣ Fetching social mentions...")
        social_sentiment = None
        try:
            mentions = self.social_aggregator.fetch_reddit_mentions(symbol, limit=50)
            if mentions:
                social_sentiment = self.social_aggregator.calculate_social_sentiment(mentions)
                self.logger.info(f"  🗣️ Social sentiment: {social_sentiment.get('sentiment_score', 0):.2f}")
        except Exception as e:
            self.logger.warning(f"  ⚠️ Could not fetch social data: {e}")
        
        # 5. Calculate monthly score
        self.logger.info(f"  5️⃣ Calculating monthly signal...")
        score_data = self.monthly_signals.calculate_monthly_score(
            price_data,
            symbol,
            news_sentiment=news_sentiment,
            social_sentiment=social_sentiment
        )
        
        if score_data:
            self.logger.info(f"  🎯 Score: {score_data['total_score']}/100 - {score_data['recommendation']}")
            
            # Save to database
            self.db.save_monthly_score(
                symbol=symbol,
                score=score_data['total_score'],
                components=score_data['components'],
                recommendation=score_data['recommendation']
            )
            
            # Check for alerts
            self._check_alerts(symbol, score_data, news_sentiment, social_sentiment)
        else:
            self.logger.warning(f"  ⚠️ Could not calculate score for {symbol}")
    
    def _fetch_price_data(self, symbol: str):
        """Fetch latest price data"""
        try:
            ticker = yf.Ticker(symbol)
            # Get 1 year of data for indicator calculations
            data = ticker.history(period='1y')
            
            if data.empty:
                return None
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching price data: {e}")
            return None
    
    def _save_price_data(self, symbol: str, data):
        """Save price data to database"""
        try:
            for date, row in data.iterrows():
                self.db.save_stock_price(
                    symbol=symbol,
                    date=date.strftime('%Y-%m-%d'),
                    open=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    volume=row['Volume']
                )
        except Exception as e:
            self.logger.error(f"Error saving price data: {e}")
    
    def _check_alerts(self, symbol: str, score_data: dict, news_sentiment: dict, social_sentiment: dict):
        """Check and send alerts if conditions met"""
        score = score_data['total_score']
        recommendation = score_data['recommendation']
        
        # Strong signals
        if score >= 85:
            self.alert_manager.alert_monthly_signal(
                symbol=symbol,
                score=score,
                recommendation=recommendation,
                change=None
            )
        
        # Sentiment shifts
        if news_sentiment:
            sentiment_score = news_sentiment.get('score', 0)
            if abs(sentiment_score) > 0.6:  # Strong sentiment
                self.alert_manager.alert_sentiment_shift(
                    symbol=symbol,
                    old_sentiment=0,
                    new_sentiment=sentiment_score,
                    source="news"
                )
    
    def _cleanup_old_data(self):
        """Remove old data to save space"""
        self.logger.info("\n🧹 Cleaning up old data...")
        
        # Remove news articles older than 30 days
        cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # This would require adding a cleanup method to DatabaseManager
        # For now, just log
        self.logger.info(f"  Would clean data before {cutoff_date}")
    
    def _generate_summary(self, watchlist: list):
        """Generate update summary"""
        self.logger.info("\n📊 Update Summary")
        self.logger.info("-" * 60)
        
        # Get latest scores
        summary_data = []
        for symbol in watchlist:
            scores = self.db.get_monthly_score_history(symbol, days=1)
            if scores:
                latest = scores[0]
                summary_data.append({
                    'symbol': symbol,
                    'score': latest['score'],
                    'recommendation': latest['recommendation']
                })
        
        # Sort by score
        summary_data.sort(key=lambda x: x['score'], reverse=True)
        
        # Display
        for item in summary_data:
            self.logger.info(f"  {item['symbol']:6s} - {item['score']:3.0f}/100 - {item['recommendation']}")
        
        self.logger.info("-" * 60)


def main():
    """Main entry point"""
    updater = DailyUpdater()
    updater.run()


if __name__ == '__main__':
    main()
