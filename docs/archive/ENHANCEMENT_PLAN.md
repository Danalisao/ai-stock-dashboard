# 🚀 Enhancement Plan - AI Stock Dashboard

## 📋 Document Overview
**Project**: AI Stock Dashboard Evolution  
**Version**: 2.0  
**Date**: October 5, 2025  
**Goal**: Transform into a decisive monthly trading tool with news analysis and alerts  
**Budget**: $0 (100% free APIs and libraries)

---

## 🎯 Vision & Objectives

### Main Goal
Create a **decisive monthly trading assistant** that:
- ✅ Aggregates free financial news with sentiment analysis
- ✅ Provides multi-channel real-time alerts
- ✅ Generates monthly trading signals with confidence scores
- ✅ Tracks portfolio performance
- ✅ Backtests strategies

### Success Metrics
- **Decision Accuracy**: 70%+ profitable signals
- **Alert Response Time**: < 5 minutes from event
- **News Coverage**: 50+ articles/day per stock
- **User Satisfaction**: Clear buy/sell/hold recommendations

---

## 📰 Feature 1: Free News Integration (NO API COSTS)

### 1.1 News Sources (All Free)

#### RSS Feeds
- **Yahoo Finance RSS**: `https://finance.yahoo.com/rss/`
- **Google Finance**: News via search results
- **Investing.com**: Real-time market news
- **MarketWatch**: Free RSS feeds
- **Benzinga**: Free articles (limited)

#### Web Scraping
- **Finviz.com**: News + sentiment indicators
- **SeekingAlpha**: Free articles section
- **TradingView**: Ideas and analysis
- **Reuters Business**: Market news
- **Bloomberg (free)**: Limited articles

#### Social Media
- **Reddit API** (free):
  - r/wallstreetbets
  - r/stocks
  - r/investing
  - r/Daytrading
- **Twitter/X via Nitter**: #stocktwits, $AAPL format
- **StockTwits** (scraping): Community sentiment

### 1.2 News Scraping Architecture

```python
class NewsAggregator:
    - fetch_rss_feeds()          # Parse RSS from multiple sources
    - scrape_finviz_news()       # BeautifulSoup scraping
    - fetch_reddit_sentiment()   # PRAW (Reddit API)
    - scrape_twitter_feed()      # Via nitter.net
    - aggregate_all_news()       # Combine + deduplicate
    - cache_news_sqlite()        # Local database storage
```

### 1.3 Sentiment Analysis (100% Free)

#### Libraries
- **VADER Sentiment**: Financial text optimized
- **TextBlob**: Simple NLP analysis
- **FinBERT** (local): Pre-trained financial sentiment

#### Sentiment Scoring System
```
Score = weighted_average(
    VADER score (40%),
    TextBlob polarity (30%),
    Keyword count (20%),
    Social media mentions (10%)
)

Result: -1.0 (Very Bearish) to +1.0 (Very Bullish)
```

#### Keywords Database
- **Bullish**: breakout, rally, surge, upgrade, beat, growth
- **Bearish**: crash, plunge, downgrade, miss, decline, lawsuit
- **Neutral**: report, announce, trading, market, price

---

## 🚨 Feature 2: Multi-Channel Alert System

### 2.1 Alert Channels (All Free)

#### Desktop Notifications
- **Library**: `plyer`
- **Platform**: Windows, macOS, Linux
- **Trigger**: Instant popup with sound

#### Email Alerts
- **SMTP**: Gmail free tier (500 emails/day)
- **Features**: HTML formatting, attachments
- **Config**: User's Gmail + App Password

#### Telegram Bot
- **API**: Free unlimited messages
- **Setup**: BotFather + Chat ID
- **Features**: Instant mobile push, charts

#### Audio Alerts
- **Library**: `pygame.mixer`
- **Sounds**: Different tones for buy/sell/news
- **Volume**: Configurable in settings

#### SMS (Optional)
- **Twilio Free**: 1 number + credits
- **Alternative**: Email-to-SMS gateway

### 2.2 Alert Conditions for Monthly Trading

#### Price Alerts
```yaml
- RSI_OVERSOLD: RSI < 30 AND Volume > 150% avg
- RSI_OVERBOUGHT: RSI > 70 AND Volume > 150% avg
- BREAKOUT_RESISTANCE: Price > Resistance AND Volume > 200% avg
- BREAKDOWN_SUPPORT: Price < Support AND Volume > 200% avg
- SMA_GOLDEN_CROSS: SMA_50 crosses above SMA_200
- SMA_DEATH_CROSS: SMA_50 crosses below SMA_200
```

#### Technical Alerts
```yaml
- MACD_BULLISH_CROSS: MACD crosses above Signal
- MACD_BEARISH_CROSS: MACD crosses below Signal
- BB_SQUEEZE: BB_width < 20% of 60-day average
- VOLATILITY_SPIKE: ATR > 2x 30-day average
- VOLUME_SURGE: Volume > 3x 20-day average
```

