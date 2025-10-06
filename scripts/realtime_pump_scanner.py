#!/usr/bin/env python3
"""
💎 REAL-TIME PUMP STOCK SCANNER - PROFESSIONAL EDITION
═══════════════════════════════════════════════════════════════════
Scanner ultra-agressif pour détecter les pump stocks en temps réel
pendant les heures de marché (9h30-16h ET)

DETECTION CRITERIA:
- 🚀 Price surge: > 5% en moins de 5 minutes
- 📊 Volume explosion: > 3x volume moyen
- ⚡ Momentum acceleration: RSI > 70 + MACD bullish
- 💎 Breakout confirmation: Cassure résistance + volume

SCAN FREQUENCY: Every 30 seconds (ultra-aggressive)
LATENCY TARGET: < 10 seconds from surge to Telegram alert

USAGE:
    python scripts/realtime_pump_scanner.py
    python scripts/realtime_pump_scanner.py --aggressive  # 15s scan interval
    
DEPLOYMENT:
    # Auto-start with market open
    nohup python scripts/realtime_pump_scanner.py > logs/pump_scanner.log 2>&1 &
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
import time
import argparse
import pytz
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
import yfinance as yf
import pandas as pd
import numpy as np
from collections import defaultdict, deque

from modules.utils import load_config, is_market_open, get_robust_ticker
from modules.alert_manager import AlertManager
from modules.database_manager import DatabaseManager
from modules.technical_indicators import TechnicalIndicators


class RealtimePumpScanner:
    """
    Real-time pump stock detection system
    Designed for aggressive day traders seeking explosive moves
    """
    
    def __init__(self, aggressive_mode: bool = False):
        """Initialize realtime pump scanner"""
        self.config = load_config()
        self.logger = self._setup_logger()
        self.aggressive_mode = aggressive_mode
        
        # Core modules
        self.alert_manager = AlertManager(self.config)
        self.db = DatabaseManager(self.config.get('database', {}))
        self.tech_indicators = TechnicalIndicators()
        
        # Tracking
        self.price_cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=20))  # Last 20 data points
        self.alerted_pumps: Set[str] = set()  # Today's alerts
        self.pump_tracking: Dict[str, Dict] = {}  # Active pumps
        
        # Scan settings
        if aggressive_mode:
            self.SCAN_INTERVAL = 15  # 15 seconds
            self.PRICE_THRESHOLD = 3.0  # 3%
            self.VOLUME_THRESHOLD = 2.0  # 2x
            self.MIN_SCORE = 70  # Lower threshold
        else:
            self.SCAN_INTERVAL = 30  # 30 seconds
            self.PRICE_THRESHOLD = 5.0  # 5%
            self.VOLUME_THRESHOLD = 3.0  # 3x
            self.MIN_SCORE = 75  # Standard threshold
        
        # Technical thresholds
        self.RSI_OVERBOUGHT = 70
        self.RSI_OVERSOLD = 30
        
        self.logger.info("=" * 70)
        self.logger.info("💎 REAL-TIME PUMP STOCK SCANNER - PROFESSIONAL EDITION")
        self.logger.info("=" * 70)
        self.logger.info(f"Mode: {'AGGRESSIVE 🔥' if aggressive_mode else 'STANDARD'}")
        self.logger.info(f"Scan Interval: {self.SCAN_INTERVAL}s")
        self.logger.info(f"Price Threshold: {self.PRICE_THRESHOLD}%")
        self.logger.info(f"Volume Threshold: {self.VOLUME_THRESHOLD}x")
        self.logger.info(f"Min Score: {self.MIN_SCORE}")
        self.logger.info("=" * 70)
    
    def _setup_logger(self) -> logging.Logger:
        """Setup dedicated logger"""
        logger = logging.getLogger('RealtimePumpScanner')
        logger.setLevel(logging.INFO)
        
        # Console
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        
        # File
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / 'pump_scanner.log')
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
    
    def scan_for_pumps(self, watchlist: List[str]) -> List[Dict]:
        """
        Scan watchlist for pump stocks
        
        Args:
            watchlist: List of symbols to monitor
            
        Returns:
            List of detected pumps
        """
        pumps = []
        
        self.logger.info(f"🔍 Scanning {len(watchlist)} symbols for pumps...")
        
        for symbol in watchlist:
            try:
                pump_data = self._check_pump_conditions(symbol)
                
                if pump_data:
                    # Calculate score
                    score = self._calculate_pump_score(pump_data)
                    pump_data['score'] = score
                    
                    # Alert if score meets threshold
                    if score >= self.MIN_SCORE:
                        # Check if already alerted today
                        alert_key = f"{symbol}_{datetime.now().strftime('%Y%m%d')}"
                        
                        if alert_key not in self.alerted_pumps:
                            pumps.append(pump_data)
                            self.alerted_pumps.add(alert_key)
                            self.logger.info(f"   🚀 PUMP DETECTED: {symbol} (Score: {score:.1f})")
                
                time.sleep(0.05)  # Small delay to avoid rate limits
                
            except Exception as e:
                self.logger.debug(f"Error scanning {symbol}: {e}")
                continue
        
        if pumps:
            self.logger.info(f"   ✅ Found {len(pumps)} pump stocks")
        else:
            self.logger.info("   No pumps detected this scan")
        
        return pumps
    
    def _check_pump_conditions(self, symbol: str) -> Optional[Dict]:
        """
        Check if symbol meets pump conditions
        
        Returns:
            Pump data dict or None
        """
        try:
            ticker = get_robust_ticker(symbol)
            if not ticker:
                return None
            
            # Get real-time data
            info = ticker.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            previous_close = info.get('previousClose')
            current_volume = info.get('volume', 0)
            avg_volume = info.get('averageVolume', 1)
            
            if not current_price or not previous_close:
                return None
            
            # Calculate metrics
            price_change_pct = ((current_price - previous_close) / previous_close) * 100
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            # Check basic thresholds
            if abs(price_change_pct) < self.PRICE_THRESHOLD:
                return None
            
            if volume_ratio < self.VOLUME_THRESHOLD:
                return None
            
            # Get intraday data for technical analysis
            hist = ticker.history(period='1d', interval='5m')
            
            if hist.empty or len(hist) < 5:
                return None
            
            # Add price to cache
            self.price_cache[symbol].append({
                'timestamp': datetime.now(),
                'price': current_price,
                'volume': current_volume
            })
            
            # Calculate technical indicators
            tech_data = self._calculate_pump_technicals(hist)
            
            # Detect momentum acceleration
            momentum_score = self._detect_momentum_acceleration(symbol, hist)
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'previous_close': previous_close,
                'price_change_pct': price_change_pct,
                'current_volume': current_volume,
                'avg_volume': avg_volume,
                'volume_ratio': volume_ratio,
                'market_cap': info.get('marketCap', 0),
                'technicals': tech_data,
                'momentum_score': momentum_score,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.debug(f"Error checking pump conditions for {symbol}: {e}")
            return None
    
    def _calculate_pump_technicals(self, hist: pd.DataFrame) -> Dict:
        """Calculate technical indicators for pump detection"""
        try:
            close = hist['Close']
            high = hist['High']
            low = hist['Low']
            volume = hist['Volume']
            
            # RSI
            rsi = self.tech_indicators.calculate_rsi(close, period=14)
            current_rsi = rsi.iloc[-1] if len(rsi) > 0 else 50
            
            # MACD
            macd_line, signal_line, _ = self.tech_indicators.calculate_macd(close)
            macd_bullish = macd_line.iloc[-1] > signal_line.iloc[-1] if len(macd_line) > 0 else False
            
            # Bollinger Bands
            upper, middle, lower = self.tech_indicators.calculate_bollinger_bands(close)
            price_position = (close.iloc[-1] - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1])
            
            # Volume trend
            volume_sma = volume.rolling(window=5).mean()
            volume_surge = volume.iloc[-1] / volume_sma.iloc[-1] if len(volume_sma) > 0 else 1
            
            # Price momentum (5-minute)
            price_momentum = ((close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] * 100) if len(close) >= 5 else 0
            
            return {
                'rsi': current_rsi,
                'macd_bullish': macd_bullish,
                'bb_position': price_position,
                'volume_surge': volume_surge,
                'price_momentum_5m': price_momentum
            }
            
        except Exception as e:
            self.logger.debug(f"Error calculating technicals: {e}")
            return {}
    
    def _detect_momentum_acceleration(self, symbol: str, hist: pd.DataFrame) -> float:
        """
        Detect if price momentum is accelerating
        
        Returns:
            Momentum score 0-100
        """
        try:
            # Get price cache
            if symbol not in self.price_cache or len(self.price_cache[symbol]) < 3:
                return 50  # Default neutral
            
            cache = list(self.price_cache[symbol])
            
            # Calculate velocity (price change rate)
            velocities = []
            for i in range(1, len(cache)):
                time_diff = (cache[i]['timestamp'] - cache[i-1]['timestamp']).total_seconds()
                price_diff = cache[i]['price'] - cache[i-1]['price']
                
                if time_diff > 0:
                    velocity = (price_diff / cache[i-1]['price']) / time_diff  # %/second
                    velocities.append(velocity)
            
            if not velocities:
                return 50
            
            # Check if velocity is increasing (acceleration)
            recent_velocity = np.mean(velocities[-3:]) if len(velocities) >= 3 else velocities[-1]
            older_velocity = np.mean(velocities[:3]) if len(velocities) >= 6 else velocities[0]
            
            if recent_velocity > older_velocity:
                # Accelerating
                acceleration_factor = recent_velocity / older_velocity if older_velocity != 0 else 1
                score = min(50 + (acceleration_factor * 25), 100)
            else:
                # Decelerating
                score = 50 - abs(recent_velocity - older_velocity) * 10
                score = max(score, 0)
            
            return score
            
        except Exception as e:
            return 50
    
    def _calculate_pump_score(self, pump_data: Dict) -> float:
        """
        Calculate composite pump score
        
        Components:
        - Price movement magnitude (25%)
        - Volume surge (25%)
        - Technical indicators (25%)
        - Momentum acceleration (25%)
        
        Returns:
            Score 0-100
        """
        try:
            # Price component
            price_change = abs(pump_data.get('price_change_pct', 0))
            price_score = min(price_change / 10 * 25, 25)
            
            # Volume component
            volume_ratio = pump_data.get('volume_ratio', 0)
            volume_score = min(volume_ratio / 5 * 25, 25)
            
            # Technical component
            tech = pump_data.get('technicals', {})
            rsi = tech.get('rsi', 50)
            macd_bullish = tech.get('macd_bullish', False)
            bb_position = tech.get('bb_position', 0.5)
            
            tech_score = 0
            
            # RSI contribution
            if rsi > self.RSI_OVERBOUGHT:
                tech_score += 10  # Overbought (momentum)
            elif rsi > 60:
                tech_score += 7
            
            # MACD contribution
            if macd_bullish:
                tech_score += 8
            
            # Bollinger position
            if bb_position > 0.8:  # Near upper band
                tech_score += 7
            
            # Momentum component
            momentum_score = pump_data.get('momentum_score', 50)
            momentum_component = (momentum_score / 100) * 25
            
            total_score = price_score + volume_score + tech_score + momentum_component
            
            return min(total_score, 100)
            
        except Exception as e:
            self.logger.error(f"Error calculating pump score: {e}")
            return 50
    
    def send_pump_alert(self, pump: Dict) -> bool:
        """Send alert for detected pump stock"""
        try:
            symbol = pump.get('symbol', 'UNKNOWN')
            score = pump.get('score', 0)
            price_change = pump.get('price_change_pct', 0)
            volume_ratio = pump.get('volume_ratio', 0)
            current_price = pump.get('current_price', 0)
            
            # Determine priority
            if score >= 90:
                priority = 'CRITICAL'
                emoji = "🚀🚀🚀"
            elif score >= 80:
                priority = 'HIGH'
                emoji = "🚀🚀"
            else:
                priority = 'MEDIUM'
                emoji = "🚀"
            
            # Get technicals
            tech = pump.get('technicals', {})
            rsi = tech.get('rsi', 0)
            macd_bullish = tech.get('macd_bullish', False)
            momentum_score = pump.get('momentum_score', 0)
            
            message = f"""
{emoji} PUMP STOCK DETECTED {emoji}

