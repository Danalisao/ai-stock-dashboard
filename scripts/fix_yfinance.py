#!/usr/bin/env python3
"""
Quick test for yfinance connection (using curl_cffi)
"""

import yfinance as yf

# Test connection
print("Testing yfinance connection with curl_cffi...")

try:
    # Test with AAPL - let yfinance handle its own session
    ticker = yf.Ticker("AAPL")
    hist = ticker.history(period="5d")
    
    if not hist.empty:
        print(f"✅ Connection successful!")
        print(f"✅ Fetched {len(hist)} days of data for AAPL")
        print(f"Latest close: ${hist['Close'].iloc[-1]:.2f}")
    else:
        print("⚠️ Connection OK but no data returned")
        print("Try using a different period or check if markets are open")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\n🔧 Solutions:")
    print("1. Vérifiez votre connexion internet")
    print("2. Désactivez temporairement votre antivirus/firewall")
    print("3. Utilisez un VPN si Yahoo Finance est bloqué")
    print("4. Vérifiez les paramètres proxy de Windows")
    print("\nCommande pour tester la connexion:")
    print("  curl https://fc.yahoo.com")
