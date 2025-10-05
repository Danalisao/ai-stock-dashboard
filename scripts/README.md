# 🤖 Automation Scripts

This directory contains automation scripts for the AI Stock Trading Dashboard.

## 📂 Available Scripts

### 1. **daily_update.py** - Daily Data Updates
Automated daily updates for all watchlist stocks.

**What it does:**
- Fetches latest price data (OHLCV)
- Aggregates news articles
- Analyzes sentiment (news + social)
- Calculates monthly signals (0-100 scores)
- Sends alerts for significant events
- Cleans up old data

**Run manually:**
```bash
python scripts/daily_update.py
```

**Schedule with cron (6 PM EST, Mon-Fri):**
```bash
crontab -e
# Add this line:
0 18 * * 1-5 cd /path/to/ai-stock-dashboard && source venv/bin/activate && python scripts/daily_update.py >> logs/daily_update.log 2>&1
```

**Features:**
- ✅ Processes all watchlist stocks
- ✅ Saves data to database
- ✅ Generates summary report
- ✅ Sends critical alerts
- ✅ Logs all operations

---

### 2. **realtime_monitor.py** - Live Market Monitoring
Continuous monitoring during market hours (9:30 AM - 4:00 PM EST).

**What it does:**
- Monitors prices every 5 minutes
- Detects price movements (>5% change)
- Detects volume surges (>2x average)
- Alerts on RSI extremes (oversold/overbought)
- Auto-pauses when market closed

**Run as background process:**
```bash
nohup python scripts/realtime_monitor.py >> logs/monitor.log 2>&1 &
```

**Check if running:**
```bash
ps aux | grep realtime_monitor
```

**Stop monitoring:**
```bash
pkill -f realtime_monitor.py
```

**Features:**
- 🔴 Live monitoring (5-minute intervals)
- ⏸️ Auto-pause when market closed
- 🚨 Real-time alerts (price, volume, RSI)
- 📊 State tracking (previous prices/volumes)
- ♾️ Runs continuously until stopped

---

### 3. **backup_database.py** - Database Backup
Automated database backup and cleanup.

**What it does:**
- Creates timestamped database backup
- Verifies backup integrity
- Keeps last 30 backups (configurable)
- Removes old backups automatically
- Displays backup summary

**Run manually:**
```bash
python scripts/backup_database.py
```

**Schedule with cron (2 AM daily):**
```bash
crontab -e
# Add this line:
0 2 * * * cd /path/to/ai-stock-dashboard && source venv/bin/activate && python scripts/backup_database.py >> logs/backup.log 2>&1
```

**Backup location:**
```
data/backups/
├── stock_data_backup_20251005_020000.db
├── stock_data_backup_20251004_020000.db
└── ... (keeps last 30)
```

---

### 4. **train_ml_models.py** - ML Model Training 🤖

Automated training of machine learning prediction models.

**What it does:**

- Trains ensemble ML models (Random Forest, Gradient Boosting, Ridge, SVR)
- Engineers 60+ features from historical data
- Saves trained models to disk for fast predictions
- Validates model performance with cross-validation
- Optional: Runs accuracy backtests
- Generates detailed training summary reports

**Run manually (train all watchlist stocks):**

```bash
python scripts/train_ml_models.py
```

**Train specific symbols:**

```bash
python scripts/train_ml_models.py --symbols AAPL MSFT GOOGL NVDA
```

**Custom forecast horizon:**

```bash
python scripts/train_ml_models.py --horizon 60  # 60-day forecast
```

**Force retrain (even if models are recent):**

```bash
python scripts/train_ml_models.py --force
```

**Include accuracy backtest:**

```bash
python scripts/train_ml_models.py --backtest
```

**Combined example:**

```bash
python scripts/train_ml_models.py --symbols AAPL TSLA --horizon 30 --force --backtest
```

**Schedule with cron (weekly, Sunday 3 AM):**

