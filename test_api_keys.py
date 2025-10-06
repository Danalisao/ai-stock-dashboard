"""
🔑 API Keys Test Script
Verify that all API keys are loaded correctly from .env
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("=" * 60)
print("🔑 API KEYS VERIFICATION")
print("=" * 60)
print()

# Define all API keys to check
api_keys = {
    # Google Gemini AI
    'GEMINI_API_KEY': 'Google Gemini (AI Market Analysis)',
    
    # Email Alerts
    'GMAIL_EMAIL': 'Gmail Email (Alerts)',
    'GMAIL_APP_PASSWORD': 'Gmail App Password (Alerts)',
    
    # Telegram Alerts
    'TELEGRAM_BOT_TOKEN': 'Telegram Bot Token (Alerts)',
    'TELEGRAM_CHAT_ID': 'Telegram Chat ID (Alerts)',
    
    # Reddit API
    'REDDIT_CLIENT_ID': 'Reddit Client ID (Social Sentiment)',
    'REDDIT_CLIENT_SECRET': 'Reddit Client Secret (Social Sentiment)',
    'REDDIT_USER_AGENT': 'Reddit User Agent (Social Sentiment)',
    
    # Optional - Not used
    'ALPHA_VANTAGE_API_KEY': 'Alpha Vantage (NOT USED)',
    'NEWS_API_KEY': 'News API (Optional)',
}

# Check each key
results = {
    'configured': [],
    'missing': [],
    'optional': []
}

for key, description in api_keys.items():
    value = os.getenv(key)
    
    if value:
        # Mask the key for security
        if len(value) > 8:
            masked = f"{value[:4]}...{value[-4:]}"
        else:
            masked = "***"
        
        status = "✅"
        results['configured'].append((key, description, masked))
        print(f"{status} {key:25s} - {description:40s} [{masked}]")
    else:
        # Check if it's optional
        if key in ['ALPHA_VANTAGE_API_KEY', 'NEWS_API_KEY', 'REDDIT_USER_AGENT']:
            status = "⚪"
            results['optional'].append((key, description))
            print(f"{status} {key:25s} - {description:40s} [OPTIONAL - Not set]")
        else:
            status = "❌"
            results['missing'].append((key, description))
            print(f"{status} {key:25s} - {description:40s} [MISSING]")

print()
print("=" * 60)
print("📊 SUMMARY")
print("=" * 60)
print(f"✅ Configured: {len(results['configured'])}")
print(f"❌ Missing:    {len(results['missing'])}")
print(f"⚪ Optional:   {len(results['optional'])}")
print()

# Check critical keys for main features
critical_keys = ['GEMINI_API_KEY']
critical_missing = [k for k in critical_keys if not os.getenv(k)]

if critical_missing:
    print("⚠️  CRITICAL KEYS MISSING:")
    for key in critical_missing:
        print(f"   - {key}")
    print()
    print("🔧 ACTION REQUIRED:")
    print("   1. Copy .env.example to .env")
    print("   2. Add your API keys to .env")
    print("   3. Restart the application")
    print()
else:
    print("🎉 ALL CRITICAL KEYS CONFIGURED!")
    print()

# Module functionality status
print("=" * 60)
print("🔧 MODULE FUNCTIONALITY STATUS")
print("=" * 60)
print()

modules_status = []

# Gemini Analyzer
if os.getenv('GEMINI_API_KEY'):
    modules_status.append(("✅", "GeminiAnalyzer", "AI Market Discovery - ACTIVE"))
else:
    modules_status.append(("❌", "GeminiAnalyzer", "AI Market Discovery - DISABLED (fallback mode)"))

# Alert Manager - Email
if os.getenv('GMAIL_EMAIL') and os.getenv('GMAIL_APP_PASSWORD'):
    modules_status.append(("✅", "AlertManager (Email)", "Email Alerts - ACTIVE"))
else:
    modules_status.append(("❌", "AlertManager (Email)", "Email Alerts - DISABLED"))

# Alert Manager - Telegram
if os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('TELEGRAM_CHAT_ID'):
    modules_status.append(("✅", "AlertManager (Telegram)", "Telegram Alerts - ACTIVE"))
else:
    modules_status.append(("❌", "AlertManager (Telegram)", "Telegram Alerts - DISABLED"))

# Social Aggregator - Reddit
if os.getenv('REDDIT_CLIENT_ID') and os.getenv('REDDIT_CLIENT_SECRET'):
    modules_status.append(("✅", "SocialAggregator", "Reddit Sentiment - ACTIVE"))
else:
    modules_status.append(("❌", "SocialAggregator", "Reddit Sentiment - DISABLED"))

for status, module, description in modules_status:
    print(f"{status} {module:30s} - {description}")

print()
print("=" * 60)

# Final recommendation
active_modules = sum(1 for s, _, _ in modules_status if s == "✅")
total_modules = len(modules_status)

print(f"📈 {active_modules}/{total_modules} modules fully operational")
print()

if active_modules == total_modules:
    print("🚀 SYSTEM READY - All features enabled!")
elif os.getenv('GEMINI_API_KEY'):
    print("🟡 SYSTEM PARTIAL - Core AI features enabled")
    print("   Consider configuring alerts and social sentiment for full experience")
else:
    print("⚠️  SYSTEM LIMITED - Configure GEMINI_API_KEY for AI features")

print()
