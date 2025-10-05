# 📈 AI Stock Trading Dashboard

**Professional Monthly Trading Signals with 0-100 Scoring System**

[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)]()

> **Transform market confusion into decisive trading actions**

A complete trading platform that aggregates **news**, **social sentiment**, and **technical analysis** into a single **0-100 score** with clear **BUY/SELL/HOLD** recommendations.

![Dashboard Screenshot](screenshots/main_dashboard.jpg)

---

## 🎯 What Makes This Special?

### **DECISIVE MONTHLY SIGNALS**
No more analysis paralysis. Get clear recommendations:
- **90-100: STRONG BUY** 🟢🟢🟢 - 5-10% position, HIGH conviction
- **75-89: BUY** 🟢🟢 - 3-5% position, GOOD conviction
- **60-74: MODERATE BUY** 🟢 - 1-3% position
- **40-59: HOLD** ⚖️ - Wait for better setup
- **26-39: MODERATE SELL** 🔴 - Reduce 25-50%
- **11-25: SELL** 🔴🔴 - Reduce 50-75%
- **0-10: STRONG SELL** 🔴🔴🔴 - Exit or short

### **5-COMPONENT WEIGHTED SCORING**
1. **Trend Analysis (30%)** - SMA alignment, ADX strength, monthly direction
2. **Momentum (20%)** - RSI, MACD, Rate of Change
3. **Sentiment (25%)** - News + Social media (Reddit) analysis
4. **Divergence (15%)** - Price vs RSI/MACD/OBV
5. **Volume (10%)** - Volume trend, VWAP, Money Flow Index

### **100% FREE - NO PAID APIS**
- ✅ Stock prices: `yfinance`
- ✅ News: Yahoo Finance RSS + Finviz
- ✅ Social: Reddit API (free tier)
- ✅ Sentiment: VADER + TextBlob
- ✅ Alerts: Desktop, Email, Telegram, Audio

---

## ✨ Core Features

### 🚨 **Monthly Signals Tab**
- **0-100 Score** with detailed component breakdown
- **Entry/Stop/Target prices** with risk/reward ratios
- **Position sizing** recommendations
- **Complete trading plan** generation
- **Score history chart** with threshold lines
- **Confidence levels** (HIGH/MEDIUM/LOW)

### 📰 **News & Sentiment Tab**
- **Multi-source news aggregation** (Yahoo, Finviz, Reddit)
- **VADER + TextBlob + Keyword** sentiment analysis
- **Sentiment trend chart** over time
- **Article-level sentiment scores**
- **Aggregated sentiment** with confidence
- **Sentiment shift detection** (alerts on major changes)

### 💼 **Portfolio Tab**
- **Position tracking** (open/closed)
- **Real-time P&L** (realized/unrealized)
- **Performance metrics**: Sharpe, Sortino, Calmar, Max Drawdown
- **Win rate** and profit factor
- **Trade history** with full details
- **Risk limit checks** (position count, exposure, drawdown)

### 📈 **Technical Analysis Tab**
- **Advanced candlestick charts** with 4 panels
- **15+ Technical indicators**: RSI, MACD, ADX, MFI, OBV, VWAP, etc.
- **Moving averages**: 20, 50, 200-day SMAs
- **Volume analysis** with surge detection
- **Current indicator values** display

### 🔮 **ML Predictions Tab** *(Coming Soon)*
- Machine learning price forecasts
- Feature importance analysis
- Model confidence metrics

### 🔙 **Backtesting Tab** *(Phase 3)*
- Historical strategy simulation
- Walk-forward analysis
- Monte Carlo simulation
- Performance vs benchmark (SPY)

### ⚙️ **Settings Tab**
- **Trading rules** configuration
- **Alert channel** management (Desktop/Email/Telegram/Audio)
- **Test alerts** functionality
- **Database statistics**

---

## 🚀 Quick Start

### **1. Prerequisites**

```bash
Python 3.10+ (tested on 3.13)
macOS / Linux / Windows
```

### **2. Installation**

```bash
# Clone repository
git clone https://github.com/yourusername/ai-stock-dashboard.git
cd ai-stock-dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **3. Configuration** *(Optional)*

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys (optional, for Reddit/Telegram)
nano .env
```

