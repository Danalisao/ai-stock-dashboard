# 🚀 QUICK START - PROFESSIONAL TRADER SETUP

> **Setup ultra-rapide pour commencer à détecter les opportunités explosives**

---

## ⚡ Démarrage en 5 minutes

### 1️⃣ Configuration des alertes Telegram (OBLIGATOIRE)

```bash
# 1. Créer un bot Telegram
# Ouvrir Telegram → Chercher @BotFather → /newbot
# Copier le token fourni

# 2. Obtenir votre Chat ID
# Démarrer une conversation avec votre bot → /start
# Ouvrir: https://api.telegram.org/bot<VOTRE_TOKEN>/getUpdates
# Copier "chat":{"id": XXXXXX}

# 3. Configurer .env
cp .env.example .env
nano .env  # ou notepad .env sur Windows
```

**Ajouter dans `.env` :**
```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321
GEMINI_API_KEY=your-gemini-key  # Optionnel mais recommandé
```

### 2️⃣ Lancer le système complet

```bash
# Windows
python scripts\launch_trading_system.py --all

# Linux/Mac
python scripts/launch_trading_system.py --all
```

### 3️⃣ Vérifier que tout fonctionne

```bash
# Tester les alertes
python scripts/launch_trading_system.py --status

# Vous devriez voir:
#   premarket_catalyst_scanner    🟢 ONLINE
#   realtime_pump_scanner         🟢 ONLINE
```

---

## 📱 Ce qui se passe maintenant

### 🌅 PRE-MARCHÉ (4h-9h30 AM ET)
- Scanner détecte: **Earnings**, **FDA**, **M&A**, **Guidance**
- Alertes Telegram **instantanées** (< 15 sec)
- Notification sur votre téléphone

### 💎 MARCHÉ OUVERT (9h30-16h ET)
- Détection **pump stocks** en temps réel
- **Volume surge** (3x+) + **Price spike** (5%+)
- Alertes avec score 0-100

### 🤖 IA 24/7
- Gemini analyse les news en continu
- Découverte d'opportunités cachées
- Scores de confiance

---

## 📊 Accéder au dashboard

```bash
# Ouvrir le dashboard principal
streamlit run app.py

# OU Control Center (recommandé)
streamlit run scripts/control_center.py
```

**URL:** http://localhost:8501

---

## 🎯 Exemple d'alerte Telegram

```
🚀🚀🚀 PUMP STOCK DETECTED 🚀🚀🚀

📊 Symbol: TSLA
💯 Score: 92.5/100
💰 Price: $245.67 (+7.8%)
📈 Volume: 4.2x average

📊 Technical Indicators:
  • RSI: 78.3
  • MACD: Bullish ✅
  • Momentum: 88.7/100

⚡ RECOMMENDATION:
🎯 STRONG BUY - Explosive momentum!

🕐 Detected: 10:23:45 ET
```

---

## ⚙️ Configuration avancée (optionnel)

### Mode Agressif (plus d'alertes)

```bash
# Seuils plus bas, scans plus fréquents
python scripts/launch_trading_system.py --all --aggressive
```

### Email (backup alertes)

```bash
# Ajouter dans .env
GMAIL_EMAIL=votre.email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx  # App Password, pas votre mdp normal
```

[Guide Gmail App Password](https://support.google.com/accounts/answer/185833)

### Gemini AI (opportunités IA)

```bash
# Obtenir une clé: https://aistudio.google.com/app/apikey
# Ajouter dans .env
GEMINI_API_KEY=your-api-key-here
```

---

## 🛑 Arrêter le système

```bash
# Arrêter tous les monitors
python scripts/launch_trading_system.py --stop-all

# OU via Control Center
streamlit run scripts/control_center.py
# → Onglet Monitors → Stop
```

---

## 🔥 Cas d'usage typique

### Trader opportuniste prémarché

```bash
# Lancer uniquement le scanner prémarché
python scripts/launch_trading_system.py --premarket

# Vous recevrez des alertes dès 4h AM sur:
# - Earnings beats/misses
# - FDA approvals (biotech 🚀)
# - M&A announcements
# - Unusual premarket volume
```

### Day trader actif

```bash
# Mode ultra-agressif pour catch tous les pumps
python scripts/launch_trading_system.py --realtime --aggressive

# Scan toutes les 15 secondes
# Seuils: 3%+ prix, 2x volume
# Alertes instantanées Telegram
```

### Investisseur long terme + opportunités IA

```bash
# Système complet avec IA Gemini
python scripts/launch_trading_system.py --all

# + Dashboard pour analyse approfondie
streamlit run app.py
```

---

## 📚 Documentation complète

- **[PRO_TRADER_SETUP.md](docs/PRO_TRADER_SETUP.md)** - Setup complet détaillé
- **[ALERT_SETUP_GUIDE.md](docs/ALERT_SETUP_GUIDE.md)** - Configuration alertes multi-canaux
- **[GEMINI_SETUP.md](docs/GEMINI_SETUP.md)** - Configuration Gemini AI

---

## 🚨 Dépannage rapide

### "No alerts received"
```bash
# Tester les alertes
python -c "from modules.alert_manager import AlertManager; from modules.utils import load_config; am = AlertManager(load_config()); print(am.test_alerts())"

# Vérifier .env
cat .env  # Linux/Mac
type .env  # Windows
```

### "Module not found"
```bash
# Réinstaller dépendances
pip install -r requirements.txt --upgrade
```

### "Market is closed"
```bash
# Normal ! Les scanners attendent l'ouverture
# Prémarché: 4h-9h30 AM ET
# Marché: 9h30-16h ET
```

---

## 💡 Conseils Pro

### ✅ À FAIRE
- Activer **Telegram** (alertes instantanées)
- Lancer le système **avant 4h AM** (catch premarket catalysts)
- Consulter le **Control Center** régulièrement
- Garder **Telegram notifications** activées sur mobile

### ❌ À ÉVITER
- Mode agressif sur watchlist > 100 stocks (surcharge)
- Ignorer les scores < 75 (faux signaux)
- Trader sans stop loss
- FOMO sur pumps déjà alertés il y a > 10 min

---

## 🎯 Prochaines étapes

1. **Tester le système maintenant** :
   ```bash
   python scripts/launch_trading_system.py --all
   ```

2. **Personnaliser votre watchlist** :
   - Éditer `config.yaml` → `watchlist.stocks`
   - Ajouter vos symboles favoris

3. **Monitorer vos gains** :
   - Utiliser le Portfolio Tracker dans le dashboard
   - Onglet "Portfolio" → Ajouter vos positions

4. **Déploiement 24/7** :
   - Serveur Unraid, Raspberry Pi, ou VPS
   - Docker: `docker-compose up -d`

---

## 🚀 Bon trading !

> **Ce système est conçu pour vous donner un avantage décisif sur le marché.**  
> **Utilisez-le de manière responsable et disciplinée.**

**Questions ?** → Consultez `docs/PRO_TRADER_SETUP.md`

---

**Version:** 2.0  
**Last Updated:** 6 Octobre 2025  
**Support:** GitHub Issues