#### News-Based Alerts
```yaml
- SENTIMENT_SHIFT: News sentiment changes > 0.3 in 24h
- MAJOR_NEWS: > 10 articles in 1 hour
- EARNINGS_IMMINENT: Earnings date within 7 days
- ANALYST_UPGRADE: Price target raised > 15%
- INSIDER_BUYING: SEC Form 4 filings detected
```

#### Monthly Signal Alerts
```yaml
- STRONG_BUY_SIGNAL: Monthly score > 80
- STRONG_SELL_SIGNAL: Monthly score < 20
- TREND_REVERSAL: Monthly trend changes direction
- DIVERGENCE_DETECTED: Price vs indicators mismatch
```

### 2.3 Alert Management System

```python
class AlertManager:
    - create_alert(condition, symbol, priority)
    - check_conditions_realtime()
    - send_notification(channel, message, priority)
    - alert_history_log()
    - user_preferences_config()
    - snooze_alert(duration)
    - acknowledge_alert(alert_id)
```

#### Priority Levels
- 🔴 **CRITICAL**: Immediate action needed (sound + all channels)
- 🟠 **HIGH**: Important signal (desktop + Telegram)
- 🟡 **MEDIUM**: Notable event (desktop only)
- 🟢 **LOW**: Informational (log only)

---

## 📊 Feature 3: Monthly Trading Signals

### 3.1 Additional Technical Indicators

#### Trend Indicators
```python
- ADX (Average Directional Index): Trend strength > 25
- Parabolic SAR: Entry/exit points
- Supertrend: Dynamic support/resistance
- Donchian Channels: Breakout detection
```

#### Volume Indicators
```python
- OBV (On-Balance Volume): Accumulation/distribution
- VWAP (Volume Weighted Avg Price): Institutional levels
- MFI (Money Flow Index): Volume-weighted RSI
- CMF (Chaikin Money Flow): Buying/selling pressure
```

#### Momentum Indicators
```python
- Rate of Change (ROC): 30/60/90 day momentum
- Williams %R: Overbought/oversold
- CCI (Commodity Channel Index): Trend changes
- Ultimate Oscillator: Multi-timeframe momentum
```

#### Monthly-Specific Indicators
```python
- Monthly Pivot Points: S1, S2, R1, R2 levels
- Ichimoku Cloud (monthly): Trend direction
- Fibonacci Retracements: Key support/resistance
- Seasonal Patterns: Historical monthly performance
```

### 3.2 Monthly Decision Score Algorithm

```python
def calculate_monthly_score(data, news_sentiment, symbol):
    """
    Calculate 0-100 score for monthly trading decision
    """
    
    # Component 1: Trend Analysis (30%)
    trend_score = analyze_trend(
        sma_alignment,      # 20 > 50 > 200 = bullish
        adx_strength,       # ADX > 25 = strong trend
        price_vs_ma,        # Distance from MAs
        monthly_direction   # Up/down/sideways
    )
    
    # Component 2: Momentum (20%)
    momentum_score = analyze_momentum(
        rsi_level,          # 40-60 ideal, <30 oversold, >70 overbought
        macd_histogram,     # Increasing = bullish
        roc_30d,            # Rate of change
        stochastic          # %K vs %D crossover
    )
    
    # Component 3: News Sentiment (25%)
    sentiment_score = analyze_sentiment(
        news_sentiment,     # -1 to +1
        article_count,      # More articles = more attention
        sentiment_trend,    # Improving or declining
        reddit_mentions     # Social media buzz
    )
    
    # Component 4: Technical Divergences (15%)
    divergence_score = detect_divergences(
        price_vs_rsi,       # Bullish/bearish divergence
        price_vs_macd,      # Hidden divergence
        volume_trend,       # Confirming or not
        obv_direction       # Accumulation vs price
    )
    
    # Component 5: Volume Profile (10%)
    volume_score = analyze_volume(
        volume_trend,       # Increasing = confirmation
        vwap_position,      # Above/below VWAP
        institutional_flow, # Large orders detected
        volume_profile      # Support/resistance zones
    )
    
    # Weighted Final Score
    final_score = (
        trend_score * 0.30 +
        momentum_score * 0.20 +
        sentiment_score * 0.25 +
        divergence_score * 0.15 +
        volume_score * 0.10
    )
    
    return round(final_score, 2)  # 0-100
```

### 3.3 Trading Signals & Recommendations

#### Signal Classification
```
Score 90-100: 🟢🟢🟢 STRONG BUY
  → High conviction, large position size (5-10% portfolio)
  → Entry: Now, Stop Loss: -8%, Target: +20-30%

Score 75-89: 🟢🟢 BUY
  → Good opportunity, medium position (3-5% portfolio)
  → Entry: Now or slight pullback, Stop: -6%, Target: +15-20%

Score 60-74: 🟢 MODERATE BUY
  → Decent setup, small position (1-3% portfolio)
  → Entry: Wait for confirmation, Stop: -5%, Target: +10-15%

Score 40-59: ⚖️ HOLD / NEUTRAL
  → No clear signal, maintain existing positions
  → Action: Wait for better setup or take partial profits

Score 26-39: 🔴 MODERATE SELL
  → Weakening setup, reduce position 25-50%
  → Exit: Partial on strength, preserve capital

Score 11-25: 🔴🔴 SELL
  → Poor outlook, reduce position 50-75%
  → Exit: Most position, keep small tracker

Score 0-10: 🔴🔴🔴 STRONG SELL
  → High risk, exit completely
  → Exit: 100% position, consider short (if experienced)
```

