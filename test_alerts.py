"""
🧪 Test Script for Alert System
Tests Telegram, Email, Desktop, and Audio alerts
"""

import os
import sys
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from modules.utils import load_config
from modules.alert_manager import AlertManager

def test_opportunity_alert():
    """Test opportunity alert with smart fallback"""
    print("\n" + "="*60)
    print("🧪 TESTING OPPORTUNITY ALERT SYSTEM")
    print("="*60 + "\n")
    
    # Load config
    config = load_config()
    
    # Initialize alert manager
    alert_manager = AlertManager(config)
    
    # Check enabled channels
    print("📡 Enabled Alert Channels:")
    channels = config.get('alerts', {}).get('channels', {})
    for channel, enabled in channels.items():
        status = "✅ ENABLED" if enabled else "❌ DISABLED"
        print(f"  • {channel.upper()}: {status}")
    
    # Check credentials
    print("\n🔐 Credentials Check:")
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
    gmail_email = os.getenv('GMAIL_EMAIL')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    
    print(f"  • Telegram Bot Token: {'✅ SET' if telegram_token else '❌ NOT SET'}")
    print(f"  • Telegram Chat ID: {'✅ SET' if telegram_chat else '❌ NOT SET'}")
    print(f"  • Gmail Email: {'✅ SET' if gmail_email else '❌ NOT SET'}")
    print(f"  • Gmail App Password: {'✅ SET' if gmail_password else '❌ NOT SET'}")
    
    # Create test opportunity (LOW RISK - highest priority)
    test_opportunity = {
        'ticker': 'AAPL',
        'risk_level': 'low',
        'confidence': 85,
        'reasoning': 'Strong earnings beat with 15% revenue growth. Analyst upgrades from 3 major institutions. New product launch expected next quarter.',
        'explosion_catalysts': [
            'Earnings beat expectations by 20%',
            'New AI chip announcement',
            'Partnership with major automaker',
            'Stock buyback program expansion'
        ],
        'sentiment': 'bullish',
        'news_count': 45,
        'timeframe': '7-30 days'
    }
    
    print("\n🎯 Test Opportunity Details:")
    print(f"  • Symbol: {test_opportunity['ticker']}")
    print(f"  • Risk Level: {test_opportunity['risk_level'].upper()}")
    print(f"  • Confidence: {test_opportunity['confidence']}%")
    print(f"  • Catalysts: {len(test_opportunity['explosion_catalysts'])} major events")
    
    print("\n🚀 Sending alert with smart fallback (Telegram > Email > Desktop/Audio)...")
    print("-" * 60)
    
    # Send alert
    success = alert_manager.send_opportunity_alert(test_opportunity)
    
    print("-" * 60)
    
    if success:
        print("\n✅ ALERT SENT SUCCESSFULLY!")
        print("   Check your Telegram, Email, or Desktop notifications.")
    else:
        print("\n❌ ALERT FAILED TO SEND")
        print("   Please check your configuration and credentials.")
    
    print("\n" + "="*60)
    print("📊 Alert Priority Logic:")
    print("="*60)
    print("1️⃣  Try Telegram first (instant, mobile notification)")
    print("2️⃣  If Telegram fails → try Email (reliable, archived)")
    print("3️⃣  If Email fails → use Desktop notification + Audio")
    print("\n💡 Only LOW RISK opportunities trigger automatic alerts!")
    print("="*60 + "\n")
    
    return success


def test_standard_alert():
    """Test standard alert system"""
    print("\n" + "="*60)
    print("🧪 TESTING STANDARD ALERT SYSTEM")
    print("="*60 + "\n")
    
    config = load_config()
    alert_manager = AlertManager(config)
    
    # Test different priority levels
    test_cases = [
        {
            'priority': 'CRITICAL',
            'symbol': 'TSLA',
            'message': 'Price dropped 15% in 5 minutes! Stop loss triggered.',
            'alert_type': 'STOP_LOSS'
        },
        {
            'priority': 'HIGH',
            'symbol': 'NVDA',
            'message': 'Volume surge detected: 3x average volume. Breakout imminent.',
            'alert_type': 'VOLUME_SURGE'
        },
        {
            'priority': 'MEDIUM',
            'symbol': 'AAPL',
            'message': 'RSI entered oversold territory (RSI: 28). Potential bounce.',
            'alert_type': 'RSI_ALERT'
        }
    ]
    
    results = []
    for test in test_cases:
        print(f"📤 Sending {test['priority']} alert for {test['symbol']}...")
        success = alert_manager.send_alert(
            alert_type=test['alert_type'],
            symbol=test['symbol'],
            message=test['message'],
            priority=test['priority']
        )
        results.append((test['symbol'], test['priority'], success))
        print(f"   {'✅ Success' if success else '❌ Failed'}\n")
    
    print("="*60)
    print("📊 RESULTS SUMMARY:")
    print("="*60)
    for symbol, priority, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {symbol} ({priority})")
    print("="*60 + "\n")
    
    return all(result[2] for result in results)


def main():
    """Run all alert tests"""
    print("\n" + "🚨"*30)
    print(" "*20 + "ALERT SYSTEM TEST SUITE")
    print("🚨"*30 + "\n")
    
    try:
        # Test 1: Opportunity Alert (main feature)
        test1_passed = test_opportunity_alert()
        
        # Wait for user input
        input("\n⏸️  Press ENTER to continue to standard alert tests...")
        
        # Test 2: Standard Alerts
        test2_passed = test_standard_alert()
        
        # Final summary
        print("\n" + "="*60)
        print("🎯 FINAL TEST SUMMARY")
        print("="*60)
        print(f"Opportunity Alert Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
        print(f"Standard Alert Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
        print("="*60)
        
        if test1_passed and test2_passed:
            print("\n🎉 ALL TESTS PASSED! Alert system is fully operational.")
        elif test1_passed:
            print("\n✅ Opportunity alerts working! Standard alerts need configuration.")
        else:
            print("\n⚠️  Some tests failed. Check configuration in config.yaml and .env")
        
        print("\n💡 Configuration Guide:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Telegram bot token and chat ID")
        print("   3. Add your Gmail credentials (app password)")
        print("   4. Enable channels in config.yaml under 'alerts.channels'")
        print("\n📚 See QUICKSTART.md for detailed setup instructions.\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
