#!/usr/bin/env python3
"""
🤖 Automatic Opportunity Detection & Alerts
Scans market for LOW RISK opportunities and sends automatic alerts
Respects market hours: Mon-Fri 9:30 AM - 4:00 PM ET

Usage:
    python scripts/auto_opportunity_alerts.py --interval 60
    
    --interval: Minutes between scans (default: 60)
    --continuous: Run continuously during market hours
    --once: Run once and exit
"""

import sys
import os
from pathlib import Path
import time
import argparse
from datetime import datetime, timedelta
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from modules.utils import load_config, setup_logging, is_market_open, get_next_market_open
from modules.database_manager import DatabaseManager
from modules.news_aggregator import NewsAggregator
from modules.gemini_analyzer import GeminiAnalyzer
from modules.alert_manager import AlertManager


class AutoOpportunityScanner:
    """
    Automatic opportunity scanner with smart alerting
    - Scans market during business hours
    - Detects LOW RISK opportunities with Gemini AI
    - Sends automatic Telegram/Email alerts
    - Respects rate limits and market hours
    """
    
    def __init__(self, scan_interval_minutes: int = 60):
        """
        Initialize scanner
        
        Args:
            scan_interval_minutes: Minutes between scans (default: 60)
        """
        self.config = load_config()
        setup_logging(self.config.get('logging', {}))
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.db = DatabaseManager(self.config.get('database', {}))
        self.news_aggregator = NewsAggregator(self.config)
        self.gemini_analyzer = GeminiAnalyzer(self.config)
        self.alert_manager = AlertManager(self.config)
        
        # Scan parameters
        self.scan_interval = scan_interval_minutes * 60  # Convert to seconds
        self.min_articles = 30  # Minimum articles for analysis
        self.max_articles = 100  # Maximum articles to analyze
        
        # State tracking
        self.last_scan_time = None
        self.opportunities_sent = set()  # Track sent alerts to avoid duplicates
        self.scan_count = 0
        
        # Get watchlist for prioritization
        db_watchlist = self.db.get_watchlist()
        self.watchlist = [item['symbol'] for item in db_watchlist] if db_watchlist else None
        
        self.logger.info("🤖 Automatic Opportunity Scanner initialized")
        self.logger.info(f"⏱️  Scan interval: {scan_interval_minutes} minutes")
        self.logger.info(f"🎯 Watchlist: {len(self.watchlist) if self.watchlist else 'All'} stocks")
        
        # Check Gemini AI status
        if not self.gemini_analyzer.enabled:
            self.logger.error("❌ Gemini AI not enabled! Cannot detect opportunities.")
            raise RuntimeError("Gemini API key required in .env file")
    
    def run_once(self) -> dict:
        """
        Run a single scan and return results
        
        Returns:
            Dictionary with scan results and alerts sent
        """
        self.logger.info("=" * 70)
        self.logger.info(f"🔍 OPPORTUNITY SCAN #{self.scan_count + 1}")
        self.logger.info(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 70)
        
        results = {
            'scan_time': datetime.now().isoformat(),
            'opportunities_found': 0,
            'alerts_sent': 0,
            'errors': []
        }
        
        try:
            # Check market status
            market_open = is_market_open()
            results['market_open'] = market_open
            
            if not market_open:
                next_open = get_next_market_open()
                self.logger.info(f"🔴 Market closed. Next open: {next_open.strftime('%Y-%m-%d %H:%M %Z')}")
                results['next_market_open'] = next_open.isoformat()
                return results
            
            self.logger.info("🟢 Market is OPEN - Starting scan...")
            
            # Step 1: Fetch market news
            self.logger.info(f"📰 Fetching market news (up to {self.max_articles} articles)...")
            news_articles = self.news_aggregator.fetch_market_news(max_articles=self.max_articles)
            
            if not news_articles or len(news_articles) < self.min_articles:
                error_msg = f"Insufficient news articles: {len(news_articles) if news_articles else 0}"
                self.logger.warning(f"⚠️  {error_msg}")
                results['errors'].append(error_msg)
                return results
            
            self.logger.info(f"✅ Fetched {len(news_articles)} articles from multiple sources")
            
            # Step 2: Analyze with Gemini AI
            self.logger.info("🤖 Analyzing with Gemini AI...")
            analysis_result = self.gemini_analyzer.analyze_trending_stock(
                news_articles,
                watchlist=self.watchlist
            )
            
            if not analysis_result or 'opportunities' not in analysis_result:
                error_msg = "No opportunities detected by Gemini AI"
                self.logger.warning(f"⚠️  {error_msg}")
                results['errors'].append(error_msg)
                return results
            
            opportunities = analysis_result.get('opportunities', [])
            results['opportunities_found'] = len(opportunities)
            
            self.logger.info(f"✅ Found {len(opportunities)} opportunities")
            
            # Step 3: Filter LOW RISK opportunities (highest priority)
            low_risk_opportunities = [
                opp for opp in opportunities 
                if opp.get('risk_level') == 'low'
            ]
            
            self.logger.info(f"💎 LOW RISK opportunities: {len(low_risk_opportunities)}")
            
            if not low_risk_opportunities:
                self.logger.info("ℹ️  No LOW RISK opportunities found this scan")
                return results
            
            # Step 4: Send alerts for each LOW RISK opportunity
            for opp in low_risk_opportunities:
                symbol = opp.get('ticker', 'N/A')
                confidence = opp.get('confidence', 0)
                
                # Check if already sent recently (avoid spam)
                alert_key = f"{symbol}_{datetime.now().date()}"
                if alert_key in self.opportunities_sent:
                    self.logger.info(f"⏭️  Skipping {symbol} (alert already sent today)")
                    continue
                
                self.logger.info(f"🚨 Sending alert for {symbol} (confidence: {confidence}%)...")
                
                try:
                    success = self.alert_manager.send_opportunity_alert(opp)
                    
                    if success:
                        self.logger.info(f"✅ Alert sent successfully for {symbol}")
                        self.opportunities_sent.add(alert_key)
                        results['alerts_sent'] += 1
                        
                        # Save to database
                        self.db.save_opportunity(
                            symbol=symbol,
                            confidence=confidence,
                            risk_level='low',
                            reasoning=opp.get('reasoning', ''),
                            catalysts=opp.get('explosion_catalysts', []),
                            source='gemini_ai',
                            alert_sent=True
                        )
                    else:
                        self.logger.warning(f"⚠️  Failed to send alert for {symbol}")
                        results['errors'].append(f"Alert failed for {symbol}")
                
                except Exception as e:
                    error_msg = f"Error sending alert for {symbol}: {e}"
                    self.logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            # Update scan state
            self.last_scan_time = datetime.now()
            self.scan_count += 1
            
            self.logger.info("=" * 70)
            self.logger.info(f"✅ Scan complete: {results['alerts_sent']} alerts sent")
            self.logger.info("=" * 70)
            
        except Exception as e:
            error_msg = f"Scan error: {e}"
            self.logger.error(error_msg, exc_info=True)
            results['errors'].append(error_msg)
        
        return results
    
    def run_continuous(self):
        """
        Run continuously, respecting market hours
        """
        self.logger.info("=" * 70)
        self.logger.info("🚀 STARTING CONTINUOUS OPPORTUNITY SCANNER")
        self.logger.info("=" * 70)
        self.logger.info(f"⏱️  Scan interval: {self.scan_interval // 60} minutes")
        self.logger.info(f"🕐 Respects market hours: Mon-Fri 9:30 AM - 4:00 PM ET")
        self.logger.info(f"🎯 Alert priority: LOW RISK opportunities only")
        self.logger.info("=" * 70)
        
        while True:
            try:
                # Check market status first
                if not is_market_open():
                    next_open = get_next_market_open()
                    wait_seconds = (next_open - datetime.now(next_open.tzinfo)).total_seconds()
                    wait_minutes = int(wait_seconds / 60)
                    
                    self.logger.info(f"🔴 Market closed. Sleeping until {next_open.strftime('%Y-%m-%d %H:%M %Z')}")
                    self.logger.info(f"⏳ Waiting {wait_minutes} minutes...")
                    
                    # Sleep in chunks to allow graceful shutdown
                    while wait_seconds > 0 and not is_market_open():
                        sleep_time = min(3600, wait_seconds)  # Sleep max 1 hour at a time
                        time.sleep(sleep_time)
                        wait_seconds -= sleep_time
                    
                    continue
                
                # Run scan
                results = self.run_once()
                
                # Calculate next scan time
                next_scan = datetime.now() + timedelta(seconds=self.scan_interval)
                
                self.logger.info(f"⏳ Next scan at: {next_scan.strftime('%H:%M:%S')}")
                self.logger.info(f"💤 Sleeping for {self.scan_interval // 60} minutes...")
                
                # Sleep until next scan
                time.sleep(self.scan_interval)
                
            except KeyboardInterrupt:
                self.logger.info("\n" + "=" * 70)
                self.logger.info("⏹️  Scanner stopped by user")
                self.logger.info(f"📊 Total scans completed: {self.scan_count}")
                self.logger.info(f"📨 Total alerts sent: {len(self.opportunities_sent)}")
                self.logger.info("=" * 70)
                break
            
            except Exception as e:
                self.logger.error(f"❌ Scanner error: {e}", exc_info=True)
                self.logger.info("⏳ Waiting 5 minutes before retry...")
                time.sleep(300)  # Wait 5 minutes on error


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Automatic LOW RISK opportunity detection with alerts'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Minutes between scans during market hours (default: 60)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (useful for cron jobs)'
    )
    parser.add_argument(
        '--continuous',
        action='store_true',
        default=True,
        help='Run continuously during market hours (default)'
    )
    
    args = parser.parse_args()
    
    try:
        scanner = AutoOpportunityScanner(scan_interval_minutes=args.interval)
        
        if args.once:
            print("\n🔄 Running single scan...\n")
            results = scanner.run_once()
            
            print("\n" + "=" * 70)
            print("📊 SCAN RESULTS")
            print("=" * 70)
            print(f"Opportunities found: {results['opportunities_found']}")
            print(f"Alerts sent: {results['alerts_sent']}")
            if results.get('errors'):
                print(f"Errors: {len(results['errors'])}")
                for error in results['errors']:
                    print(f"  • {error}")
            print("=" * 70 + "\n")
        else:
            scanner.run_continuous()
    
    except KeyboardInterrupt:
        print("\n⏹️  Stopped by user\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
