#!/usr/bin/env python3
"""
🧪 PROFESSIONAL TRADING SYSTEM - COMPLETE TEST SUITE
═══════════════════════════════════════════════════════════════════
Test complet de tous les composants du système professionnel

TESTS:
- ✅ Configuration .env
- ✅ Alertes (Telegram, Email, Desktop)
- ✅ Database connection
- ✅ API data fetch (yfinance)
- ✅ Gemini AI (si configuré)
- ✅ Technical indicators
- ✅ Scanners (premarket, pump)

USAGE:
    python scripts/test_trading_system.py
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
from datetime import datetime
from typing import Dict, List, Tuple
import yfinance as yf

from modules.utils import load_config, get_robust_ticker
from modules.alert_manager import AlertManager
from modules.database_manager import DatabaseManager
from modules.gemini_analyzer import GeminiAnalyzer
from modules.technical_indicators import TechnicalIndicators
from modules.news_aggregator import NewsAggregator


class TradingSystemTester:
    """Comprehensive testing suite for trading system"""
    
    def __init__(self):
        """Initialize tester"""
        self.config = load_config()
        self.results: List[Tuple[str, bool, str]] = []
        
        print("")
        print("═" * 70)
        print("🧪 PROFESSIONAL TRADING SYSTEM - TEST SUITE")
        print("═" * 70)
        print("")
    
    def run_all_tests(self) -> bool:
        """Run all tests and return overall success"""
        
        # Configuration tests
        print("📋 TESTING CONFIGURATION")
        print("-" * 70)
        self.test_env_file()
        self.test_config_yaml()
        print("")
        
        # Alert tests
        print("🔔 TESTING ALERT SYSTEM")
        print("-" * 70)
        self.test_telegram()
        self.test_email()
        self.test_desktop()
        print("")
        
        # Database tests
        print("💾 TESTING DATABASE")
        print("-" * 70)
        self.test_database()
        print("")
        
        # API tests
        print("📊 TESTING DATA SOURCES")
        print("-" * 70)
        self.test_yfinance()
        self.test_news_aggregator()
        print("")
        
        # AI tests
        print("🤖 TESTING AI MODULES")
        print("-" * 70)
        self.test_gemini()
        print("")
        
        # Technical analysis tests
        print("📈 TESTING TECHNICAL INDICATORS")
        print("-" * 70)
        self.test_technical_indicators()
        print("")
        
        # Display results
        self._display_results()
        
        # Return overall success
        all_passed = all(result[1] for result in self.results)
        return all_passed
    
    def test_env_file(self):
        """Test .env file configuration"""
        test_name = ".env file exists"
        
        try:
            env_path = project_root / '.env'
            
            if env_path.exists():
                # Check critical variables
                telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
                telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
                
                if telegram_token and telegram_chat:
                    self.results.append((test_name, True, "Telegram configured ✅"))
                else:
                    self.results.append((test_name, False, "Telegram not configured ⚠️"))
            else:
                self.results.append((test_name, False, ".env file missing ❌"))
                
        except Exception as e:
            self.results.append((test_name, False, f"Error: {e}"))
    
    def test_config_yaml(self):
        """Test config.yaml"""
        test_name = "config.yaml"
        
        try:
            if self.config:
                watchlist = self.config.get('watchlist', {}).get('stocks', [])
                
                if len(watchlist) > 0:
                    self.results.append((test_name, True, f"{len(watchlist)} stocks in watchlist ✅"))
                else:
                    self.results.append((test_name, False, "Empty watchlist ⚠️"))
            else:
                self.results.append((test_name, False, "Config failed to load ❌"))
                
        except Exception as e:
            self.results.append((test_name, False, f"Error: {e}"))
    
    def test_telegram(self):
        """Test Telegram alerts"""
        test_name = "Telegram alerts"
        
        try:
            alert_manager = AlertManager(self.config)
            
            # Check if Telegram is configured
            if alert_manager.telegram_bot:
                # Test sending message
                result = alert_manager._send_telegram("🧪 Test from Trading System - Ignore")
                
                if result:
                    self.results.append((test_name, True, "Telegram working ✅"))
                else:
                    self.results.append((test_name, False, "Failed to send ❌"))
            else:
                self.results.append((test_name, False, "Not configured ⚠️"))
                
        except Exception as e:
            self.results.append((test_name, False, f"Error: {e}"))
    
    def test_email(self):
        """Test email alerts"""
        test_name = "Email alerts"
        
        try:
            alert_manager = AlertManager(self.config)
            
            gmail_email = os.getenv('GMAIL_EMAIL')
            gmail_password = os.getenv('GMAIL_APP_PASSWORD')
            
            if gmail_email and gmail_password:
                # Don't actually send test email (avoid spam)
                self.results.append((test_name, True, "Email configured ✅"))
            else:
                self.results.append((test_name, False, "Not configured ⚠️"))
                
        except Exception as e:
            self.results.append((test_name, False, f"Error: {e}"))
    
    def test_desktop(self):
        """Test desktop notifications"""
        test_name = "Desktop notifications"
        
        try:
            from plyer import notification
            
            # Test notification (will appear on screen)
            notification.notify(
                title="🧪 Trading System Test",
                message="Desktop notifications working!",
                app_name="Stock Dashboard",
                timeout=3
            )
            
            self.results.append((test_name, True, "Desktop working ✅"))
            
        except Exception as e:
            self.results.append((test_name, False, f"Error: {e}"))
    
    def test_database(self):
        """Test database connection"""
        test_name = "Database connection"
        
        try:
            db = DatabaseManager(self.config.get('database', {}))
            
            # Try to get watchlist
            watchlist = db.get_watchlist()
            
            self.results.append((test_name, True, "Database working ✅"))
            
        except Exception as e:
            self.results.append((test_name, False, f"Error: {e}"))
    
    def test_yfinance(self):
        """Test yfinance data fetching"""
        test_name = "yfinance API"
        
        try:
            # Test fetching AAPL data
            ticker = get_robust_ticker('AAPL')
            
            if ticker:
                info = ticker.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                
                if current_price:
                    self.results.append((test_name, True, f"Data fetch OK (AAPL: ${current_price:.2f}) ✅"))
                else:
                    self.results.append((test_name, False, "No price data ⚠️"))
            else:
                self.results.append((test_name, False, "Ticker failed ❌"))
                
        except Exception as e:
            self.results.append((test_name, False, f"Error: {e}"))
    
    def test_news_aggregator(self):
        """Test news fetching"""
        test_name = "News aggregator"
        
        try:
            news_aggregator = NewsAggregator(self.config)
            
            # Fetch news
            articles = news_aggregator.fetch_market_news(max_articles=10)
            
            if articles and len(articles) > 0:
                self.results.append((test_name, True, f"{len(articles)} articles fetched ✅"))
            else:
                self.results.append((test_name, False, "No articles fetched ⚠️"))
                
        except Exception as e:
            self.results.append((test_name, False, f"Error: {e}"))
    
    def test_gemini(self):
        """Test Gemini AI"""
        test_name = "Gemini AI"
        
        try:
            gemini_analyzer = GeminiAnalyzer(self.config)
            
            if gemini_analyzer.enabled:
                self.results.append((test_name, True, "Gemini configured ✅"))
            else:
                self.results.append((test_name, False, "Not configured (optional) ⚠️"))
                
        except Exception as e:
            self.results.append((test_name, False, f"Error: {e}"))
    
    def test_technical_indicators(self):
        """Test technical indicators calculation"""
        test_name = "Technical indicators"
        
        try:
            tech = TechnicalIndicators()
            
            # Get AAPL data
            ticker = yf.Ticker('AAPL')
            hist = ticker.history(period='1mo')
            
            if not hist.empty:
                close = hist['Close']
                
                # Calculate indicators
                rsi = tech.calculate_rsi(close)
                macd_line, signal_line, histogram = tech.calculate_macd(close)
                upper, middle, lower = tech.calculate_bollinger_bands(close)
                
                if len(rsi) > 0 and len(macd_line) > 0:
                    self.results.append((test_name, True, "Calculations OK ✅"))
                else:
                    self.results.append((test_name, False, "Empty results ❌"))
            else:
                self.results.append((test_name, False, "No historical data ❌"))
                
        except Exception as e:
            self.results.append((test_name, False, f"Error: {e}"))
    
    def _display_results(self):
        """Display test results"""
        print("")
        print("═" * 70)
        print("📊 TEST RESULTS")
        print("═" * 70)
        print("")
        
        passed = 0
        failed = 0
        
        for test_name, success, message in self.results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status:10} | {test_name:30} | {message}")
            
            if success:
                passed += 1
            else:
                failed += 1
        
        print("")
        print("─" * 70)
        print(f"  Total: {passed + failed} tests | Passed: {passed} | Failed: {failed}")
        print("─" * 70)
        print("")
        
        if failed == 0:
            print("✅ ALL TESTS PASSED - System ready for trading!")
        else:
            print(f"⚠️ {failed} TESTS FAILED - Please fix configuration")
            print("")
            print("Common fixes:")
            print("  • Telegram not configured → Check .env file")
            print("  • Email not configured → Add GMAIL_EMAIL and GMAIL_APP_PASSWORD")
            print("  • Gemini not configured → Optional, add GEMINI_API_KEY")
            print("  • yfinance issues → Check internet connection")
        
        print("")


def main():
    """Main entry point"""
    tester = TradingSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("🚀 Ready to launch trading system!")
        print("")
        print("Next steps:")
        print("  1. python scripts/launch_trading_system.py --all")
        print("  2. Check Telegram for test alert")
        print("  3. Open Control Center: streamlit run scripts/control_center.py")
        print("")
        sys.exit(0)
    else:
        print("❌ Please fix errors before launching")
        sys.exit(1)


if __name__ == '__main__':
    main()