### 3.4 Entry & Exit Strategy

```python
class MonthlyTradingStrategy:
    
    def generate_entry_signals(score, indicators, sentiment):
        """Generate specific entry recommendations"""
        
        if score >= 80:
            return {
                'action': 'BUY',
                'conviction': 'HIGH',
                'entry_price': current_price,
                'entry_timing': 'IMMEDIATE',
                'position_size': '5-10% portfolio',
                'stop_loss': current_price * 0.92,  # -8%
                'take_profit': current_price * 1.25,  # +25%
                'conditions': [
                    'Enter at market open',
                    'Or wait for 2-3% pullback',
                    'Scale in if drops to support'
                ],
                'risk_reward': 3.0  # 3:1 ratio
            }
    
    def generate_exit_signals(score, position, current_pnl):
        """Generate exit recommendations"""
        
        if score < 30 and position > 0:
            return {
                'action': 'SELL',
                'urgency': 'HIGH',
                'exit_percentage': 75,
                'exit_timing': 'Within 1-2 days',
                'reasons': [
                    'Score dropped below 30',
                    'Trend reversal detected',
                    'Negative news sentiment',
                    'Volume declining'
                ]
            }
    
    def trailing_stop_management(entry_price, current_price, high_price):
        """Dynamic trailing stop"""
        
        gain_percent = (current_price - entry_price) / entry_price
        
        if gain_percent > 0.30:  # 30%+ profit
            return high_price * 0.90  # Trail 10% from high
        elif gain_percent > 0.20:  # 20%+ profit
            return high_price * 0.92  # Trail 8% from high
        elif gain_percent > 0.10:  # 10%+ profit
            return high_price * 0.95  # Trail 5% from high
        else:
            return entry_price * 0.92  # Fixed 8% stop loss
```

---

## 💼 Feature 4: Portfolio Tracking

### 4.1 Portfolio Management System

```python
class PortfolioTracker:
    """Track all trading positions and performance"""
    
    def __init__(self):
        self.positions = []
        self.closed_trades = []
        self.cash_balance = 0.0
        self.total_value = 0.0
    
    # Core Functions
    - add_position(symbol, shares, entry_price, entry_date)
    - close_position(symbol, exit_price, exit_date)
    - update_positions_current_prices()
    - calculate_unrealized_pnl()
    - calculate_realized_pnl()
    - get_portfolio_allocation()
    - rebalance_recommendations()
    
    # Analytics
    - calculate_win_rate()
    - calculate_average_gain()
    - calculate_average_loss()
    - calculate_profit_factor()
    - calculate_sharpe_ratio()
    - calculate_max_drawdown()
    - calculate_total_return()
```

### 4.2 Position Tracking Schema (SQLite)

```sql
CREATE TABLE positions (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    shares REAL NOT NULL,
    entry_price REAL NOT NULL,
    entry_date TEXT NOT NULL,
    entry_score INTEGER,
    current_price REAL,
    unrealized_pnl REAL,
    unrealized_pnl_pct REAL,
    stop_loss REAL,
    take_profit REAL,
    status TEXT DEFAULT 'OPEN',
    notes TEXT
);

CREATE TABLE closed_trades (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    shares REAL NOT NULL,
    entry_price REAL NOT NULL,
    entry_date TEXT NOT NULL,
    entry_score INTEGER,
    exit_price REAL NOT NULL,
    exit_date TEXT NOT NULL,
    exit_score INTEGER,
    realized_pnl REAL,
    realized_pnl_pct REAL,
    hold_days INTEGER,
    win_loss TEXT,
    notes TEXT
);

CREATE TABLE portfolio_snapshots (
    id INTEGER PRIMARY KEY,
    snapshot_date TEXT NOT NULL,
    total_value REAL,
    cash_balance REAL,
    invested_value REAL,
    total_return_pct REAL,
    positions_count INTEGER
);
```

### 4.3 Portfolio Dashboard Metrics

```yaml
Real-Time Metrics:
  - Total Portfolio Value
  - Cash Balance
  - Invested Amount
  - Total Return ($)
  - Total Return (%)
  - Day Change ($)
  - Day Change (%)

Position Summary:
  - Number of Open Positions
  - Total Unrealized P&L
  - Best Performing Stock (%)
  - Worst Performing Stock (%)
  - Average Position Size
  - Largest Position (%)

Trade Statistics:
  - Total Trades Closed
  - Win Rate (%)
  - Average Win (%)
  - Average Loss (%)
  - Profit Factor
  - Best Trade ($)
  - Worst Trade ($)

Risk Metrics:
  - Portfolio Beta
  - Sharpe Ratio
  - Maximum Drawdown (%)
  - Current Drawdown (%)
  - Value at Risk (VaR)
  - Diversification Score
```