**Required only for Reddit social sentiment:**
- `REDDIT_CLIENT_ID` - Get from https://www.reddit.com/prefs/apps
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT`

**Optional for Telegram alerts:**
- `TELEGRAM_BOT_TOKEN` - Get from @BotFather
- `TELEGRAM_CHAT_ID` - Your chat ID

### **4. Launch Dashboard**

**Option A: Using launch script (Recommended)**
```bash
./run_dashboard.sh
```

**Option B: Manual launch**
```bash
source venv/bin/activate
streamlit run app.py
```

**Dashboard opens at:** http://localhost:8501

---

## 📁 Project Structure

```
ai-stock-dashboard/
├── app.py                      # Main Streamlit dashboard (refactored)
├── stock_dashboard.py          # Original dashboard (legacy)
├── config.yaml                 # System configuration
├── .env                        # API keys (create from .env.example)
├── requirements.txt            # Python dependencies
├── run_dashboard.sh            # Launch script
│
├── modules/                    # Core trading modules
│   ├── __init__.py
│   ├── utils.py                # Financial utilities & calculations
│   ├── database_manager.py    # SQLite operations
│   ├── news_aggregator.py     # Multi-source news scraping
│   ├── sentiment_analyzer.py  # VADER + TextBlob + Keywords
│   ├── social_aggregator.py   # Reddit API integration
│   ├── technical_indicators.py # 15+ advanced indicators
│   ├── monthly_signals.py     # 🎯 CORE: 0-100 scoring algorithm
│   ├── alert_manager.py       # Multi-channel alerts
│   └── portfolio_tracker.py   # Position & performance tracking
│
├── data/                       # Database & cached data
│   └── stock_data.db           # SQLite database
│
├── logs/                       # Application logs
│   └── dashboard.log
│
├── scripts/                    # Automation scripts (Phase 3)
│   ├── daily_update.py         # Scheduled data updates
│   ├── realtime_monitor.py    # Market hours monitoring
│   └── backup_database.py     # Database backups
│
└── screenshots/                # Dashboard screenshots
    ├── main_dashboard.jpg
    ├── monthly_signals.jpg
    └── ...
```

---

## 🔧 Configuration

### **config.yaml**

```yaml
# Watchlist
watchlist:
  stocks: [AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, AMD]
  max_stocks: 20

# Portfolio Settings
portfolio:
  initial_capital: 10000
  position_size_pct: 5      # % of portfolio per stock
  max_positions: 10
  risk_per_trade_pct: 2     # Max loss per trade

# Alert Settings
alerts:
  enabled: true
  channels:
    desktop: true
    email: false            # Configure SMTP in .env
    telegram: false         # Add bot token in .env
    audio: true
  
  conditions:
    price_change_pct: 5     # Alert on 5%+ moves
    volume_surge_multiplier: 2.0
    rsi_oversold: 30
    rsi_overbought: 70

# Monthly Signal Weights
monthly_signals:
  weights:
    trend: 0.30             # 30%
    momentum: 0.20          # 20%
    sentiment: 0.25         # 25%
    divergence: 0.15        # 15%
    volume: 0.10            # 10%
```

---

## 📊 How Monthly Signals Work

### **1. Data Collection**
```
Stock Data (yfinance) → Technical Indicators
News (RSS feeds) → Sentiment Analysis
Reddit Posts → Social Sentiment
```

### **2. Component Scoring (0-100 each)**

**Trend Analysis (30% weight)**
- SMA Alignment: Price > SMA20 > SMA50 > SMA200 = bullish
- ADX Strength: ADX > 50 = very strong trend
- Monthly Direction: Up/down/sideways

**Momentum (20% weight)**
- RSI: 40-60 = healthy, <30 = oversold, >70 = overbought
- MACD: Bullish/bearish crossovers, histogram strength
- ROC: Rate of change momentum

**Sentiment (25% weight)**
- News sentiment: VADER + TextBlob + keyword analysis
- Social sentiment: Reddit post scores and engagement
- Weighted by recency and volume

**Divergence (15% weight)**
- Price vs RSI: Bullish/bearish divergences
- Price vs MACD: Momentum divergences
- OBV trend: Volume confirmation

**Volume (10% weight)**
- Volume trend: Above/below average
- VWAP position: Price relative to VWAP
- MFI: Money flow strength

### **3. Final Score Calculation**
```
Total Score = (Trend × 0.30) + (Momentum × 0.20) + 
              (Sentiment × 0.25) + (Divergence × 0.15) + 
              (Volume × 0.10)
