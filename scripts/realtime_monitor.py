#!/usr/bin/env python3
"""
⏱️ Real-Time Monitoring Script
Continuous monitoring during market hours
Run: nohup python scripts/realtime_monitor.py &
"""

import sys
import os
from pathlib import Path
import time
from datetime import datetime
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.utils import load_config, setup_logging, is_market_open, get_next_market_open
from modules.database_manager import DatabaseManager
from modules.alert_manager import AlertManager
import yfinance as yf


class RealtimeMonitor:
    """Real-time market monitoring"""
    
    def __init__(self):
        """Initialize monitor"""
        self.config = load_config()
        setup_logging(self.config.get('logging', {}))
        self.logger = logging.getLogger(__name__)
        
        self.db = DatabaseManager(self.config.get('database', {}))
        self.alert_manager = AlertManager(self.config)
        
        # Monitoring parameters
        self.check_interval = 300  # 5 minutes
        self.price_threshold = 5.0  # % change to alert
        self.volume_threshold = 2.0  # 2x avg volume
        
        # State tracking
        self.last_prices = {}
        self.last_volumes = {}
        
        self.logger.info("Real-Time Monitor initialized")
    
    def run(self):
        """Main monitoring loop"""
        self.logger.info("=" * 60)
        self.logger.info("🔴 LIVE: Real-Time Monitor Started")
        self.logger.info("=" * 60)
        
        while True:
            try:
                # Check if market is open
                if not is_market_open():
                    next_open = get_next_market_open()
                    self.logger.info(f"⏸️ Market closed. Next open: {next_open}")
                    time.sleep(3600)  # Sleep 1 hour when market closed
                    continue
                
                # Get watchlist
                watchlist = self._get_watchlist()
                
                # Monitor each stock
                self.logger.info(f"🔍 Monitoring {len(watchlist)} stocks...")
                for symbol in watchlist:
                    try:
                        self._monitor_stock(symbol)
                    except Exception as e:
                        self.logger.error(f"Error monitoring {symbol}: {e}")
                        continue
                
                # Wait before next check
                self.logger.info(f"⏳ Next check in {self.check_interval} seconds...")
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                self.logger.info("\n⏹️ Monitor stopped by user")
                break
            
            except Exception as e:
                self.logger.error(f"Monitor error: {e}", exc_info=True)
                time.sleep(60)  # Wait 1 minute on error
    
    def _get_watchlist(self):
        """Get stocks to monitor"""
        db_watchlist = self.db.get_watchlist()
        if db_watchlist:
            return [item['symbol'] for item in db_watchlist]
        return self.config.get('watchlist', {}).get('stocks', ['AAPL'])
    
    def _monitor_stock(self, symbol: str):
        """Monitor single stock for alerts"""
        try:
            # Fetch current data
            ticker = yf.Ticker(symbol)
            
            # Get latest quote
            info = ticker.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if not current_price:
                return
            
            prev_close = info.get('previousClose')
            volume = info.get('volume', 0)
            avg_volume = info.get('averageVolume', volume)
            
            # Check price change
            if prev_close and prev_close > 0:
                price_change_pct = ((current_price - prev_close) / prev_close) * 100
                
                if abs(price_change_pct) >= self.price_threshold:
                    self.alert_manager.alert_price_move(
                        symbol=symbol,
                        current_price=current_price,
                        change_pct=price_change_pct
                    )
                    self.logger.info(f"  🚨 {symbol}: Price moved {price_change_pct:+.2f}%")
            
            # Check volume surge
            if avg_volume > 0:
                volume_ratio = volume / avg_volume
                
                if volume_ratio >= self.volume_threshold:
                    self.alert_manager.alert_volume_surge(
                        symbol=symbol,
                        current_volume=volume,
                        avg_volume=avg_volume,
                        surge_factor=volume_ratio
                    )
                    self.logger.info(f"  🚨 {symbol}: Volume surge {volume_ratio:.1f}x")
            
            # Check RSI (requires historical data)
            hist = ticker.history(period='1mo')
            if not hist.empty and len(hist) >= 14:
                # Calculate RSI
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1]
                
                # Alert on extreme RSI
                if current_rsi <= 30:
                    self.alert_manager.alert_rsi_level(
                        symbol=symbol,
                        rsi=current_rsi,
                        level="oversold"
                    )
                    self.logger.info(f"  🚨 {symbol}: RSI oversold ({current_rsi:.1f})")
                
                elif current_rsi >= 70:
                    self.alert_manager.alert_rsi_level(
                        symbol=symbol,
                        rsi=current_rsi,
                        level="overbought"
                    )
                    self.logger.info(f"  🚨 {symbol}: RSI overbought ({current_rsi:.1f})")
            
            # Update state
            self.last_prices[symbol] = current_price
            self.last_volumes[symbol] = volume
            
        except Exception as e:
            self.logger.error(f"Error monitoring {symbol}: {e}")


def main():
    """Main entry point"""
    monitor = RealtimeMonitor()
    monitor.run()


if __name__ == '__main__':
    main()