---

## 🔙 Feature 5: Backtesting Engine

### 5.1 Backtesting System

```python
class StrategyBacktester:
    """Backtest monthly trading strategies"""
    
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}
        self.trade_history = []
    
    def backtest_strategy(
        self,
        symbol,
        start_date,
        end_date,
        entry_rules,
        exit_rules,
        position_sizing='fixed'
    ):
        """
        Run backtest on historical data
        
        Parameters:
        - symbol: Stock ticker
        - start_date: Backtest start
        - end_date: Backtest end
        - entry_rules: Dict of entry conditions
        - exit_rules: Dict of exit conditions
        - position_sizing: 'fixed', 'kelly', 'risk_based'
        """
        
        # Load historical data
        data = fetch_historical_data(symbol, start_date, end_date)
        data = calculate_all_indicators(data)
        data = add_news_sentiment_historical(data)
        
        # Simulate trading
        for date in data.index:
            current_data = data.loc[:date]
            
            # Calculate monthly score
            score = calculate_monthly_score(current_data)
            
            # Check entry signals
            if check_entry_conditions(score, entry_rules):
                self.enter_position(symbol, date, current_data)
            
            # Check exit signals
            if symbol in self.positions:
                if check_exit_conditions(score, exit_rules):
                    self.exit_position(symbol, date, current_data)
        
        # Calculate performance metrics
        return self.generate_backtest_report()
```

### 5.2 Backtest Metrics

```yaml
Performance Metrics:
  - Total Return (%)
  - Annualized Return (%)
  - CAGR (Compound Annual Growth Rate)
  - Total Trades
  - Winning Trades / Losing Trades
  - Win Rate (%)
  - Average Win (%)
  - Average Loss (%)
  - Largest Win (%)
  - Largest Loss (%)
  - Profit Factor

Risk Metrics:
  - Maximum Drawdown (%)
  - Average Drawdown (%)
  - Sharpe Ratio
  - Sortino Ratio
  - Calmar Ratio
  - Standard Deviation
  - Beta vs SPY
  - Alpha vs SPY

Trade Analysis:
  - Average Hold Time (days)
  - Average Win Hold Time
  - Average Loss Hold Time
  - Best Month Return (%)
  - Worst Month Return (%)
  - Consecutive Wins (max)
  - Consecutive Losses (max)

Benchmark Comparison:
  - Return vs Buy & Hold
  - Return vs SPY
  - Risk-Adjusted Return vs Benchmark
```

### 5.3 Strategy Comparison

```python
def compare_strategies(symbol, strategies, start_date, end_date):
    """
    Compare multiple strategies on same stock
    
    Example strategies:
    1. Score > 80 (aggressive)
    2. Score > 75 + positive sentiment (balanced)
    3. Score > 70 + RSI < 40 (value)
    4. Golden Cross + high volume (trend following)
    """
    
    results = []
    for strategy in strategies:
        backtest = run_backtest(symbol, strategy, start_date, end_date)
        results.append(backtest)
    
    # Generate comparison report
    comparison_df = pd.DataFrame({
        'Strategy': [s.name for s in strategies],
        'Return': [r.total_return for r in results],
        'Win Rate': [r.win_rate for r in results],
        'Sharpe': [r.sharpe_ratio for r in results],
        'Max DD': [r.max_drawdown for r in results]
    })
    
    return comparison_df
```

---

## ⚙️ Feature 6: Configuration & Automation

### 6.1 Configuration File (YAML)

```yaml
# config.yaml

# Watchlist
watchlist:
  stocks:
    - AAPL
    - MSFT
    - GOOGL
    - AMZN
    - TSLA
    - NVDA
    - META
    - AMD
    - NFLX
    - DIS
  max_positions: 10
  position_size_pct: 5  # % of portfolio per stock

# Alert Settings
alerts:
  enabled: true
  channels:
    desktop: true
    email: true
    telegram: true
    audio: true
  
  email:
    smtp_server: smtp.gmail.com
    smtp_port: 587
    sender_email: your_email@gmail.com
    sender_password: your_app_password
    recipient_email: your_email@gmail.com
  
  telegram:
    bot_token: YOUR_BOT_TOKEN
    chat_id: YOUR_CHAT_ID
  
  conditions:
    rsi_oversold: 30
    rsi_overbought: 70
    volume_surge_multiplier: 2.0
    sentiment_change_threshold: 0.3
    score_strong_buy: 80
    score_strong_sell: 20

# News Settings
news:
  update_interval_minutes: 60
  sources:
    rss_feeds: true
    finviz: true
    reddit: true
    twitter: false  # Requires setup
  sentiment:
    engine: vader  # vader, textblob, finbert
    cache_hours: 24

# Trading Rules
trading:
  entry_score_min: 75
  exit_score_max: 35
  stop_loss_pct: 8
  take_profit_pct: 25
  trailing_stop: true
  max_hold_days: 90

# Backtesting
backtesting:
  initial_capital: 10000
  commission_per_trade: 0  # Free with Robinhood, etc.
  slippage_pct: 0.1

# Database
database:
  path: ./data/stock_data.db
  backup_enabled: true
  backup_interval_days: 7

# Dashboard
dashboard:
  refresh_interval_seconds: 300  # 5 minutes
  theme: dark
  show_debug: false
```

