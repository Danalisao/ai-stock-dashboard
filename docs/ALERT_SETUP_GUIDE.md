# 🚨 Alert System Setup Guide

## Quick Setup (5 minutes)

### 1. Enable Alerts in Config

Edit `config.yaml`:

```yaml
alerts:
  enabled: true
  channels:
    desktop: true      # ✅ Always works (no setup needed)
    telegram: true     # ⚡ Recommended (instant mobile alerts)
    email: true        # 📧 Reliable backup
    audio: true        # 🔊 Sound notifications
```

### 2. Create .env File

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Telegram (RECOMMENDED - Best for mobile alerts)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# Gmail (BACKUP - Reliable email alerts)
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password

# Gemini AI (for opportunity detection)
GEMINI_API_KEY=your_gemini_api_key
```

---

## Telegram Setup (RECOMMENDED) ⚡

### Why Telegram?
- ✅ **Instant** notifications on your phone
- ✅ **Free** forever (no costs)
- ✅ **Reliable** (99.9% uptime)
- ✅ **No spam filters** (unlike email)
- ✅ **Works everywhere** (mobile, desktop, web)

### Step-by-Step:

#### 1. Create a Telegram Bot (2 minutes)

1. Open Telegram app
2. Search for **@BotFather**
3. Send `/newbot`
4. Choose a name: `My Stock Alert Bot`
5. Choose a username: `mystockalert_bot`
6. **Copy the token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### 2. Get Your Chat ID (1 minute)

1. Start a chat with your new bot
2. Send any message (e.g., "Hello")
3. Search for **@userinfobot** in Telegram
4. Send `/start`
5. **Copy your Chat ID** (looks like: `123456789`)

#### 3. Add to .env

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

#### 4. Test It!

```bash
python test_alerts.py
```

You should receive a test message on Telegram! 🎉

---

## Email Setup (Gmail) 📧

### Why Email?
- ✅ **Reliable** backup if Telegram fails
- ✅ **Archived** permanently (easy to review)
- ✅ **HTML formatting** with nice visuals

### Step-by-Step:

#### 1. Enable 2-Factor Authentication

1. Go to: https://myaccount.google.com/security
2. Enable **2-Step Verification**

#### 2. Generate App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Select **Mail** and your device
3. Click **Generate**
4. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

#### 3. Add to .env

```env
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop  # No spaces!
```

#### 4. Test It!

```bash
python test_alerts.py
```

Check your email inbox! 📬

---

## Desktop Notifications 💻

### Windows / macOS / Linux

**No setup needed!** Desktop notifications work automatically.

- Windows: System tray notifications
- macOS: Notification Center
- Linux: libnotify (should work out-of-box)

---

## Audio Alerts 🔊

### Setup (Optional)

1. Place sound files in `assets/sounds/`:
   - `critical_alert.mp3`
   - `high_alert.mp3`
   - `alert.mp3`

2. Or let it use system beep (automatic fallback)

---

## Alert Priority Logic 🎯

### Opportunity Alerts (Gemini AI Discovery)

When a **LOW RISK** opportunity is detected:

```
1️⃣  Try Telegram first (instant mobile alert)
     ↓ If fails
2️⃣  Try Email (reliable backup)
     ↓ If fails