```

### **4. Recommendation Mapping**
```python
if score >= 90: "STRONG BUY 🟢🟢🟢"
elif score >= 75: "BUY 🟢🟢"
elif score >= 60: "MODERATE BUY 🟢"
elif score >= 40: "HOLD ⚖️"
elif score >= 26: "MODERATE SELL 🔴"
elif score >= 11: "SELL 🔴🔴"
else: "STRONG SELL 🔴🔴🔴"
```

### **5. Trade Parameters**
- **Entry price**: Current price or breakout level
- **Stop loss**: 6-8% below entry (tight risk)
- **Target price**: 10-25% above entry (based on conviction)
- **Risk/Reward**: Minimum 1:2 ratio, ideally 1:3+
- **Position size**: 1-10% of portfolio (based on score)

---

## 🎯 Usage Examples

### **Example 1: Check Monthly Signal**

1. Launch dashboard: `./run_dashboard.sh`
2. Select stock from watchlist (or add custom)
3. Click **"🚨 Monthly Signals"** tab
4. Review **0-100 score** and **component breakdown**
5. Check **trading plan** with entry/stop/target prices
6. Review **score history** for trend

### **Example 2: Analyze Sentiment**

1. Go to **"📰 News & Sentiment"** tab
2. Adjust **days of news** slider (1-30 days)
3. Review **aggregate sentiment score** (-1 to +1)
4. Check **sentiment trend chart**
5. Read individual **article sentiments**

### **Example 3: Track Portfolio**

1. Go to **"💼 Portfolio"** tab
2. Add position via **Paper Trading Simulator**
3. View **real-time P&L** (unrealized)
4. Check **performance metrics** (Sharpe, win rate)
5. Review **trade history**

### **Example 4: Set Up Alerts**

1. Go to **"⚙️ Settings"** tab
2. Enable **alert channels** (Desktop/Email/Telegram)
3. Click **"🔔 Test All Alerts"** to verify
4. Alerts trigger on:
   - Score > 85 (CRITICAL)
   - Price moves > 5%
   - Volume surge > 2x
   - Sentiment shift > 0.3
   - RSI oversold/overbought

---

## 🔬 Technical Deep Dive

### **Financial Engineering Principles**

1. **NO MOCK DATA**: All data from real APIs (`yfinance`, RSS, Reddit)
2. **Error handling**: Comprehensive try-catch blocks with logging
3. **Rate limiting**: Respect API limits with RateLimiter class
4. **Data validation**: Check for gaps, outliers, stale prices
5. **Financial rigor**: Industry-standard formulas (Sharpe, MACD, etc.)

### **Key Algorithms**

**Sharpe Ratio:**
```python
sharpe = (returns.mean() * 252) / (returns.std() * sqrt(252))
```

**Monthly Score:**
```python
score = (trend × 0.30) + (momentum × 0.20) + 
        (sentiment × 0.25) + (divergence × 0.15) + 
        (volume × 0.10)
```

**Position Sizing:**
```python
risk_amount = capital × risk_per_trade_pct
shares = risk_amount / (entry_price - stop_loss)
```

### **Database Schema**

**8 Tables:**
- `stock_prices` - OHLCV data
- `news_articles` - Scraped news with sentiment
- `social_mentions` - Reddit posts/comments
- `monthly_scores` - Historical scores
- `alerts` - Alert history
- `watchlist` - User watchlist
- `positions` - Open positions
- `closed_trades` - Trade history

---

## 🚧 Roadmap

### **Phase 3: Backtesting** *(Next)*
- [ ] Backtesting engine module
- [ ] Historical strategy simulation
- [ ] Walk-forward analysis
- [ ] Monte Carlo simulation
- [ ] Performance comparison vs SPY

### **Phase 4: Automation**
- [ ] Daily update script (cron job)
- [ ] Real-time monitoring (market hours)
- [ ] Automated alerts
- [ ] Database backups

### **Phase 5: Advanced Features**
- [ ] ML price predictions integration
- [ ] Options analysis
- [ ] Sector rotation tracking
- [ ] Correlation matrices
- [ ] Economic calendar integration

---

## ⚠️ Important Disclaimers

### **Not Financial Advice**
This software is for **educational and informational purposes only**. It does NOT constitute financial advice, investment recommendations, or an offer to buy/sell securities.

### **Trading Risks**
- **Trading involves substantial risk** of loss
- **Past performance** does not guarantee future results
- **You can lose money** - only trade what you can afford to lose
- **Consult a licensed financial advisor** before making investment decisions

### **Data Accuracy**
- Market data may be **delayed or inaccurate**
- News sentiment is **automated and may have errors**
- Social media sentiment is **noisy and unreliable**
- Always **verify critical information** from official sources

### **No Guarantees**
- **No guaranteed returns** - markets are unpredictable
- **Scores are probabilistic** - not certainties
- **Models can be wrong** - use as ONE input to decisions
- **Technical analysis is subjective** - multiple interpretations exist

**BY USING THIS SOFTWARE, YOU ACKNOWLEDGE THESE RISKS AND AGREE TO USE IT AT YOUR OWN RISK.**

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Contribution Guidelines:**
- Follow existing code style (PEP 8)
- Add docstrings to all functions
- Include error handling with logging
- NO mock data - real APIs only
- Test thoroughly before submitting

---

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

**Built with:**
- [Streamlit](https://streamlit.io/) - Beautiful web apps for ML/data science
- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance API
- [Plotly](https://plotly.com/) - Interactive charts
- [VADER Sentiment](https://github.com/cjhutto/vaderSentiment) - Financial sentiment analysis
- [PRAW](https://praw.readthedocs.io/) - Reddit API wrapper

**Inspired by:**
- Modern Portfolio Theory (Markowitz)
- Technical Analysis of the Financial Markets (Murphy)
- Quantitative Trading (Chan)
- Algorithmic Trading (Chan)

---

## 📞 Support

**Issues?** Open a GitHub issue with:
- Detailed description
- Steps to reproduce
- Error messages/logs
- Python version & OS

**Questions?** Check:
- [ENHANCEMENT_PLAN.md](ENHANCEMENT_PLAN.md) - Feature roadmap
- [TODO.md](TODO.md) - Task tracking
- [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md) - Progress updates

---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐!

---

**Built with ❤️ for traders who want decisive signals, not more confusion.**

*"In God we trust. All others must bring data."* — W. Edwards Deming
