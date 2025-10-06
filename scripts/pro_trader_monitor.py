#!/usr/bin/env python3
"""
🚀 PROFESSIONAL TRADER MONITOR - 24/7 OPPORTUNITY HUNTER
═══════════════════════════════════════════════════════════════════
Monitoring système optimisé pour trader opportuniste professionnel
Détection aggressive des pump stocks et opportunités explosives

FEATURES:
- 🌅 Pre-market monitoring (4:00-9:30 AM ET) - Detection d'earnings, FDA, M&A
- 📊 Real-time pump detection (volume surge + price spike)
- 🤖 AI-powered opportunity discovery avec Gemini
- 🚨 Multi-channel instant alerts (Telegram prioritaire)
- 💎 Focus sur les mouvements > 5% avec volume exceptionnel
- ⚡ Latence minimale - Alertes en < 30 secondes

USAGE:
    python scripts/pro_trader_monitor.py                    # Monitoring complet 24/7
    python scripts/pro_trader_monitor.py --premarket-only   # Prémarché uniquement
    python scripts/pro_trader_monitor.py --aggressive       # Mode ultra-agressif
    
DEPLOYMENT:
    nohup python scripts/pro_trader_monitor.py > logs/monitor.log 2>&1 &
    
STOP:
    pkill -f pro_trader_monitor.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
import pytz
from collections import defaultdict
import yfinance as yf
import pandas as pd
import numpy as np

from dotenv import load_dotenv
load_dotenv()

from modules.utils import load_config, is_market_open, get_robust_ticker
from modules.news_aggregator import NewsAggregator
from modules.alert_manager import AlertManager
from modules.database_manager import DatabaseManager
from modules.gemini_analyzer import GeminiAnalyzer
from modules.sentiment_analyzer import SentimentAnalyzer


class ProTraderMonitor:
    """
    Professional 24/7 trading opportunity monitor
    Optimized for aggressive day/swing trading
    """
    
    def __init__(self, config_path: str = 'config.yaml', aggressive_mode: bool = False):
        """Initialize professional monitoring system"""
        self.config = load_config(config_path)
        self.logger = self._setup_logger()
        self.aggressive_mode = aggressive_mode
        
        # Initialize core modules
        self.news_aggregator = NewsAggregator(self.config)
        self.alert_manager = AlertManager(self.config)
        self.db = DatabaseManager(self.config.get('database', {}))
        self.gemini_analyzer = GeminiAnalyzer(self.config)
        self.sentiment_analyzer = SentimentAnalyzer(self.config, self.gemini_analyzer)
        
        # Tracking state
        self.alerted_opportunities: Set[str] = set()  # Symbol tracking
        self.price_cache: Dict[str, float] = {}
        self.volume_cache: Dict[str, float] = {}
        self.last_premarket_scan = datetime.min
        self.last_opportunity_scan = datetime.min
        self.pump_candidates: Dict[str, Dict] = {}  # Recent pump detections
        
        # Professional thresholds (aggressive for opportunities)
        if aggressive_mode:
            self.PRICE_THRESHOLD = 3.0  # 3%+ move
            self.VOLUME_THRESHOLD = 1.5  # 1.5x volume
            self.PREMARKET_SCAN_INTERVAL = 10  # 10 min
            self.MARKET_SCAN_INTERVAL = 60  # 1 min
            self.OPPORTUNITY_SCAN_INTERVAL = 30  # 30 min
        else:
            self.PRICE_THRESHOLD = 5.0  # 5%+ move
            self.VOLUME_THRESHOLD = 2.0  # 2x volume
            self.PREMARKET_SCAN_INTERVAL = 15  # 15 min
            self.MARKET_SCAN_INTERVAL = 180  # 3 min
            self.OPPORTUNITY_SCAN_INTERVAL = 60  # 60 min
        
        self.logger.info("=" * 70)
        self.logger.info("🚀 PROFESSIONAL TRADER MONITOR INITIALIZED")
        self.logger.info("=" * 70)
        self.logger.info(f"Mode: {'AGGRESSIVE 🔥' if aggressive_mode else 'STANDARD'}")
        self.logger.info(f"Gemini AI: {'ENABLED ✅' if self.gemini_analyzer.enabled else 'DISABLED ❌'}")
        self.logger.info(f"Alert Channels: Telegram, Email, Desktop, Audio")
        self.logger.info(f"Price Threshold: {self.PRICE_THRESHOLD}%")
        self.logger.info(f"Volume Threshold: {self.VOLUME_THRESHOLD}x")
        self.logger.info("=" * 70)
    
    def _setup_logger(self) -> logging.Logger:
        """Setup dedicated logger for monitor"""
        logger = logging.getLogger('ProTraderMonitor')
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # File handler
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / 'pro_monitor.log')
        file_handler.setLevel(logging.DEBUG)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def is_premarket_hours(self) -> bool:
        """Check if current time is pre-market (4:00-9:30 AM ET)"""
        try:
            et_tz = pytz.timezone('America/New_York')
            now_et = datetime.now(et_tz)
            premarket_start = now_et.replace(hour=4, minute=0, second=0, microsecond=0)
            premarket_end = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
            return premarket_start <= now_et <= premarket_end
        except Exception as e:
            self.logger.error(f"Error checking premarket hours: {e}")
            return False
    
    def is_market_hours(self) -> bool:
        """Check if market is open (9:30 AM - 4:00 PM ET)"""
        return is_market_open()
    
    def get_market_phase(self) -> str:
        """Get current market phase"""
        if self.is_premarket_hours():
            return "PREMARKET"
        elif self.is_market_hours():
            return "MARKET_OPEN"
        else:
            return "AFTER_HOURS"
    
    def scan_premarket_catalysts(self) -> int:
        """
        Scan for pre-market catalysts (earnings, FDA, M&A, guidance)
        Returns: Number of alerts sent
        """
        self.logger.info("🌅 PREMARKET CATALYST SCAN")
        
        try:
            # Fetch pre-market announcements
            announcements = self.news_aggregator.fetch_premarket_announcements()
            
            if not announcements:
                self.logger.info("   ✓ No new premarket catalysts")
                return 0
            
            # Filter high-priority only
            critical_announcements = [
                ann for ann in announcements
                if ann.get('priority') in ['CRITICAL', 'HIGH']
            ]
            
            self.logger.info(f"   📰 Found {len(announcements)} announcements")
            self.logger.info(f"   🚨 {len(critical_announcements)} CRITICAL/HIGH priority")
            
            # Send alerts
            alerts_sent = 0
            for announcement in critical_announcements:
                symbol = announcement.get('symbol')
                
                # Deduplicate
                alert_key = f"{symbol}_{hash(announcement.get('title', ''))}"
                if alert_key in self.alerted_opportunities:
                    continue
                
                if self.alert_manager.alert_premarket_announcement(announcement):
                    alerts_sent += 1
                    self.alerted_opportunities.add(alert_key)
                    self.logger.info(f"   ✅ Alert sent: {symbol} | {announcement.get('priority')}")
                
                time.sleep(0.3)  # Rate limiting
            
            return alerts_sent
            
        except Exception as e:
            self.logger.error(f"Premarket scan error: {e}")
            return 0
    
    def scan_pump_stocks(self, watchlist: Optional[List[str]] = None) -> List[Dict]:
        """
        Detect pump stocks (volume surge + price spike)
        Returns: List of pump candidates
        """
        self.logger.info("💎 PUMP STOCK SCAN")
        
        pumps = []
        
        try:
            # Get watchlist
            if not watchlist:
                watchlist = self._get_enhanced_watchlist()
            
            self.logger.info(f"   Scanning {len(watchlist)} symbols...")
            
            for symbol in watchlist:
                try:
                    ticker = get_robust_ticker(symbol)
                    
                    # Get current quote
                    info = ticker.info
                    current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                    
                    if not current_price:
                        continue
                    
                    # Check price change
                    prev_close = info.get('previousClose', info.get('regularMarketPreviousClose'))
                    if not prev_close or prev_close <= 0:
                        continue
                    
                    price_change_pct = ((current_price - prev_close) / prev_close) * 100
                    
                    # Check volume
                    volume = info.get('volume', 0)
                    avg_volume = info.get('averageVolume', volume)
                    volume_ratio = volume / avg_volume if avg_volume > 0 else 0
                    
                    # PUMP DETECTION: Price spike + Volume surge
                    if (abs(price_change_pct) >= self.PRICE_THRESHOLD and 
                        volume_ratio >= self.VOLUME_THRESHOLD):
                        
                        pump_data = {
                            'symbol': symbol,
                            'price': current_price,
                            'price_change_pct': price_change_pct,
                            'volume': volume,
                            'avg_volume': avg_volume,
                            'volume_ratio': volume_ratio,
                            'direction': 'UP' if price_change_pct > 0 else 'DOWN',
                            'timestamp': datetime.now(),
                            'market_cap': info.get('marketCap', 0)
                        }
                        
                        pumps.append(pump_data)
                        
                        self.logger.info(
                            f"   🚀 PUMP DETECTED: {symbol} | "
                            f"{price_change_pct:+.2f}% | "
                            f"{volume_ratio:.1f}x volume"
                        )
                    
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    self.logger.debug(f"Error scanning {symbol}: {e}")
                    continue
            
            if pumps:
                self.logger.info(f"   ✅ Detected {len(pumps)} pump stocks")
                # Sort by combined score (price change * volume ratio)
                pumps.sort(
                    key=lambda x: abs(x['price_change_pct']) * x['volume_ratio'],
                    reverse=True
                )
            else:
                self.logger.info("   ✓ No pump stocks detected")
            
            return pumps
            
        except Exception as e:
            self.logger.error(f"Pump scan error: {e}")
            return []
    
    def scan_ai_opportunities(self) -> List[Dict]:
        """
        Scan for AI-discovered trading opportunities (Gemini-powered)
        Returns: List of opportunities
        """
        self.logger.info("🤖 AI OPPORTUNITY SCAN")
        
        if not self.gemini_analyzer.enabled:
            self.logger.warning("   ⚠️ Gemini AI not available - skipping")
            return []
        
        try:
            # Fetch market news
            news = self.news_aggregator.fetch_market_news(max_articles=100)
            
            if not news or len(news) < 10:
                self.logger.info("   ✓ Insufficient news for AI analysis")
                return []
            
            self.logger.info(f"   Analyzing {len(news)} market articles...")
            
            # Get AI-powered opportunities
            analysis = self.gemini_analyzer.analyze_trending_stock(news)
            
            if not analysis:
                self.logger.info("   ✓ No AI opportunities detected")
                return []
            
            opportunities = analysis.get('opportunities', [])
            
            if not opportunities:
                # Legacy format fallback
                if 'trending_stock' in analysis:
                    opportunities = [{
                        'ticker': analysis.get('trending_stock'),
                        'confidence': analysis.get('confidence', 0),
                        'reasoning': analysis.get('reasoning', ''),
                        'risk_level': analysis.get('risk_level', 'medium')
                    }]
            
            # Filter for high-confidence opportunities
            high_confidence = [
                opp for opp in opportunities
                if opp.get('confidence', 0) >= 70
            ]
            
            self.logger.info(f"   🎯 Found {len(opportunities)} opportunities")
            self.logger.info(f"   💎 {len(high_confidence)} high-confidence (≥70%)")
            
            return high_confidence
            
        except Exception as e:
            self.logger.error(f"AI opportunity scan error: {e}")
            return []
    
    def send_pump_alert(self, pump: Dict) -> bool:
        """Send alert for pump stock detection"""
        try:
            symbol = pump['symbol']
            price_change = pump['price_change_pct']
            volume_ratio = pump['volume_ratio']
            direction = pump['direction']
            
            emoji = "🚀" if direction == "UP" else "📉"
            
            message = f"""
{emoji} PUMP STOCK DETECTED {emoji}