### 6.2 Automation Scripts

#### Daily Update Script
```python
# daily_update.py
"""
Run this script via cron job every day
Schedule: 6:00 PM EST (after market close)
"""

def daily_update():
    # 1. Update all watchlist stock data
    update_stock_data(watchlist)
    
    # 2. Scrape latest news
    aggregate_news(watchlist)
    
    # 3. Calculate sentiment scores
    analyze_sentiment(watchlist)
    
    # 4. Recalculate monthly scores
    update_monthly_scores(watchlist)
    
    # 5. Check alert conditions
    check_and_send_alerts(watchlist)
    
    # 6. Update portfolio values
    update_portfolio_positions()
    
    # 7. Generate daily report
    generate_daily_report()
    
    # 8. Backup database
    backup_database()
```

#### Real-Time Monitor Script
```python
# realtime_monitor.py
"""
Run this script during market hours
Updates every 5 minutes
"""

def realtime_monitor():
    while market_is_open():
        # Update prices
        update_current_prices(watchlist)
        
        # Check critical alerts (RSI, breakouts, etc.)
        check_critical_alerts(watchlist)
        
        # Check news (hourly)
        if should_update_news():
            fetch_latest_news(watchlist)
        
        # Sleep 5 minutes
        time.sleep(300)
```

#### Crontab Setup (macOS/Linux)
```bash
# Edit crontab
crontab -e

# Add these lines:

# Daily update at 6 PM EST (after market close)
0 18 * * 1-5 cd /path/to/ai-stock-dashboard && python3 daily_update.py

# News update every hour during market hours (9:30 AM - 4:30 PM EST)
30 9-16 * * 1-5 cd /path/to/ai-stock-dashboard && python3 fetch_news.py

# Weekly backup on Sunday at 11 PM
0 23 * * 0 cd /path/to/ai-stock-dashboard && python3 backup_database.py
```

---

## 🗂️ Technical Implementation

### 7.1 New File Structure

```
ai-stock-dashboard/
├── stock_dashboard.py          # Main Streamlit app (enhanced)
├── requirements.txt            # Updated dependencies
├── config.yaml                 # User configuration
├── README.md                   # Updated documentation
├── ENHANCEMENT_PLAN.md         # This file
├── TODO.md                     # Task checklist
│
├── modules/                    # New modules directory
│   ├── __init__.py
│   ├── news_aggregator.py      # News scraping & RSS
│   ├── sentiment_analyzer.py   # NLP & sentiment scoring
│   ├── alert_manager.py        # Multi-channel alerts
│   ├── monthly_signals.py      # Trading signals & scoring
│   ├── portfolio_tracker.py    # Position management
│   ├── backtester.py          # Strategy backtesting
│   ├── database_manager.py     # SQLite operations
│   └── utils.py               # Helper functions
│
├── data/                       # Data storage
│   ├── stock_data.db          # SQLite database
│   ├── news_cache/            # Cached news articles
│   └── backups/               # Database backups
│
├── scripts/                    # Automation scripts
│   ├── daily_update.py        # Daily cron job
│   ├── realtime_monitor.py    # Market hours monitoring
│   ├── fetch_news.py          # News fetching
│   └── backup_database.py     # Backup script
│
├── assets/                     # Static assets
│   ├── sounds/                # Alert sounds
│   │   ├── buy_alert.mp3
│   │   ├── sell_alert.mp3
│   │   └── news_alert.mp3
│   └── icons/                 # App icons
│
├── templates/                  # Email/report templates
│   ├── email_alert.html       # HTML email template
│   ├── daily_report.html      # Daily summary email
│   └── monthly_report.html    # Monthly performance
│
├── tests/                      # Unit tests
│   ├── test_news.py
│   ├── test_sentiment.py
│   ├── test_alerts.py
│   └── test_backtester.py
│
└── docs/                       # Documentation
    ├── USER_GUIDE.md          # User manual
    ├── API_REFERENCE.md       # Code documentation
    └── TRADING_STRATEGIES.md  # Strategy guides
```

### 7.2 Updated Dependencies

