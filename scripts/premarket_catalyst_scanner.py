#!/usr/bin/env python3
"""
🌅 PRE-MARKET CATALYST SCANNER - PROFESSIONAL EDITION
═══════════════════════════════════════════════════════════════════
Scanner ultra-réactif pour détecter les catalyseurs explosifs
avant l'ouverture du marché (4h00-9h30 AM ET)

DETECTED CATALYSTS:
- 💰 EARNINGS: Résultats beat/miss avec volume prémarché
- 💊 FDA: Approbations médicaments (biotech moonshots)
- 🤝 M&A: Fusions/acquisitions/buyouts
- 📊 GUIDANCE: Révisions guidance (upgrades/downgrades)
- 🚨 BANKRUPTCY: Faillites (short opportunities)
- 💎 UNUSUAL VOLUME: Volume prémarché > 5x normal

LATENCY TARGET: < 15 seconds from announcement to Telegram alert

USAGE:
    python scripts/premarket_catalyst_scanner.py
    
DEPLOYMENT (Auto-start at 4h AM):
    # Linux/Mac cron
    0 4 * * 1-5 cd /path/to/project && python scripts/premarket_catalyst_scanner.py
    
    # Windows Task Scheduler
    Trigger: Daily at 4:00 AM
    Action: python.exe premarket_catalyst_scanner.py
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
import time
import pytz
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import yfinance as yf
import pandas as pd
from collections import defaultdict

from modules.utils import load_config, get_robust_ticker
from modules.news_aggregator import NewsAggregator
from modules.alert_manager import AlertManager
from modules.database_manager import DatabaseManager
from modules.gemini_analyzer import GeminiAnalyzer


class PremarketCatalystScanner:
    """
    Ultra-fast pre-market catalyst detection system
    Designed for professional traders seeking explosive opportunities
    """
    
    def __init__(self):
        """Initialize catalyst scanner"""
        self.config = load_config()
        self.logger = self._setup_logger()
        
        # Core modules
        self.news_aggregator = NewsAggregator(self.config)
        self.alert_manager = AlertManager(self.config)
        self.db = DatabaseManager(self.config.get('database', {}))
        self.gemini_analyzer = GeminiAnalyzer(self.config)
        
        # Tracking
        self.alerted_catalysts: Set[str] = set()  # Cache to avoid duplicate alerts
        self.last_scan_time = datetime.min
        
        # Professional thresholds
        self.PREMARKET_VOLUME_THRESHOLD = 5.0  # 5x normal volume
        self.PREMARKET_PRICE_THRESHOLD = 3.0  # 3%+ move
        self.SCAN_INTERVAL_SECONDS = 300  # 5 minutes (aggressive)
        
        # Catalyst priority weights
        self.CATALYST_WEIGHTS = {
            'earnings': 0.85,  # High impact
            'fda': 0.95,  # Explosive for biotech
            'm&a': 0.90,  # Market movers
            'bankruptcy': 0.80,  # Short opportunities
            'guidance': 0.75,  # Significant moves
            'unusual_volume': 0.70,  # Attention grabber
        }
        
        self.logger.info("=" * 70)
        self.logger.info("🌅 PRE-MARKET CATALYST SCANNER - PROFESSIONAL EDITION")
        self.logger.info("=" * 70)
        self.logger.info(f"Scan Interval: {self.SCAN_INTERVAL_SECONDS}s")
        self.logger.info(f"Volume Threshold: {self.PREMARKET_VOLUME_THRESHOLD}x")
        self.logger.info(f"Price Threshold: {self.PREMARKET_PRICE_THRESHOLD}%")
        self.logger.info(f"Gemini AI: {'ENABLED ✅' if self.gemini_analyzer.enabled else 'DISABLED ❌'}")
        self.logger.info("=" * 70)
    
    def _setup_logger(self) -> logging.Logger:
        """Setup dedicated logger"""
        logger = logging.getLogger('PremarketScanner')
        logger.setLevel(logging.INFO)
        
        # Console
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        
        # File
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / 'premarket_scanner.log')
        file_handler.setLevel(logging.DEBUG)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console)
        logger.addHandler(file_handler)
        
        return logger
    
    def is_premarket_hours(self) -> bool:
        """Check if current time is pre-market (4:00-9:30 AM ET)"""
        try:
            et_tz = pytz.timezone('America/New_York')
            now_et = datetime.now(et_tz)
            
            # Pre-market: 4:00 AM - 9:30 AM ET (Monday-Friday)
            if now_et.weekday() > 4:  # Saturday/Sunday
                return False
            
            premarket_start = now_et.replace(hour=4, minute=0, second=0, microsecond=0)
            premarket_end = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
            
            return premarket_start <= now_et <= premarket_end
            
        except Exception as e:
            self.logger.error(f"Error checking premarket hours: {e}")
            return False
    
    def scan_news_catalysts(self) -> List[Dict]:
        """
        Scan news for pre-market catalysts
        
        Returns:
            List of detected catalysts with priority
        """
        self.logger.info("📰 Scanning news for catalysts...")
        
        try:
            # Fetch pre-market announcements (method from news_aggregator)
            announcements = self.news_aggregator.fetch_premarket_announcements()
            
            if not announcements:
                self.logger.info("   No announcements found")
                return []
            
            # Filter for high-priority only
            critical_announcements = [
                ann for ann in announcements
                if ann.get('priority') in ['CRITICAL', 'HIGH']
            ]
            
            self.logger.info(f"   Found {len(announcements)} announcements")
            self.logger.info(f"   {len(critical_announcements)} CRITICAL/HIGH priority")
            
            # Enhance with real-time price data
            enhanced_catalysts = []
            for ann in critical_announcements:
                symbol = ann.get('symbol')
                
                if not symbol or symbol == 'UNKNOWN':
                    continue
                
                # Skip if already alerted
                cache_key = f"{symbol}_{ann.get('title', '')[:50]}"
                if cache_key in self.alerted_catalysts:
                    continue
                
                # Get pre-market price movement
                price_data = self._get_premarket_price_data(symbol)
                
                if price_data:
                    ann['premarket_data'] = price_data
                    
                    # Calculate composite score
                    score = self._calculate_catalyst_score(ann, price_data)
                    ann['score'] = score
                    
                    # Only alert if score > 70
                    if score >= 70:
                        enhanced_catalysts.append(ann)
                        self.alerted_catalysts.add(cache_key)
                else:
                    # No price data, but still alert if catalyst is critical
                    if ann.get('priority') == 'CRITICAL':
                        ann['score'] = 75  # Default high score
                        enhanced_catalysts.append(ann)
                        self.alerted_catalysts.add(cache_key)
            
            # Sort by score (highest first)
            enhanced_catalysts.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            return enhanced_catalysts
            
        except Exception as e:
            self.logger.error(f"Error scanning news catalysts: {e}")
            return []
    
    def scan_unusual_volume(self, watchlist: List[str] = None) -> List[Dict]:
        """
        Scan for unusual pre-market volume
        
        Args:
            watchlist: Optional list of symbols to monitor
            
        Returns:
            List of stocks with unusual volume
        """
        self.logger.info("📊 Scanning for unusual pre-market volume...")
        
        unusual_stocks = []
        
        try:
            # Get watchlist
            if not watchlist:
                watchlist = self._get_premarket_watchlist()
            
            self.logger.info(f"   Monitoring {len(watchlist)} symbols")
            
            for symbol in watchlist:
                try:
                    # Get pre-market data
                    price_data = self._get_premarket_price_data(symbol)
                    
                    if not price_data:
                        continue
                    
                    volume_ratio = price_data.get('volume_ratio', 0)
                    price_change = price_data.get('change_pct', 0)
                    
                    # Filter for unusual activity
                    if (volume_ratio >= self.PREMARKET_VOLUME_THRESHOLD or 
                        abs(price_change) >= self.PREMARKET_PRICE_THRESHOLD):
                        
                        # Skip if already alerted
                        cache_key = f"{symbol}_volume_{datetime.now().strftime('%Y%m%d')}"
                        if cache_key in self.alerted_catalysts:
                            continue
                        
                        # Calculate score
                        score = self._calculate_volume_score(price_data)
                        
                        if score >= 70:
                            unusual_stocks.append({
                                'symbol': symbol,
                                'type': 'unusual_volume',
                                'score': score,
                                'premarket_data': price_data,
                                'priority': 'HIGH' if score >= 85 else 'MEDIUM'
                            })
                            
                            self.alerted_catalysts.add(cache_key)
                    
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    self.logger.debug(f"Error scanning {symbol}: {e}")
                    continue
            
            if unusual_stocks:
                self.logger.info(f"   ✅ Found {len(unusual_stocks)} stocks with unusual volume")
            else:
                self.logger.info("   No unusual volume detected")
            
            return unusual_stocks
            
        except Exception as e:
            self.logger.error(f"Error scanning unusual volume: {e}")
            return []
    
    def _get_premarket_price_data(self, symbol: str) -> Optional[Dict]:
        """
        Get pre-market price and volume data
        
        Args:
            symbol: Stock ticker
            
        Returns:
            Dict with premarket data or None
        """
        try:
            ticker = get_robust_ticker(symbol)
            if not ticker:
                return None
            
            # Get current price (includes pre-market)
            info = ticker.info
            
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            previous_close = info.get('previousClose')
            
            if not current_price or not previous_close:
                return None
            
            # Calculate change
            change_pct = ((current_price - previous_close) / previous_close) * 100
            
            # Get volume (yfinance includes pre-market in 'volume')
            current_volume = info.get('volume', 0)
            avg_volume = info.get('averageVolume', 1)
            
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            return {
                'current_price': current_price,
                'previous_close': previous_close,
                'change_pct': change_pct,
                'current_volume': current_volume,
                'avg_volume': avg_volume,
                'volume_ratio': volume_ratio,
                'market_cap': info.get('marketCap', 0),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.debug(f"Error getting premarket data for {symbol}: {e}")
            return None
    
    def _calculate_catalyst_score(self, catalyst: Dict, price_data: Dict) -> float:
        """
        Calculate composite score for catalyst opportunity
        
        Score components:
        - Catalyst type weight (40%)
        - Price movement magnitude (30%)
        - Volume surge (20%)
        - AI confidence (10%)
        
        Returns:
            Score 0-100
        """
        try:
            # Catalyst weight
            catalyst_types = catalyst.get('catalysts', [])
            max_weight = 0
            
            for c_type in catalyst_types:
                for key, weight in self.CATALYST_WEIGHTS.items():
                    if key in c_type.lower():
                        max_weight = max(max_weight, weight)
            
            catalyst_score = max_weight * 40
            
            # Price movement
            price_change = abs(price_data.get('change_pct', 0))
            price_score = min(price_change / 10 * 30, 30)  # Max 30 points
            
            # Volume surge
            volume_ratio = price_data.get('volume_ratio', 0)
            volume_score = min(volume_ratio / 5 * 20, 20)  # Max 20 points
            
            # AI confidence (if available)
            ai_confidence = catalyst.get('ai_confidence', 50)
            ai_score = (ai_confidence / 100) * 10
            
            total_score = catalyst_score + price_score + volume_score + ai_score
            
            return min(total_score, 100)
            
        except Exception as e:
            self.logger.error(f"Error calculating catalyst score: {e}")
            return 50  # Default mid-range score
    
    def _calculate_volume_score(self, price_data: Dict) -> float:
        """Calculate score for unusual volume (no news catalyst)"""
        try:
            volume_ratio = price_data.get('volume_ratio', 0)
            price_change = abs(price_data.get('change_pct', 0))
            
            # Volume component (60%)
            volume_score = min(volume_ratio / 10 * 60, 60)
            
            # Price component (40%)
            price_score = min(price_change / 10 * 40, 40)
            
            return min(volume_score + price_score, 100)
            
        except Exception as e:
            return 50
    
    def _get_premarket_watchlist(self) -> List[str]:
        """Get watchlist for pre-market monitoring"""
        watchlist = set()
        
        # Database watchlist
        db_watchlist = self.db.get_watchlist()
        if db_watchlist:
            watchlist.update(db_watchlist)
        
        # Config watchlist
        config_watchlist = self.config.get('watchlist', {}).get('stocks', [])
        watchlist.update(config_watchlist)
        
        # Popular movers (likely to have pre-market action)
        popular = [
            # Tech
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'AMD', 'NFLX',
            # Biotech (FDA catalysts)
            'MRNA', 'BNTX', 'PFE', 'JNJ', 'GILD', 'REGN', 'VRTX', 'AMGN',
            # Financials
            'JPM', 'BAC', 'GS', 'MS', 'WFC',
            # Retail/Consumer
            'WMT', 'TGT', 'HD', 'LOW', 'COST',
            # Energy
            'XOM', 'CVX', 'COP', 'SLB',
            # ETFs
            'SPY', 'QQQ', 'IWM', 'DIA'
        ]
        watchlist.update(popular)
        
        return list(watchlist)
    
    def send_catalyst_alert(self, catalyst: Dict) -> bool:
        """Send alert for detected catalyst"""
        try:
            symbol = catalyst.get('symbol', 'UNKNOWN')
            score = catalyst.get('score', 0)
            priority = catalyst.get('priority', 'MEDIUM')
            catalyst_type = catalyst.get('type', 'catalyst')
            
            # Format message based on catalyst type
            if catalyst_type == 'unusual_volume':
                message = self._format_volume_alert(catalyst)
            else:
                message = self._format_catalyst_alert(catalyst)
            
            # Send via AlertManager
            success = self.alert_manager.send_alert(
                alert_type='PREMARKET_CATALYST',
                symbol=symbol,
                message=message,
                priority=priority,
                value=score,
                data=catalyst
            )
            
            # Store in database
            if success:
                self.db.store_alert({
                    'symbol': symbol,
                    'alert_type': 'PREMARKET_CATALYST',
                    'message': message,
                    'priority': priority,
                    'score': score,
                    'timestamp': datetime.now().isoformat()
                })
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending catalyst alert: {e}")
            return False
    
    def _format_catalyst_alert(self, catalyst: Dict) -> str:
        """Format news catalyst alert message"""
        symbol = catalyst.get('symbol', 'N/A')
        score = catalyst.get('score', 0)
        title = catalyst.get('title', '')
        catalysts = catalyst.get('catalysts', [])
        price_data = catalyst.get('premarket_data', {})
        
        # Price info
        price_change = price_data.get('change_pct', 0)
        volume_ratio = price_data.get('volume_ratio', 0)
        current_price = price_data.get('current_price', 0)
        
        emoji = "🚀" if price_change > 0 else "📉"
        
        message = f"""
{emoji} PRE-MARKET CATALYST DETECTED {emoji}

