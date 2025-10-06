#!/usr/bin/env python3
"""
🧪 Quick System Test
Verify all modules load and basic functionality works
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from modules.utils import load_config, setup_logging
        print("✅ utils imported")
        
        from modules.database_manager import DatabaseManager
        print("✅ database_manager imported")
        
        from modules.news_aggregator import NewsAggregator
        print("✅ news_aggregator imported")
        
        from modules.sentiment_analyzer import SentimentAnalyzer
        print("✅ sentiment_analyzer imported")
        
        from modules.social_aggregator import SocialAggregator
        print("✅ social_aggregator imported")
        
        from modules.technical_indicators import TechnicalIndicators
        print("✅ technical_indicators imported")
        
        from modules.monthly_signals import MonthlySignals
        print("✅ monthly_signals imported")
        
        from modules.alert_manager import AlertManager
        print("✅ alert_manager imported")
        
        from modules.portfolio_tracker import PortfolioTracker
        print("✅ portfolio_tracker imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n🧪 Testing configuration...")
    
    try:
        from modules.utils import load_config
        config = load_config()
        
        if not config:
            print("❌ Config is empty")
            return False
        
        # Check key sections
        required_sections = ['watchlist', 'portfolio', 'alerts', 'monthly_signals']
        for section in required_sections:
            if section not in config:
                print(f"⚠️  Missing config section: {section}")
        
        print(f"✅ Config loaded with {len(config)} sections")
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_database():
    """Test database initialization"""
    print("\n🧪 Testing database...")
    
    try:
        from modules.database_manager import DatabaseManager
        
        db = DatabaseManager({'path': ':memory:'})  # Use in-memory DB for testing
        
        # Test basic operations
        db.add_to_watchlist('AAPL')
        watchlist = db.get_watchlist()
        
        if not watchlist or watchlist[0]['symbol'] != 'AAPL':
            print("❌ Watchlist operation failed")
            return False
        
        print("✅ Database operations working")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_data_fetch():
    """Test fetching stock data"""
    print("\n🧪 Testing data fetching...")
    
    try:
        import yfinance as yf
        
        ticker = yf.Ticker('AAPL')
        data = ticker.history(period='5d')
        
        if data.empty:
            print("❌ No data fetched")
            return False
        
        print(f"✅ Fetched {len(data)} days of data")
        return True
        
    except Exception as e:
        print(f"❌ Data fetch failed: {e}")
        return False

def test_technical_indicators():
    """Test technical indicator calculations"""
    print("\n🧪 Testing technical indicators...")
    
    try:
        import yfinance as yf
        from modules.technical_indicators import TechnicalIndicators
        
        # Fetch sample data
        ticker = yf.Ticker('AAPL')
        data = ticker.history(period='3mo')
        
        if data.empty:
            print("⚠️  No data for indicator test")
            return False
        
        # Test indicators
        indicators = TechnicalIndicators()
        
        data = indicators.calculate_adx(data)
        if 'ADX' not in data.columns:
            print("❌ ADX calculation failed")
            return False
        
        data = indicators.calculate_obv(data)
        if 'OBV' not in data.columns:
            print("❌ OBV calculation failed")
            return False
        
        print("✅ Technical indicators working")
        return True
        
    except Exception as e:
        print(f"❌ Technical indicators test failed: {e}")
        return False

def test_sentiment():
    """Test sentiment analysis"""
    print("\n🧪 Testing sentiment analysis...")
    
    try:
        from modules.sentiment_analyzer import SentimentAnalyzer
        
        analyzer = SentimentAnalyzer()
        
        # Test article
        article = {
            'title': 'Apple stock rallies on strong earnings beat',
            'description': 'AAPL surges as revenue exceeds expectations',
            'content': 'Apple reported excellent quarterly results'
        }
        
        result = analyzer.analyze_article(article)
        
        if 'sentiment' not in result:
            print("❌ Sentiment analysis failed")
            return False
        
        sentiment = result['sentiment']
        if sentiment < -1 or sentiment > 1:
            print(f"❌ Invalid sentiment score: {sentiment}")
            return False
        
        print(f"✅ Sentiment analysis working (score: {sentiment:.2f})")
        return True
        
    except Exception as e:
        print(f"❌ Sentiment test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 AI Stock Trading Dashboard - System Test")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
        ("Data Fetching", test_data_fetch),
        ("Technical Indicators", test_technical_indicators),
        ("Sentiment Analysis", test_sentiment),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"❌ {name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("=" * 60)
    print(f"Result: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("🎉 All tests passed! System ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