```txt
# requirements.txt

# Existing
streamlit>=1.28.0
yfinance>=0.2.18
pandas>=1.5.0
numpy>=1.24.0
plotly>=5.15.0
scikit-learn>=1.3.0

# New - News & Scraping
feedparser>=6.0.10           # RSS feed parsing
beautifulsoup4>=4.12.0       # Web scraping
requests>=2.31.0             # HTTP requests
lxml>=4.9.0                  # XML/HTML parsing
selenium>=4.15.0             # Dynamic scraping (optional)

# New - Sentiment Analysis
vaderSentiment>=3.3.2        # Financial sentiment
textblob>=0.17.0             # NLP analysis
transformers>=4.35.0         # FinBERT (optional, large)
torch>=2.1.0                 # PyTorch for FinBERT (optional)

# New - Alerts & Notifications
plyer>=2.1.0                 # Desktop notifications
python-telegram-bot>=20.7    # Telegram bot API
pygame>=2.5.0                # Audio alerts

# New - Social Media
praw>=7.7.1                  # Reddit API
tweepy>=4.14.0               # Twitter API (optional)

# New - Database & Storage
pyyaml>=6.0.1                # YAML config parsing

# New - Utilities
schedule>=1.2.0              # Task scheduling
python-dotenv>=1.0.0         # Environment variables
tabulate>=0.9.0              # Pretty tables
```

### 7.3 Database Schema

```sql
-- data/stock_data.db

-- Stock data cache
CREATE TABLE stock_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    updated_at TEXT,
    UNIQUE(symbol, date)
);

-- News articles
CREATE TABLE news_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT UNIQUE,
    source TEXT,
    published_date TEXT,
    content TEXT,
    sentiment_score REAL,
    sentiment_label TEXT,
    keywords TEXT,
    fetched_at TEXT
);

-- Social media mentions
CREATE TABLE social_mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    platform TEXT,
    content TEXT,
    author TEXT,
    posted_date TEXT,
    upvotes INTEGER,
    sentiment_score REAL,
    url TEXT,
    fetched_at TEXT
);

-- Monthly scores
CREATE TABLE monthly_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    date TEXT NOT NULL,
    score INTEGER,
    trend_score REAL,
    momentum_score REAL,
    sentiment_score REAL,
    divergence_score REAL,
    volume_score REAL,
    recommendation TEXT,
    calculated_at TEXT,
    UNIQUE(symbol, date)
);

-- Alerts log
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    priority TEXT,
    message TEXT,
    condition_met TEXT,
    channels_sent TEXT,
    created_at TEXT,
    acknowledged BOOLEAN DEFAULT 0,
    acknowledged_at TEXT
);

-- Watchlist
CREATE TABLE watchlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT UNIQUE NOT NULL,
    name TEXT,
    added_date TEXT,
    active BOOLEAN DEFAULT 1,
    notes TEXT
);

-- User settings
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT
);

-- Indexes for performance
CREATE INDEX idx_news_symbol ON news_articles(symbol);
CREATE INDEX idx_news_date ON news_articles(published_date);
CREATE INDEX idx_scores_symbol ON monthly_scores(symbol);
CREATE INDEX idx_scores_date ON monthly_scores(date);
CREATE INDEX idx_alerts_symbol ON alerts(symbol);
CREATE INDEX idx_alerts_date ON alerts(created_at);
```

---

## 📊 Feature 7: Enhanced Dashboard UI

### 7.1 New Streamlit Tabs

```python
# Main navigation
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🚨 Alerts & Signals",      # NEW - Main dashboard
    "📰 News & Sentiment",       # NEW - News aggregator
    "📊 Monthly Analysis",       # NEW - Decisive signals
    "📈 Technical Analysis",     # EXISTING - Enhanced
    "🤖 AI Predictions",         # EXISTING
    "💼 Portfolio",              # NEW - Position tracking
    "🔙 Backtesting"            # NEW - Strategy testing
])
```

### 7.2 Tab 1: Alerts & Signals Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│ 🚨 ACTIVE ALERTS (3)                                        │
├─────────────────────────────────────────────────────────────┤
│ 🔴 AAPL - RSI Oversold (28.5) + Volume Surge 2.3x          │
│    Score: 82 → STRONG BUY | 5 min ago                      │
│    [📧 Email] [📱 Telegram] [🔕 Snooze] [✓ Acknowledge]    │
├─────────────────────────────────────────────────────────────┤
│ 🟢 TSLA - Bullish Breakout Above $250 Resistance           │
│    Score: 78 → BUY | 23 min ago                            │
│    [📧 Email] [📱 Telegram] [✓ Acknowledge]                 │
├─────────────────────────────────────────────────────────────┤
│ 🟡 NVDA - Positive Sentiment Shift (+0.35 in 24h)          │
│    Score: 71 → MODERATE BUY | 1 hour ago                   │
│    [📧 Email] [✓ Acknowledge]                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 📊 WATCHLIST SCORES                                         │
├──────────┬──────┬───────────┬──────────────┬───────────────┤
│ Symbol   │Score │Trend      │Sentiment     │Recommendation │
├──────────┼──────┼───────────┼──────────────┼───────────────┤
│ AAPL 🔼  │  82  │ ↗️ Bullish│ 😊 +0.62     │ 🟢🟢🟢 STRONG BUY│
│ TSLA 🔼  │  78  │ ↗️ Bullish│ 😊 +0.41     │ 🟢🟢 BUY      │
│ NVDA 🔼  │  71  │ ↗️ Bullish│ 😐 +0.18     │ 🟢 MOD BUY    │
│ MSFT ➡️  │  58  │ ➡️ Neutral│ 😐 +0.05     │ ⚖️ HOLD       │
│ GOOGL ➡️ │  52  │ ➡️ Neutral│ 😐 -0.08     │ ⚖️ HOLD       │
│ META 🔽  │  38  │ ↘️ Bearish│ 😟 -0.28     │ 🔴 MOD SELL   │
│ AMD 🔽   │  25  │ ↘️ Bearish│ 😞 -0.55     │ 🔴🔴 SELL     │
└──────────┴──────┴───────────┴──────────────┴───────────────┘