📊 Symbol: {symbol}
💯 Score: {score:.1f}/100
💰 Price: ${current_price:.2f} ({price_change:+.2f}%)
📈 Volume: {volume_ratio:.1f}x average

⚡ Catalysts:
{', '.join(catalysts[:3])}

📰 Headline:
{title[:200]}

🕐 Detected: {datetime.now().strftime('%H:%M:%S ET')}
"""
        
        return message
    
    def _format_volume_alert(self, catalyst: Dict) -> str:
        """Format unusual volume alert message"""
        symbol = catalyst.get('symbol', 'N/A')
        score = catalyst.get('score', 0)
        price_data = catalyst.get('premarket_data', {})
        
        price_change = price_data.get('change_pct', 0)
        volume_ratio = price_data.get('volume_ratio', 0)
        current_price = price_data.get('current_price', 0)
        
        emoji = "💎" if abs(price_change) >= 5 else "📊"
        
        message = f"""
{emoji} UNUSUAL PRE-MARKET VOLUME {emoji}

📊 Symbol: {symbol}
💯 Score: {score:.1f}/100
💰 Price: ${current_price:.2f} ({price_change:+.2f}%)
📈 Volume: {volume_ratio:.1f}x average

⚠️ No news catalyst - investigate manually!

🕐 Detected: {datetime.now().strftime('%H:%M:%S ET')}
"""
        
        return message
    
    def run_scan_cycle(self) -> int:
        """
        Run one complete scan cycle
        
        Returns:
            Number of alerts sent
        """
        alerts_sent = 0
        
        self.logger.info("")
        self.logger.info("┌" + "─" * 68 + "┐")
        self.logger.info(f"│ SCAN CYCLE | {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')} {'':20} │")
        self.logger.info("└" + "─" * 68 + "┘")
        
        try:
            # 1. Scan news catalysts
            news_catalysts = self.scan_news_catalysts()
            
            for catalyst in news_catalysts:
                if self.send_catalyst_alert(catalyst):
                    alerts_sent += 1
                time.sleep(1)  # Rate limiting between alerts
            
            # 2. Scan unusual volume
            volume_alerts = self.scan_unusual_volume()
            
            for alert in volume_alerts:
                if self.send_catalyst_alert(alert):
                    alerts_sent += 1
                time.sleep(1)
            
            self.logger.info(f"✅ Scan complete | Alerts sent: {alerts_sent}")
            
        except Exception as e:
            self.logger.error(f"Error in scan cycle: {e}")
        
        return alerts_sent
    
    def run(self):
        """Main monitoring loop - runs during pre-market hours"""
        self.logger.info("")
        self.logger.info("╔" + "═" * 68 + "╗")
        self.logger.info("║" + " " * 15 + "🌅 PRE-MARKET CATALYST SCANNER ONLINE" + " " * 14 + "║")
        self.logger.info("╚" + "═" * 68 + "╝")
        self.logger.info("")
        self.logger.info("Monitoring: 4:00 AM - 9:30 AM ET")
        self.logger.info("Press Ctrl+C to stop")
        self.logger.info("")
        
        try:
            while True:
                # Check if pre-market hours
                if not self.is_premarket_hours():
                    et_tz = pytz.timezone('America/New_York')
                    now_et = datetime.now(et_tz)
                    
                    # If before 4 AM, wait until 4 AM
                    if now_et.hour < 4:
                        next_scan = now_et.replace(hour=4, minute=0, second=0)
                        wait_seconds = (next_scan - now_et).total_seconds()
                        self.logger.info(f"⏰ Waiting for pre-market open at 4:00 AM ET...")
                        self.logger.info(f"   Next scan in {wait_seconds/3600:.1f} hours")
                        time.sleep(min(wait_seconds, 3600))  # Max 1 hour sleep
                        continue
                    
                    # If after 9:30 AM, done for the day
                    else:
                        self.logger.info("✅ Pre-market scanning complete for today")
                        self.logger.info("   Market is now open - switch to realtime scanner")
                        break
                
                # Run scan cycle
                self.run_scan_cycle()
                
                # Update last scan time
                self.last_scan_time = datetime.now()
                
                # Wait for next scan
                self.logger.info(f"⏳ Next scan in {self.SCAN_INTERVAL_SECONDS}s...")
                time.sleep(self.SCAN_INTERVAL_SECONDS)
                
        except KeyboardInterrupt:
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("🛑 Scanner stopped by user")
            self.logger.info("=" * 70)
        
        except Exception as e:
            self.logger.error(f"Fatal error in scanner: {e}", exc_info=True)


def main():
    """Main entry point"""
    scanner = PremarketCatalystScanner()
    scanner.run()


if __name__ == '__main__':
    main()