```bash
crontab -e
# Add this line:
0 3 * * 0 cd /path/to/ai-stock-dashboard && source venv/bin/activate && python scripts/train_ml_models.py --force >> logs/ml_training.log 2>&1
```

**Output:**

- Trained models saved to: `models/{SYMBOL}_models.pkl`
- Training summary: `logs/ml_training_summary_YYYYMMDD_HHMMSS.txt`

**Features:**

- 🎯 Trains ensemble of 4 ML models per stock
- 📊 60+ engineered features (price momentum, technical indicators, volume, etc.)
- ✅ Time-series cross-validation for robustness
- 💾 Model persistence (saves/loads from disk)
- 📈 Optional accuracy backtesting
- 📄 Detailed summary reports
- ⏭️ Smart skipping (only retrains if models are >7 days old)

**Model Architecture:**

- **Random Forest** (35% weight): Non-linear patterns
- **Gradient Boosting** (30% weight): Sequential error correction
- **Ridge Regression** (20% weight): Linear trends with regularization
- **SVR** (15% weight): Complex pattern recognition

```

**Features:**
- 💾 Automatic timestamped backups
- ✅ Integrity verification (SQLite PRAGMA)
- 🧹 Auto-cleanup (keeps 30 most recent)
- 📊 Size tracking and reporting
- 🔐 Preserves file permissions

---

## 🚀 Complete Automation Setup

### **1. Create Log Directory**
```bash
mkdir -p logs
```

### **2. Make Scripts Executable**
```bash
chmod +x scripts/*.py
```

### **3. Setup Cron Jobs**
```bash
crontab -e
```

Add these lines:
```bash
# Daily update (6 PM EST, Mon-Fri)
0 18 * * 1-5 cd /path/to/ai-stock-dashboard && source venv/bin/activate && python scripts/daily_update.py >> logs/daily_update.log 2>&1

# Database backup (2 AM daily)
0 2 * * * cd /path/to/ai-stock-dashboard && source venv/bin/activate && python scripts/backup_database.py >> logs/backup.log 2>&1
```

**Replace `/path/to/ai-stock-dashboard` with your actual path!**

### **4. Start Real-Time Monitor**
```bash
# Activate environment
source venv/bin/activate

# Start monitoring in background
nohup python scripts/realtime_monitor.py >> logs/monitor.log 2>&1 &

# Save process ID for later
echo $! > logs/monitor.pid
```

### **5. Verify Everything is Running**
```bash
# Check cron jobs
crontab -l

# Check monitor process
ps aux | grep realtime_monitor

# Check recent logs
tail -f logs/daily_update.log
tail -f logs/monitor.log
tail -f logs/backup.log
```

---

## 📅 Automation Schedule

| Time | Script | Frequency | Purpose |
|------|--------|-----------|---------|
| **6:00 PM EST** | daily_update.py | Mon-Fri | Daily data refresh |
| **2:00 AM EST** | backup_database.py | Daily | Database backup |
| **9:30 AM - 4:00 PM EST** | realtime_monitor.py | Continuous | Live monitoring |

---

## 🔔 Alert Channels

Scripts can send alerts via multiple channels (configure in `config.yaml`):

- **Desktop Notifications** ✅ (default)
- **Email** 📧 (configure SMTP in config)
- **Telegram** 💬 (add bot token in config)
- **Audio** 🔊 (pygame alerts)

**Configure in `config.yaml`:**
```yaml
alerts:
  enabled: true
  channels:
    desktop: true
    email: false  # Set to true and add SMTP details
    telegram: false  # Set to true and add bot token
    audio: true
```

---

## 📊 Monitoring Logs

### **View Live Logs**
```bash
# Daily update log
tail -f logs/daily_update.log

# Real-time monitor log
tail -f logs/monitor.log

# Backup log
tail -f logs/backup.log

# Main application log
tail -f logs/app.log
```

### **Log Rotation**
Logs automatically rotate when they reach 10 MB (keeps 5 backups).

**Location:** `logs/`
```
logs/
├── app.log           # Main application
├── app.log.1         # Rotated logs
├── daily_update.log  # Daily updates
├── monitor.log       # Real-time monitoring
└── backup.log        # Database backups
```

---

## 🛑 Stopping Automation

### **Stop Real-Time Monitor**
```bash
# If you saved PID
kill $(cat logs/monitor.pid)

# Or find and kill
pkill -f realtime_monitor.py
```

### **Disable Cron Jobs**
```bash
crontab -e
# Comment out lines with #
```

### **Temporarily Disable**
```bash
# Stop monitor
pkill -f realtime_monitor.py

# Remove cron jobs
crontab -r  # WARNING: Removes ALL cron jobs
```

---

## ⚙️ Configuration

All scripts use `config.yaml` for settings:

```yaml
# Watchlist
watchlist:
  stocks: [AAPL, MSFT, GOOGL, ...]

# Alerts
alerts:
  conditions:
    price_change_pct: 5  # Alert threshold
    volume_surge_multiplier: 2.0
    rsi_oversold: 30
    rsi_overbought: 70

# Database
database:
  backup_enabled: true
  backup_interval_days: 7
  max_backups: 30

# Logging
logging:
  level: INFO
  max_log_size_mb: 10
  backup_count: 5
```

---

## 🧪 Testing Scripts

### **Test Daily Update (Dry Run)**
```bash
# Run for single stock
python scripts/daily_update.py
# Check logs for errors
```

### **Test Real-Time Monitor (5 minutes)**
```bash
# Run in foreground (Ctrl+C to stop)
python scripts/realtime_monitor.py
```

### **Test Backup**
```bash
python scripts/backup_database.py
# Check data/backups/ for new file
```

---

## 📈 Expected Behavior

### **Daily Update (6 PM)**
- Duration: 5-10 minutes (depends on watchlist size)
- Output: Updated database, alerts for strong signals
- Log: Summary with all processed stocks + scores

### **Real-Time Monitor (Market Hours)**
- Checks: Every 5 minutes
- Alerts: Only on significant events (>5% moves, volume surges)
- Sleep: 1 hour when market closed

### **Database Backup (2 AM)**
- Duration: <1 minute
- Output: New backup file in `data/backups/`
- Cleanup: Keeps 30 most recent backups

---

## 🚨 Troubleshooting

### **Script Not Running**
```bash
# Check Python path
which python

# Check virtual environment
source venv/bin/activate
python --version

# Check dependencies
pip list | grep yfinance
```

### **Cron Job Not Working**
```bash
# Check cron logs (macOS)
log show --predicate 'process == "cron"' --last 1h

# Check cron logs (Linux)
grep CRON /var/log/syslog

# Test cron command manually
cd /path/to/ai-stock-dashboard && source venv/bin/activate && python scripts/daily_update.py
```

### **No Alerts Received**
1. Check `config.yaml` → `alerts.enabled: true`
2. Test alerts: Open dashboard → Settings tab → "Test All Alerts"
3. Check logs for alert errors

### **Database Locked Error**
- Close dashboard before running scripts
- Or run scripts when dashboard is not active

---

## 💡 Best Practices

1. **Start Small**: Test with 3-5 stocks first
2. **Monitor Logs**: Check logs daily for errors
3. **Backup Before Updates**: Run backup script before major changes
4. **Use Absolute Paths**: In cron jobs, always use full paths
5. **Test Alerts**: Verify alert channels work before relying on them

---

## 🔗 Related Documentation

- **[README.md](../README.md)** - Main project documentation
- **[config.yaml](../config.yaml)** - Configuration reference
- **[ENHANCEMENT_PLAN.md](../ENHANCEMENT_PLAN.md)** - Development roadmap

---

## 📞 Support

If scripts fail or behave unexpectedly:

1. Check logs in `logs/` directory
2. Review `config.yaml` settings
3. Test scripts manually first
4. Ensure virtual environment is activated
5. Verify API keys (Reddit, Telegram) if using social/alerts

---

**🚀 Happy Automating! Set it and forget it! 🤖**
