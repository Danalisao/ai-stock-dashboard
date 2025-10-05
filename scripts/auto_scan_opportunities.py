#!/usr/bin/env python3
"""
🤖 Automatic Opportunity Scanner & Alert System
Lance des scans automatiques et envoie des alertes pour les pépites détectées

Usage:
    python scripts/auto_scan_opportunities.py              # Scan unique
    python scripts/auto_scan_opportunities.py --schedule   # Scan automatique toutes les 4h
    python scripts/auto_scan_opportunities.py --realtime   # Scan en temps réel (market hours)
"""

import sys
import os
import argparse
import logging
import time
import schedule
from typing import Dict, List, Any
from datetime import datetime, time as dt_time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.utils import load_config, setup_logging, is_market_open
from modules.opportunity_scanner import OpportunityScanner
from modules.alert_manager import AlertManager
from modules.database_manager import DatabaseManager


class AutoScanner:
    """Automatic opportunity scanner with alerts"""
    
    def __init__(self):
        """Initialize auto scanner"""
        # Load configuration
        self.config = load_config()
        
        # Setup logging
        setup_logging(self.config.get('logging', {}))
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.scanner = OpportunityScanner(self.config)
        self.alert_manager = AlertManager(self.config)
        self.db = DatabaseManager(self.config.get('database', {}))
        
        # Scanner settings
        self.min_score = 85.0
        self.min_risk_reward = 2.5
        self.scan_interval_hours = 4  # Scan every 4 hours
        
        # Track already alerted opportunities to avoid duplicates
        self.alerted_opportunities = set()
        
        self.logger.info("AutoScanner initialized")
    
    def run_single_scan(self, alert_on_findings: bool = True) -> List[Dict[str, Any]]:
        """
        Run a single scan and optionally send alerts
        
        Args:
            alert_on_findings: Whether to send alerts for findings
            
        Returns:
            List of opportunities found
        """
        self.logger.info("="*80)
        self.logger.info(f"🔍 Starting opportunity scan - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("="*80)
        
        # Run scan
        opportunities = self.scanner.scan_all_opportunities()
        
        if not opportunities:
            self.logger.info("❌ No opportunities found matching criteria")
            return []
        
        self.logger.info(f"✅ Found {len(opportunities)} opportunities!")
        
        # Save to database
        self._save_opportunities_to_db(opportunities)
        
        # Save to CSV for backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.scanner.save_opportunities_to_csv(
            opportunities, 
            f"opportunities_{timestamp}.csv"
        )
        
        # Send alerts for new opportunities
        if alert_on_findings:
            new_opportunities = self._filter_new_opportunities(opportunities)
            if new_opportunities:
                self.logger.info(f"📢 Sending alerts for {len(new_opportunities)} new opportunities")
                self._send_opportunity_alerts(new_opportunities)
            else:
                self.logger.info("ℹ️ No new opportunities (all already alerted)")
        
        # Print summary
        self._print_summary(opportunities)
        
        return opportunities
    
    def _filter_new_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out opportunities that were already alerted today
        
        Args:
            opportunities: List of all opportunities
            
        Returns:
            List of new opportunities not yet alerted
        """
        new_opportunities = []
        today = datetime.now().date()
        
        for opp in opportunities:
            # Create unique key: symbol + date
            opp_key = f"{opp['symbol']}_{today}"
            
            if opp_key not in self.alerted_opportunities:
                new_opportunities.append(opp)
                self.alerted_opportunities.add(opp_key)
        
        return new_opportunities
    
    def _send_opportunity_alerts(self, opportunities: List[Dict[str, Any]]):
        """
        Send alerts for detected opportunities
        
        Args:
            opportunities: List of opportunities to alert on
        """
        for opp in opportunities:
            # Generate alert message
            message = self.scanner.generate_alert_message(opp)
            
            # Determine priority based on score
            if opp['score'] >= 90:
                priority = 'CRITICAL'
            elif opp['score'] >= 87:
                priority = 'HIGH'
            else:
                priority = 'MEDIUM'
            
            # Send alert through all channels
            success = self.alert_manager.send_alert(
                alert_type='GOLDEN_OPPORTUNITY',
                symbol=opp['symbol'],
                message=message,
                priority=priority,
                value=opp['score'],
                data=opp
            )
            
            if success:
                self.logger.info(f"✅ Alert sent for {opp['symbol']} (Score: {opp['score']:.1f})")
            else:
                self.logger.warning(f"⚠️ Failed to send alert for {opp['symbol']}")
            
            # Small delay between alerts to avoid spam
            time.sleep(2)
    
    def _save_opportunities_to_db(self, opportunities: List[Dict[str, Any]]):
        """Save opportunities to database"""
        try:
            for opp in opportunities:
                self.db.store_monthly_score(
                    symbol=opp['symbol'],
                    score=opp['score'],
                    trend_score=opp['trend_score'],
                    momentum_score=opp['momentum_score'],
                    sentiment_score=opp['sentiment_score'],
                    divergence_score=opp['divergence_score'],
                    volume_score=opp['volume_score'],
                    recommendation=opp['recommendation'],
                    entry_price=opp['entry_price'],
                    stop_loss=opp['stop_loss'],
                    target_price=opp['target_price'],
                    risk_reward=opp['risk_reward']
                )
            self.logger.info(f"💾 Saved {len(opportunities)} opportunities to database")
        except Exception as e:
            self.logger.error(f"Error saving to database: {e}")
    
    def _print_summary(self, opportunities: List[Dict[str, Any]]):
        """Print summary of opportunities"""
        print("\n" + "="*80)
        print("📊 PÉPITES DÉTECTÉES")
        print("="*80)
        
        if not opportunities:
            print("Aucune opportunité trouvée.")
            return
        
        # Sort by score
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        for i, opp in enumerate(opportunities, 1):
            print(f"\n{i}. {opp['symbol']} - {opp['name']}")
            print(f"   Score: {opp['score']:.1f}/100 | {opp['recommendation']} | R/R: 1:{opp['risk_reward']:.2f}")
            print(f"   Prix: ${opp['current_price']:.2f} | Entrée: ${opp['entry_price']:.2f}")
            print(f"   🎯 TP: ${opp['target_price']:.2f} (+{opp['target_pct']:.1f}%) | 🛑 SL: ${opp['stop_loss']:.2f} (-{opp['stop_loss_pct']:.1f}%)")
            print(f"   Volume: {opp['volume_ratio']:.1f}x | Volatilité: {opp['volatility']:.1f}% | Confiance: {opp['confidence']*100:.0f}%")
        
        print("\n" + "="*80)
        print(f"Total: {len(opportunities)} pépites détectées")
        print("="*80 + "\n")
    
    def run_scheduled_scan(self):
        """Run scans on a schedule (every 4 hours during market hours)"""
        self.logger.info("🤖 Starting scheduled auto-scanner")
        self.logger.info(f"Scan interval: Every {self.scan_interval_hours} hours")
        
        # Schedule scans
        schedule.every(self.scan_interval_hours).hours.do(self._scheduled_scan_job)
        
        # Run first scan immediately
        self._scheduled_scan_job()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _scheduled_scan_job(self):
        """Scheduled scan job"""
        try:
            # Only scan during market hours (extended hours: 4am - 8pm ET)
            market_open = is_market_open()
            current_hour = datetime.now().hour
            
            # Scan during extended hours: 9am - 8pm local time
            if 9 <= current_hour <= 20:
                self.logger.info("🟢 Market hours - Running scan")
                self.run_single_scan(alert_on_findings=True)
            else:
                self.logger.info("🔴 Outside market hours - Skipping scan")
        
        except Exception as e:
            self.logger.error(f"Error in scheduled scan: {e}")
    
    def run_realtime_monitoring(self):
        """Run real-time monitoring during market hours"""
        self.logger.info("🚀 Starting real-time monitoring mode")
        self.logger.info("Monitoring during market hours: 9:30am - 4:00pm ET")
        
        while True:
            try:
                now = datetime.now()
                current_time = now.time()
                
                # Market hours: 9:30am - 4:00pm ET (adjust for your timezone)
                market_open_time = dt_time(9, 30)
                market_close_time = dt_time(16, 0)
                
                if market_open_time <= current_time <= market_close_time:
                    self.logger.info("🟢 Market is open - Running scan")
                    self.run_single_scan(alert_on_findings=True)
                    
                    # Wait 15 minutes before next scan (4 scans per hour)
                    self.logger.info("⏳ Waiting 15 minutes before next scan...")
                    time.sleep(15 * 60)
                else:
                    self.logger.info(f"🔴 Market closed - Next scan at {market_open_time}")
                    # Sleep until market opens
                    time.sleep(60 * 60)  # Check every hour
            
            except KeyboardInterrupt:
                self.logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in realtime monitoring: {e}")
                time.sleep(60)  # Wait a minute before retrying


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Automatic Opportunity Scanner & Alert System'
    )
    parser.add_argument(
        '--schedule',
        action='store_true',
        help='Run on schedule (every 4 hours)'
    )
    parser.add_argument(
        '--realtime',
        action='store_true',
        help='Run in real-time during market hours (every 15 min)'
    )
    parser.add_argument(
        '--no-alerts',
        action='store_true',
        help='Run scan without sending alerts'
    )
    parser.add_argument(
        '--min-score',
        type=float,
        default=85.0,
        help='Minimum score for opportunities (default: 85)'
    )
    
    args = parser.parse_args()
    
    # Initialize scanner
    scanner = AutoScanner()
    scanner.min_score = args.min_score
    
    # Run based on mode
    if args.schedule:
        scanner.run_scheduled_scan()
    elif args.realtime:
        scanner.run_realtime_monitoring()
    else:
        # Single scan
        scanner.run_single_scan(alert_on_findings=not args.no_alerts)


if __name__ == '__main__':
    main()