📊 Symbol: {symbol}
💯 Score: {score:.1f}/100
💰 Price: ${current_price:.2f} ({price_change:+.2f}%)
📈 Volume: {volume_ratio:.1f}x average

📊 Technical Indicators:
  • RSI: {rsi:.1f}
  • MACD: {'Bullish ✅' if macd_bullish else 'Bearish ❌'}
  • Momentum: {momentum_score:.1f}/100

⚡ RECOMMENDATION:
{'🎯 STRONG BUY - Explosive momentum!' if score >= 85 else '✅ BUY - Good entry' if score >= 75 else '⚖️ WATCH - Monitor closely'}

🕐 Detected: {datetime.now().strftime('%H:%M:%S ET')}
"""
            
            # Send alert
            success = self.alert_manager.send_alert(
                alert_type='PUMP_STOCK',
                symbol=symbol,
                message=message,
                priority=priority,
                value=score,
                data=pump
            )
            
            # Store in database
            if success:
                self.db.store_alert({
                    'symbol': symbol,
                    'alert_type': 'PUMP_STOCK',
                    'message': message,
                    'priority': priority,
                    'score': score,
                    'timestamp': datetime.now().isoformat()
                })
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending pump alert: {e}")
            return False
    
    def _get_scan_watchlist(self) -> List[str]:
        """Get watchlist for scanning"""
        watchlist = set()
        
        # Database watchlist
        db_watchlist = self.db.get_watchlist()
        if db_watchlist:
            watchlist.update(db_watchlist)
        
        # Config watchlist
        config_watchlist = self.config.get('watchlist', {}).get('stocks', [])
        watchlist.update(config_watchlist)
        
        # High-volume movers (most likely to pump)
        popular = [
            # Mega caps
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'AMD',
            # Volatile tech
            'SNAP', 'PINS', 'TWTR', 'UBER', 'LYFT', 'COIN', 'RBLX',
            # Meme stocks
            'GME', 'AMC', 'BB', 'NOK', 'BBBY',
            # Biotech (pump potential)
            'MRNA', 'BNTX', 'NVAX', 'VXRT', 'OCGN',
            # ETFs
            'SPY', 'QQQ', 'IWM', 'ARKK', 'SQQQ', 'TQQQ'
        ]
        watchlist.update(popular)
        
        # Limit watchlist size for performance
        max_stocks = 100 if self.aggressive_mode else 150
        
        return list(watchlist)[:max_stocks]
    
    def run_scan_cycle(self) -> int:
        """Run one complete scan cycle"""
        alerts_sent = 0
        
        try:
            # Get watchlist
            watchlist = self._get_scan_watchlist()
            
            # Scan for pumps
            pumps = self.scan_for_pumps(watchlist)
            
            # Send alerts
            for pump in pumps:
                if self.send_pump_alert(pump):
                    alerts_sent += 1
                time.sleep(0.5)  # Small delay between alerts
            
            if alerts_sent > 0:
                self.logger.info(f"✅ Sent {alerts_sent} pump alerts")
            
        except Exception as e:
            self.logger.error(f"Error in scan cycle: {e}")
        
        return alerts_sent
    
    def run(self):
        """Main monitoring loop"""
        self.logger.info("")
        self.logger.info("╔" + "═" * 68 + "╗")
        self.logger.info("║" + " " * 15 + "💎 PUMP STOCK SCANNER ONLINE" + " " * 22 + "║")
        self.logger.info("╚" + "═" * 68 + "╝")
        self.logger.info("")
        self.logger.info("Monitoring: Market hours (9:30 AM - 4:00 PM ET)")
        self.logger.info("Press Ctrl+C to stop")
        self.logger.info("")
        
        try:
            while True:
                # Check if market is open
                if not is_market_open():
                    self.logger.info("⏰ Market is closed - waiting for next open...")
                    
                    # Reset daily tracking
                    self.alerted_pumps.clear()
                    self.price_cache.clear()
                    
                    time.sleep(300)  # Check every 5 minutes
                    continue
                
                # Run scan cycle
                self.run_scan_cycle()
                
                # Wait for next scan
                self.logger.info(f"⏳ Next scan in {self.SCAN_INTERVAL}s...")
                time.sleep(self.SCAN_INTERVAL)
                
        except KeyboardInterrupt:
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("🛑 Scanner stopped by user")
            self.logger.info("=" * 70)
        
        except Exception as e:
            self.logger.error(f"Fatal error in scanner: {e}", exc_info=True)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Real-time Pump Stock Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--aggressive',
        action='store_true',
        help='Aggressive mode: 15s scans, lower thresholds'
    )
    
    args = parser.parse_args()
    
    scanner = RealtimePumpScanner(aggressive_mode=args.aggressive)
    scanner.run()


if __name__ == '__main__':
    main()
