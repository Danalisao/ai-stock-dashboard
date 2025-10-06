#!/usr/bin/env python3
"""
🧪 Test Rapide du Système Intraday
===================================

Test rapide pour vérifier que le système intraday est prêt.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from datetime import datetime
import pytz

from modules.alert_manager import AlertManager
from modules.database_manager import DatabaseManager
from modules.utils import load_config, get_robust_ticker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def print_header(title):
    """Print test section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def test_telegram():
    """Test Telegram notifications."""
    print_header("TEST: Telegram Notifications")
    
    try:
        config = load_config()
        alert_manager = AlertManager(config)
        
        # Send test alert
        alert_manager.send_alert(
            alert_type="test",
            symbol="TEST",
            message="🧪 Test Système Intraday\n\n✅ Le système de trading intraday est configuré correctement !\n\nVous recevrez des alertes comme celle-ci.",
            priority="MEDIUM"
        )
        
        print("✅ PASS | Notification Telegram envoyée")
        print("   Vérifiez votre Telegram !")
        return True
        
    except Exception as e:
        print(f"❌ FAIL | Erreur Telegram: {e}")
        return False


def test_market_data():
    """Test market data fetching."""
    print_header("TEST: Market Data (yfinance)")
    
    try:
        ticker = get_robust_ticker("AAPL")
        if not ticker:
            raise Exception("Impossible de créer ticker")
        
        data = ticker.history(period="1d", interval="1m")
        
        if data.empty:
            raise Exception("Aucune donnée retournée")
        
        current_price = float(data['Close'].iloc[-1])
        print(f"✅ PASS | AAPL prix actuel: ${current_price:.2f}")
        return True
        
    except Exception as e:
        print(f"❌ FAIL | Erreur yfinance: {e}")
        return False


def test_database():
    """Test database connection."""
    print_header("TEST: Database")
    
    try:
        config = load_config()
        db = DatabaseManager(config)
        
        # Test log alert
        db.log_alert(
            symbol="TEST",
            alert_type="TEST",
            priority="LOW",
            message="Test intraday system",
            value=100.0
        )
        
        print("✅ PASS | Database connection OK")
        return True
        
    except Exception as e:
        print(f"❌ FAIL | Erreur database: {e}")
        return False


def test_config():
    """Test configuration."""
    print_header("TEST: Configuration")
    
    try:
        config = load_config()
        
        # Check Telegram config
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
        
        if not telegram_token:
            print("⚠️  WARNING | TELEGRAM_BOT_TOKEN non configuré dans .env")
            return False
        
        if not telegram_chat:
            print("⚠️  WARNING | TELEGRAM_CHAT_ID non configuré dans .env")
            return False
        
        print("✅ PASS | Configuration Telegram OK")
        print(f"   Bot Token: {telegram_token[:20]}...")
        print(f"   Chat ID: {telegram_chat}")
        return True
        
    except Exception as e:
        print(f"❌ FAIL | Erreur configuration: {e}")
        return False


def test_market_hours():
    """Test market hours detection."""
    print_header("TEST: Market Hours Detection")
    
    try:
        et_tz = pytz.timezone('America/New_York')
        now_et = datetime.now(et_tz)
        
        is_weekday = now_et.weekday() < 5
        
        market_open = now_et.replace(hour=9, minute=30, second=0)
        market_close = now_et.replace(hour=16, minute=0, second=0)
        
        is_market_hours = is_weekday and (market_open <= now_et <= market_close)
        
        print(f"   Heure ET actuelle: {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"   Jour semaine: {'Oui ✅' if is_weekday else 'Non ❌ (Weekend)'}")
        print(f"   Heures marché: {'Oui ✅' if is_market_hours else 'Non ❌ (9:30-16:00 ET)'}")
        
        if is_market_hours:
            print("\n   🔥 Le système va scanner activement maintenant !")
        else:
            print("\n   ⏰ Le système attend les heures de marché (9:30-16:00 ET)")
        
        print("\n✅ PASS | Détection heures marché OK")
        return True
        
    except Exception as e:
        print(f"❌ FAIL | Erreur détection heures: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "🧪" * 30)
    print("    TEST RAPIDE - SYSTÈME INTRADAY")
    print("🧪" * 30)
    
    results = []
    
    # Run tests
    results.append(("Configuration", test_config()))
    results.append(("Telegram", test_telegram()))
    results.append(("Market Data", test_market_data()))
    results.append(("Database", test_database()))
    results.append(("Market Hours", test_market_hours()))
    
    # Summary
    print_header("RÉSUMÉ DES TESTS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:12} | {test_name}")
    
    print(f"\n{'=' * 60}")
    print(f"RÉSULTAT: {passed}/{total} tests réussis")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 SYSTÈME PRÊT ! Vous pouvez lancer:")
        print("   python scripts/intraday_trader.py")
        print("\n📱 Vous recevrez des alertes Telegram pendant 9:30-16:00 ET")
    else:
        print("\n⚠️  PROBLÈMES DÉTECTÉS")
        print("   Vérifiez la configuration (.env, config.yaml)")
        print("   Documentation: docs/INTRADAY_TRADING_GUIDE.md")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