[🔄 Refresh Now] [⚙️ Configure Alerts] [📜 Alert History]
```

### 7.3 Tab 2: News & Sentiment

```
┌─────────────────────────────────────────────────────────────┐
│ 📰 LATEST NEWS (AAPL)                              😊 +0.62 │
├─────────────────────────────────────────────────────────────┤
│ 🟢 "Apple Announces Record Q4 Earnings"                     │
│    Source: Yahoo Finance | 2 hours ago | Sentiment: +0.85  │
│    [Read More] [Full Article]                              │
├─────────────────────────────────────────────────────────────┤
│ 🟢 "iPhone 16 Sales Exceed Expectations"                    │
│    Source: Reuters | 5 hours ago | Sentiment: +0.72        │
│    [Read More] [Full Article]                              │
├─────────────────────────────────────────────────────────────┤
│ 🟡 "Apple Invests $500M in AI Research"                     │
│    Source: TechCrunch | 8 hours ago | Sentiment: +0.45     │
│    [Read More] [Full Article]                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 📊 SENTIMENT TREND (7 Days)                                 │
│                                                             │
│   +1.0 ┤                                         ●          │
│        │                                    ●──●            │
│   +0.5 ┤                          ●──●──●                   │
│        │                     ●──●                           │
│    0.0 ┼─────●──●──●                                        │
│        │                                                    │
│   -0.5 ┤                                                    │
│        │                                                    │
│   -1.0 ┤                                                    │
│        └────────────────────────────────────────────────────│
│         Mon  Tue  Wed  Thu  Fri  Sat  Sun                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 💬 SOCIAL MEDIA BUZZ                                        │
├─────────────────────────────────────────────────────────────┤
│ Reddit (r/stocks): 247 mentions | Sentiment: +0.58         │
│ Top Post: "AAPL earnings beat - time to buy?" (1.2k ↑)     │
├─────────────────────────────────────────────────────────────┤
│ Reddit (r/wallstreetbets): 1,823 mentions | Sent: +0.71    │
│ Top Post: "AAPL calls printing 🚀🚀🚀" (8.3k ↑)              │
└─────────────────────────────────────────────────────────────┘
```

### 7.4 Tab 3: Monthly Analysis (NEW)

```
┌─────────────────────────────────────────────────────────────┐
│ 📊 MONTHLY DECISION ANALYSIS - AAPL                         │
│ Current Score: 82 / 100 → 🟢🟢🟢 STRONG BUY                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ SCORE BREAKDOWN                                             │
├──────────────────────────┬──────┬──────────────────────────┤
│ Component                │Score │ ████████░░ Visual        │
├──────────────────────────┼──────┼──────────────────────────┤
│ 1. Trend Analysis (30%)  │ 88   │ ████████▓░ Excellent     │
│    • SMA Alignment       │  ✓   │ All MAs bullish aligned  │
│    • ADX Strength        │ 31.2 │ Strong trend             │
│    • Monthly Direction   │  ↗️   │ Upward momentum          │
├──────────────────────────┼──────┼──────────────────────────┤
│ 2. Momentum (20%)        │ 75   │ ███████▌░░ Good          │
│    • RSI                 │ 58.3 │ Neutral/bullish          │
│    • MACD                │  +   │ Bullish histogram        │
│    • ROC 30d             │+18.2%│ Strong momentum          │
├──────────────────────────┼──────┼──────────────────────────┤
│ 3. Sentiment (25%)       │ 89   │ ████████▉░ Excellent     │
│    • News sentiment      │+0.62 │ Very positive            │
│    • Article count       │  34  │ High attention           │
│    • Social buzz         │ High │ Reddit/Twitter active    │
├──────────────────────────┼──────┼──────────────────────────┤
│ 4. Divergences (15%)     │ 72   │ ███████▏░░ Good          │
│    • Price vs RSI        │  -   │ No divergence            │
│    • Price vs MACD       │  -   │ No divergence            │
│    • OBV trend           │  ↗️   │ Confirming               │
├──────────────────────────┼──────┼──────────────────────────┤
│ 5. Volume (10%)          │ 85   │ ████████▌░ Very Good     │
│    • Volume trend        │  ↗️   │ Increasing               │
│    • VWAP position       │Above │ Institutional support    │
│    • Surge detected      │ 2.3x │ Strong conviction        │
└──────────────────────────┴──────┴──────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 💡 TRADING RECOMMENDATION                                   │
├─────────────────────────────────────────────────────────────┤
│ Action: BUY                                                 │
│ Conviction: HIGH (82/100)                                   │
│ Position Size: 5-10% of portfolio                          │
│                                                             │
│ Entry Strategy:                                             │
│  • Entry Price: $178.50 (current)                          │
│  • Or wait for pullback to $175 (SMA_20 support)           │
│  • Scale in if drops to $172 (strong support)              │
│                                                             │
│ Risk Management:                                            │
│  • Stop Loss: $164.22 (-8%)                                │
│  • Take Profit Target: $223.13 (+25%)                      │
│  • Risk/Reward Ratio: 3.1:1                                │
│  • Max Hold: 90 days                                       │
│                                                             │
│ Confidence Level: ████████░░ 82%                            │
│                                                             │
│ Key Catalysts:                                              │
│  ✓ Strong earnings beat                                    │
│  ✓ Product cycle momentum                                  │
│  ✓ Positive analyst upgrades                               │
│  ✓ Technical breakout confirmed                            │
│                                                             │
│ [🎯 Add to Watchlist] [💼 Open Position] [📊 Backtest]     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security & Best Practices