3️⃣  Desktop notification + Audio sound
```

### Standard Trading Alerts

- **CRITICAL**: All channels (Telegram, Email, Desktop, Audio)
  - Example: Stop loss triggered
  
- **HIGH**: Telegram, Desktop, Audio
  - Example: Volume surge detected
  
- **MEDIUM**: Desktop only
  - Example: RSI oversold
  
- **LOW**: Log only (no notifications)

---

## Testing Your Setup 🧪

### Quick Test

```bash
# Test all alert channels
python test_alerts.py
```

### In-Dashboard Test

1. Launch dashboard: `streamlit run app.py`
2. Go to **Settings** tab
3. Click **"Test Alerts"** button
4. Check all channels

---

## Troubleshooting 🔧

### Telegram Not Working?

**Check:**
- ✅ Token format: `123456789:ABC...xyz` (numbers:letters)
- ✅ Chat ID format: `123456789` (only numbers)
- ✅ Started chat with bot? (send any message first)
- ✅ Bot not blocked?

**Test manually:**
```python
from telegram import Bot
bot = Bot(token="YOUR_TOKEN")
bot.send_message(chat_id="YOUR_CHAT_ID", text="Test")
```

### Email Not Working?

**Check:**
- ✅ 2FA enabled on Gmail?
- ✅ App password (not regular password)?
- ✅ No spaces in password?
- ✅ Less secure apps disabled? (App password bypasses this)

**Error "535 Authentication failed":**
- Generate new app password
- Make sure 2FA is enabled first

### Desktop Notifications Not Showing?

**Windows:**
- Check Focus Assist settings
- Enable notifications for Python

**macOS:**
- System Preferences → Notifications → Allow Python

**Linux:**
- Install: `sudo apt-get install libnotify-bin`

---

## Configuration Reference 📋

### config.yaml - Alert Settings

```yaml
alerts:
  enabled: true
  
  channels:
    desktop: true
    email: true
    telegram: true
    audio: true
  
  conditions:
    price_change_pct: 5          # Alert on 5%+ moves
    volume_surge_multiplier: 2.0  # Alert on 2x avg volume
    rsi_oversold: 30
    rsi_overbought: 70
    sentiment_shift: 0.3
    news_article_threshold: 10
  
  priority:
    critical_score: 85
    high_score: 75
    medium_score: 60
    low_score: 40
```

---

## Security Best Practices 🔐

### DO ✅

- ✅ Use environment variables (`.env` file)
- ✅ Add `.env` to `.gitignore`
- ✅ Use Gmail App Passwords (not main password)
- ✅ Regenerate tokens if leaked
- ✅ Keep bot token private

### DON'T ❌

- ❌ Commit `.env` to git
- ❌ Share tokens publicly
- ❌ Use main Gmail password
- ❌ Post tokens in screenshots/logs
- ❌ Reuse tokens across projects

---

## Examples 📚

### Opportunity Alert Example

```python
from modules.alert_manager import AlertManager
from modules.utils import load_config

config = load_config()
alert_mgr = AlertManager(config)

opportunity = {
    'ticker': 'AAPL',
    'risk_level': 'low',
    'confidence': 85,
    'reasoning': 'Strong earnings beat...',
    'explosion_catalysts': ['Earnings beat', 'New product launch']
}

# Send alert (tries Telegram → Email → Desktop)
alert_mgr.send_opportunity_alert(opportunity)
```

### Standard Alert Example

```python
# Send custom alert
alert_mgr.send_alert(
    alert_type='PRICE_ALERT',
    symbol='TSLA',
    message='Price dropped 10% today!',
    priority='HIGH',
    value=250.50
)
```

---

## FAQ ❓

**Q: Do I need all channels?**
A: No! Desktop works without setup. Telegram is recommended for best experience.

**Q: Are alerts free?**
A: Yes! Telegram, Gmail, and Desktop are all free.

**Q: How many alerts will I receive?**
A: Only for significant events:
- LOW RISK opportunities (auto-detected by AI)
- Major price moves (>5%)
- Volume surges (2x average)
- Critical portfolio events

**Q: Can I customize alert conditions?**
A: Yes! Edit `config.yaml` under `alerts.conditions`

**Q: Will I get spammed?**
A: No. Opportunities refresh every hour. Standard alerts have intelligent thresholds.

---

## Support 💬

Having issues? Check:

1. **Logs**: `./logs/app.log`
2. **Test script**: `python test_alerts.py`
3. **Documentation**: `README.md` and `QUICKSTART.md`

---

**Ready to receive trading alerts?** 🚀

```bash
# 1. Configure .env
cp .env.example .env
# Edit .env with your tokens

# 2. Test alerts
python test_alerts.py

# 3. Launch dashboard
streamlit run app.py
```

**Let the AI find opportunities while you sleep!** 😴💰
