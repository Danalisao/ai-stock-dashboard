#!/usr/bin/env python3
"""
🌅 Pre-Market Announcement Monitor
Scans for pre-market catalysts and sends alerts before market open

Run this script: 4:00 AM - 9:30 AM ET (before market open)
Recommended: Schedule via cron/Task Scheduler to run every 30 minutes

Usage:
    python scripts/premarket_monitor.py
    python scripts/premarket_monitor.py --watchlist AAPL TSLA MSFT
    python scripts/premarket_monitor.py --continuous --interval 30
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
from datetime import datetime
from typing import List, Optional
import pytz

from modules.utils import load_config, setup_logging
from modules.news_aggregator import NewsAggregator
from modules.alert_manager import AlertManager


class PreMarketMonitor:
    """Monitor pre-market announcements and send alerts"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize pre-market monitor"""
        self.config = load_config(config_path)
        self.logger = setup_logging('premarket_monitor')
        
        # Initialize modules
        self.news_aggregator = NewsAggregator(self.config)
        self.alert_manager = AlertManager(self.config)
        
        # Track sent alerts to avoid duplicates
        self.sent_alerts = set()
        
        self.logger.info("Pre-market monitor initialized")
    
    def is_premarket_hours(self) -> bool:
        """Check if current time is pre-market hours (4:00 AM - 9:30 AM ET)"""
        try:
            et_tz = pytz.timezone('America/New_York')
            now_et = datetime.now(et_tz)
            
            # Pre-market: 4:00 AM - 9:30 AM ET
            premarket_start = now_et.replace(hour=4, minute=0, second=0)
            premarket_end = now_et.replace(hour=9, minute=30, second=0)
            
            return premarket_start <= now_et <= premarket_end
            
        except Exception as e:
            self.logger.error(f"Error checking pre-market hours: {e}")
            # If timezone check fails, allow monitoring to continue
            return True
    
    def scan_announcements(self, watchlist: Optional[List[str]] = None) -> List[dict]:
        """
        Scan for pre-market announcements
        
        Args:
            watchlist: Optional list of symbols to monitor
            
        Returns:
            List of announcements
        """
        self.logger.info("🔍 Scanning for pre-market announcements...")
        
        try:
            # Fetch pre-market announcements
            announcements = self.news_aggregator.fetch_premarket_announcements(watchlist)
            
            if not announcements:
                self.logger.info("✓ No new pre-market announcements found")
                return []
            
            # Filter announcements we haven't alerted on yet
            new_announcements = []
            for announcement in announcements:
                # Create unique key (symbol + title hash)
                alert_key = f"{announcement['symbol']}_{hash(announcement['title'])}"
                
                if alert_key not in self.sent_alerts:
                    new_announcements.append(announcement)
                    self.sent_alerts.add(alert_key)
            
            if new_announcements:
                self.logger.info(f"🎯 Found {len(new_announcements)} new announcements")
                
                # Log summary by priority
                by_priority = {}
                for ann in new_announcements:
                    priority = ann['priority']
                    by_priority[priority] = by_priority.get(priority, 0) + 1
                
                for priority, count in sorted(by_priority.items()):
                    self.logger.info(f"  • {priority}: {count} announcements")
            else:
                self.logger.info("✓ No new announcements (all previously alerted)")
            
            return new_announcements
            
        except Exception as e:
            self.logger.error(f"Error scanning announcements: {e}")
            return []
    
    def send_alerts(self, announcements: List[dict]) -> int:
        """
        Send alerts for announcements
        
        Args:
            announcements: List of announcements to alert on
            
        Returns:
            Number of alerts sent successfully
        """
        if not announcements:
            return 0
        
        success_count = 0
        
        self.logger.info(f"📢 Sending alerts for {len(announcements)} announcements...")
        
        for announcement in announcements:
            try:
                symbol = announcement['symbol']
                priority = announcement['priority']
                catalysts = announcement.get('catalysts', [])
                
                self.logger.info(
                    f"  → {symbol} | {priority} | {', '.join(catalysts[:2])}"
                )
                
                # Send alert
                if self.alert_manager.alert_premarket_announcement(announcement):
                    success_count += 1
                    self.logger.info(f"    ✅ Alert sent for {symbol}")
                else:
                    self.logger.warning(f"    ⚠️ Failed to send alert for {symbol}")
                
                # Small delay between alerts
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Error sending alert for {symbol}: {e}")
                continue
        
        self.logger.info(f"✓ Sent {success_count}/{len(announcements)} alerts successfully")
        return success_count
    
    def run_single_scan(self, watchlist: Optional[List[str]] = None) -> int:
        """
        Run a single scan and send alerts
        
        Args:
            watchlist: Optional watchlist to monitor
            
        Returns:
            Number of alerts sent
        """
        et_tz = pytz.timezone('America/New_York')
        now_et = datetime.now(et_tz)
        
        self.logger.info("=" * 60)
        self.logger.info(f"🌅 PRE-MARKET SCAN | {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        self.logger.info("=" * 60)
        
        if watchlist:
            self.logger.info(f"📋 Monitoring watchlist: {', '.join(watchlist)}")
        else:
            self.logger.info("📋 Monitoring ALL market (no watchlist filter)")
        
        # Check if pre-market hours
        if not self.is_premarket_hours():
            self.logger.warning("⚠️ Not pre-market hours (4:00 AM - 9:30 AM ET)")
            self.logger.info("💡 Running scan anyway (hours check can be disabled)")
        
        # Scan for announcements
        announcements = self.scan_announcements(watchlist)
        
        # Send alerts
        alerts_sent = self.send_alerts(announcements)
        
        self.logger.info("=" * 60)
        
        return alerts_sent
    
    def run_continuous(self, watchlist: Optional[List[str]] = None, 
                      interval_minutes: int = 30):
        """
        Run continuous monitoring with periodic scans
        
        Args:
            watchlist: Optional watchlist to monitor
            interval_minutes: Minutes between scans
        """
        self.logger.info("🔄 Starting continuous pre-market monitoring")
        self.logger.info(f"   Scan interval: {interval_minutes} minutes")
        self.logger.info(f"   Active hours: 4:00 AM - 9:30 AM ET")
        self.logger.info("   Press Ctrl+C to stop")
        self.logger.info("")
        
        try:
            while True:
                # Run scan
                self.run_single_scan(watchlist)
                
                # Wait for next scan
                self.logger.info(f"⏳ Next scan in {interval_minutes} minutes...\n")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            self.logger.info("\n🛑 Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Error in continuous monitoring: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Pre-Market Announcement Monitor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single scan (all market)
  python scripts/premarket_monitor.py
  
  # Single scan (watchlist only)
  python scripts/premarket_monitor.py --watchlist AAPL TSLA MSFT NVDA
  
  # Continuous monitoring (scan every 30 minutes)
  python scripts/premarket_monitor.py --continuous --interval 30
  
  # Continuous monitoring with watchlist
  python scripts/premarket_monitor.py --watchlist AAPL TSLA --continuous --interval 15

Schedule via cron (Linux/Mac):
  # Run every 30 minutes from 4:00 AM - 9:30 AM ET
  */30 4-9 * * 1-5 cd /path/to/project && python scripts/premarket_monitor.py

Schedule via Task Scheduler (Windows):
  1. Open Task Scheduler
  2. Create Basic Task
  3. Trigger: Daily at 4:00 AM
  4. Action: Start program
  5. Program: python
  6. Arguments: C:\\path\\to\\project\\scripts\\premarket_monitor.py
  7. Repeat task every 30 minutes for 5.5 hours
        """
    )
    
    parser.add_argument(
        '--watchlist',
        nargs='+',
        help='Stock symbols to monitor (default: all market)',
        metavar='SYMBOL'
    )
    
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run continuous monitoring (periodic scans)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Scan interval in minutes (default: 30)',
        metavar='MINUTES'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Config file path (default: config.yaml)',
        metavar='PATH'
    )
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = PreMarketMonitor(config_path=args.config)
    
    # Run
    if args.continuous:
        monitor.run_continuous(
            watchlist=args.watchlist,
            interval_minutes=args.interval
        )
    else:
        alerts_sent = monitor.run_single_scan(watchlist=args.watchlist)
        sys.exit(0 if alerts_sent >= 0 else 1)


if __name__ == '__main__':
    main()