### 8.1 API Keys & Credentials

```python
# Use .env file (never commit to git)
# .env
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_char_password
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=123456789

# Load in Python
from dotenv import load_dotenv
import os

load_dotenv()
email = os.getenv('GMAIL_EMAIL')
```

### 8.2 Rate Limiting

```python
class RateLimiter:
    """Prevent API abuse"""
    
    def __init__(self):
        self.requests = {}
    
    def check_rate_limit(self, source, max_requests, time_window):
        """
        source: 'yahoo_finance', 'reddit', etc.
        max_requests: Number of allowed requests
        time_window: Time window in seconds
        """
        # Implementation
        pass
```

### 8.3 Error Handling

```python
import logging

# Setup logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def safe_fetch_data(symbol):
    try:
        data = yf.download(symbol)
        return data
    except Exception as e:
        logging.error(f"Failed to fetch {symbol}: {str(e)}")
        return None
```

---

## 📚 Resources & Documentation

### 9.1 Free Resources

**Learning Materials:**
- Investopedia - Technical analysis guides
- QuantConnect - Algorithm tutorials
- r/algotrading - Community knowledge
- YouTube - Trading strategy videos

**Data Sources:**
- Yahoo Finance - Free stock data
- Alpha Vantage - Free API (limited)
- Quandl - Economic data
- FRED - Federal Reserve data

**Tools:**
- TradingView - Chart analysis (free tier)
- Finviz - Stock screener
- Portfolio Visualizer - Backtesting
- Seeking Alpha - Market analysis

### 9.2 Recommended Reading

**Books:**
- "Technical Analysis of Financial Markets" - John Murphy
- "Algorithmic Trading" - Ernest Chan
- "Evidence-Based Technical Analysis" - David Aronson
- "Trading Systems" - Emilio Tomasini

**Papers:**
- "Common Risk Factors in Stock Returns" - Fama & French
- "The Profitability of Technical Analysis" - Multiple authors
- "Sentiment Analysis in Finance" - Various

---

## 🚀 Future Enhancements (Phase 3)

### Optional Advanced Features

1. **Options Analysis**
   - Implied volatility tracking
   - Options chain visualization
   - Greeks calculator
   - Unusual options activity alerts

2. **Cryptocurrency Support**
   - BTC, ETH, major altcoins
   - Crypto-specific indicators
   - 24/7 monitoring
   - Exchange arbitrage detection

3. **AI Enhancements**
   - GPT integration for news summary
   - Computer vision for chart patterns
   - Reinforcement learning for strategy optimization
   - Ensemble model predictions

4. **Social Trading**
   - Share strategies with community
   - Follow top traders
   - Copy trading functionality
   - Performance leaderboards

5. **Mobile App**
   - React Native app
   - Push notifications
   - Simplified mobile interface
   - Voice commands

6. **Broker Integration**
   - Alpaca API (commission-free)
   - Interactive Brokers
   - TD Ameritrade
   - Robinhood (unofficial)

---

## 📞 Support & Community

### Getting Help
- **GitHub Issues**: Bug reports & feature requests
- **Discussions**: Q&A and general discussion
- **Discord** (optional): Real-time community chat
- **Email**: support@yourdomain.com

### Contributing
Contributions welcome! See CONTRIBUTING.md for guidelines.

---

## 📄 License

MIT License - Free for personal and commercial use

---

**Document Version**: 1.0  
**Last Updated**: October 5, 2025  
**Next Review**: December 2025

---

## 🎯 Success Criteria Checklist

- [ ] News aggregation working from 3+ sources
- [ ] Sentiment analysis accuracy > 75%
- [ ] Alerts delivered within 5 minutes
- [ ] Monthly score calculation complete
- [ ] Portfolio tracking functional
- [ ] Backtesting engine validated
- [ ] User configuration system working
- [ ] Documentation complete
- [ ] All tests passing
- [ ] Demo video created

---

**End of Enhancement Plan Document**