📊 Symbol: {symbol}
💰 Price: ${pump['price']:.2f} ({price_change:+.2f}%)
📊 Volume: {volume_ratio:.1f}x average
📈 Direction: {direction}
💎 Market Cap: ${pump['market_cap'] / 1e9:.2f}B

⚡ INSTANT ACTION REQUIRED
"""
            
            # Determine priority
            if abs(price_change) >= 10 or volume_ratio >= 5:
                priority = 'CRITICAL'
            elif abs(price_change) >= 7 or volume_ratio >= 3:
                priority = 'HIGH'
            else:
                priority = 'MEDIUM'
            
            # Send alert
            success = self.alert_manager.send_alert(
                alert_type='PUMP_DETECTED',
                symbol=symbol,
                message=message,
                priority=priority,
                value=price_change,
                data={
                    'volume_ratio': volume_ratio,
                    'direction': direction,
                    'market_cap': pump['market_cap']
                }
            )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending pump alert: {e}")
            return False
    
    def send_opportunity_alerts(self, opportunities: List[Dict]) -> int:
        """Send alerts for AI opportunities"""
        alerts_sent = 0
        
        for opp in opportunities:
            symbol = opp.get('ticker')
            
            # Deduplicate
            if symbol in self.alerted_opportunities:
                continue
            
            try:
                if self.alert_manager.send_opportunity_alert(opp):
                    alerts_sent += 1
                    self.alerted_opportunities.add(symbol)
                    self.logger.info(f"   ✅ Opportunity alert sent: {symbol}")
                
                time.sleep(0.3)
                
            except Exception as e:
                self.logger.error(f"Error sending opportunity alert for {symbol}: {e}")
                continue
        
        return alerts_sent
    
    def _get_enhanced_watchlist(self) -> List[str]:
        """Get enhanced watchlist (database + config + top movers)"""
        watchlist = set()
        
        # Database watchlist
        db_watchlist = self.db.get_watchlist()
        if db_watchlist:
            watchlist.update([item['symbol'] for item in db_watchlist])
        
        # Config watchlist
        config_watchlist = self.config.get('watchlist', {}).get('stocks', [])
        watchlist.update(config_watchlist)
        
        # Add popular tickers
        popular = ['SPY', 'QQQ', 'AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META']
        watchlist.update(popular)
        
        return list(watchlist)
    
    def run_cycle(self, premarket_only: bool = False):
        """
        Run one complete monitoring cycle
        
        Args:
            premarket_only: If True, only run premarket monitoring
        """
        phase = self.get_market_phase()
        
        self.logger.info("")
        self.logger.info("┌" + "─" * 68 + "┐")
        self.logger.info(f"│ MONITORING CYCLE | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Phase: {phase:12} │")
        self.logger.info("└" + "─" * 68 + "┘")
        
        alerts_sent = 0
        
        # PREMARKET: Catalyst monitoring (4:00-9:30 AM ET)
        if phase == "PREMARKET":
            now = datetime.now()
            if (now - self.last_premarket_scan).seconds >= self.PREMARKET_SCAN_INTERVAL * 60:
                alerts_sent += self.scan_premarket_catalysts()
                self.last_premarket_scan = now
        
        # MARKET HOURS: Real-time pump detection
        if phase == "MARKET_OPEN" and not premarket_only:
            pumps = self.scan_pump_stocks()
            
            for pump in pumps[:5]:  # Top 5 pumps
                symbol = pump['symbol']
                
                # Deduplicate (alert once per hour per symbol)
                last_pump = self.pump_candidates.get(symbol, {}).get('timestamp')
                if last_pump and (datetime.now() - last_pump).seconds < 3600:
                    continue
                
                if self.send_pump_alert(pump):
                    alerts_sent += 1
                    self.pump_candidates[symbol] = pump
        
        # AI OPPORTUNITY SCAN (all phases, periodic)
        if not premarket_only:
            now = datetime.now()
            if (now - self.last_opportunity_scan).seconds >= self.OPPORTUNITY_SCAN_INTERVAL * 60:
                opportunities = self.scan_ai_opportunities()
                alerts_sent += self.send_opportunity_alerts(opportunities)
                self.last_opportunity_scan = now
        
        # Summary
        self.logger.info(f"Cycle complete | Alerts sent: {alerts_sent}")
    
    def run(self, premarket_only: bool = False):
        """
        Main monitoring loop - runs 24/7
        
        Args:
            premarket_only: If True, only monitor premarket hours
        """
        self.logger.info("")
        self.logger.info("╔" + "═" * 68 + "╗")
        self.logger.info("║" + " " * 15 + "PROFESSIONAL TRADER MONITOR - ONLINE" + " " * 15 + "║")
        self.logger.info("╚" + "═" * 68 + "╝")
        self.logger.info("")
        
        if premarket_only:
            self.logger.info("🌅 MODE: PREMARKET ONLY")
        else:
            self.logger.info("🔄 MODE: 24/7 CONTINUOUS MONITORING")
        
        self.logger.info("Press Ctrl+C to stop")
        self.logger.info("")
        
        try:
            while True:
                phase = self.get_market_phase()
                
                # Skip if premarket_only and not premarket
                if premarket_only and phase != "PREMARKET":
                    self.logger.info(f"⏸️ Not premarket hours - sleeping...")
                    time.sleep(300)  # 5 minutes
                    continue
                
                # Run monitoring cycle
                self.run_cycle(premarket_only)
                
                # Dynamic sleep based on phase
                if phase == "PREMARKET":
                    sleep_time = self.PREMARKET_SCAN_INTERVAL * 60
                elif phase == "MARKET_OPEN":
                    sleep_time = self.MARKET_SCAN_INTERVAL
                else:  # After hours
                    sleep_time = 600  # 10 minutes
                
                self.logger.info(f"⏳ Next cycle in {sleep_time // 60} min {sleep_time % 60} sec")
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.logger.info("")
            self.logger.info("╔" + "═" * 68 + "╗")
            self.logger.info("║" + " " * 20 + "MONITOR STOPPED BY USER" + " " * 21 + "║")
            self.logger.info("╚" + "═" * 68 + "╝")
        
        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
            raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Professional Trader Monitor - 24/7 Opportunity Hunter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Full 24/7 monitoring
  python scripts/pro_trader_monitor.py
  
  # Premarket only (4:00-9:30 AM ET)
  python scripts/pro_trader_monitor.py --premarket-only
  
  # Aggressive mode (lower thresholds, faster scans)
  python scripts/pro_trader_monitor.py --aggressive
  
  # Background deployment
  nohup python scripts/pro_trader_monitor.py > logs/monitor.log 2>&1 &

DEPLOYMENT (Linux/Mac):
  # Add to crontab for auto-start on reboot
  @reboot cd /path/to/project && nohup python scripts/pro_trader_monitor.py &

DEPLOYMENT (Windows):
  # Use Task Scheduler to run on system startup
  Action: Start program
  Program: python.exe
  Arguments: C:\\path\\to\\project\\scripts\\pro_trader_monitor.py
  Start in: C:\\path\\to\\project
        """
    )
    
    parser.add_argument(
        '--premarket-only',
        action='store_true',
        help='Monitor premarket hours only (4:00-9:30 AM ET)'
    )
    
    parser.add_argument(
        '--aggressive',
        action='store_true',
        help='Aggressive mode: lower thresholds, faster scans'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Config file path (default: config.yaml)'
    )
    
    args = parser.parse_args()
    
    # Initialize and run
    monitor = ProTraderMonitor(
        config_path=args.config,
        aggressive_mode=args.aggressive
    )
    
    monitor.run(premarket_only=args.premarket_only)


if __name__ == '__main__':
    main()
