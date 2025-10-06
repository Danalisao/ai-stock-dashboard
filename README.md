# 🚀 AI Stock Trading Dashboard# 💎 AI Stock Trading Dashboard

> **Plateforme professionnelle de trading avec système intraday automatique**[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/)

[![Streamlit](https://img.shields.io/badge/Streamlit-1.50-red)](https://streamlit.io/)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)](https://streamlit.io/)[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)]()

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Plateforme de trading professionnel avec IA - Détection d'opportunités explosives 24/7**

---

Dashboard professionnel de trading qui scanne automatiquement **250+ actions** et détecte les meilleures opportunités avec signaux décisifs, alertes instantanées et monitoring prémarché.

## 📋 Table des Matières

![Main Dashboard](screenshots/main_dashboard.jpg)

- [Vue d'ensemble](#-vue-densemble)

- [Fonctionnalités](#-fonctionnalités)---

- [Démarrage Rapide](#-démarrage-rapide)

- [Trading Intraday Automatique](#-trading-intraday-automatique)## 🚀 SETUP PROFESSIONNEL DE TRADING

- [Documentation](#-documentation)

- [Architecture](#-architecture)### **Nouveau : Monitoring 24/7 pour Trader Opportuniste**

---Ce système est conçu pour les traders professionnels qui veulent **saisir TOUTES les opportunités explosives**, particulièrement en prémarché (4h-9h30 AM ET) quand les mouvements les plus importants se produisent.

## 🎯 Vue d'ensemble**🎯 Caractéristiques professionnelles :**

Plateforme complète de trading professionnel combinant :- **🌅 Détection Prémarché** : Earnings, FDA, M&A, guidance AVANT l'ouverture

- **💎 Pump Stocks** : Détection automatique volume surge + price spike

- 📊 **Analyse technique avancée** (50+ indicateurs)- **🤖 IA Gemini** : Découverte d'opportunités cachées par intelligence artificielle

- 🤖 **IA Gemini** pour analyse de marché- **⚡ Alertes Instantanées** : Telegram (< 5 sec), Email, Desktop, Audio

- ⚡ **Trading intraday automatique** avec notifications Telegram- **🔄 Monitoring 24/7** : Le système tourne en continu et vous alerte automatiquement

- 📰 **Agrégation de news** multi-sources- **📊 Control Center** : Dashboard de contrôle pour gérer tous les monitors

- 💼 **Gestion de portfolio** avec P&L tracking

- 🔮 **Prédictions ML** (LSTM, Random Forest, XGBoost)### **Démarrage Rapide Professionnel**

- 🎯 **Scoring 0-100** pour signaux mensuels

- 📱 **Alertes multi-canaux** (Telegram, Email, Desktop, Audio)#### **Option 1 : Lancement Automatique (RECOMMANDÉ)**

---**Windows :**

```bash

## ✨ Fonctionnalités# Double-cliquer sur

launch_pro_trading.bat

### 🔥 Trading Intraday Automatique (NOUVEAU)```



**Système 100% automatique qui scanne le marché et vous alerte via Telegram :****Linux/Mac :**

```bash

- ⚡ **5 types de setups** : ORB, Momentum Breakout, VWAP Reversal, Volume Surge, BB Breakoutchmod +x launch_pro_trading.sh

- 📱 **Notifications instantanées** : Entry/Exit avec prix, stop loss, target, R/R./launch_pro_trading.sh

- 🔄 **Scan continu** : 9:30-16:00 ET (30s standard / 15s agressif)```

- 🛑 **Auto-close** : Fermeture automatique avant 16h (zéro risque overnight)

- 🎯 **Scoring intelligent** : 0-100 basé sur prix, volume, technicals, momentum#### **Option 2 : Control Center (Interface Graphique)**



**Lancement** :```bash

```bashstreamlit run scripts/control_center.py

# Mode standard (3-7 alertes/jour)```

python scripts/intraday_trader.py

Le Control Center vous permet de :

# Mode agressif (10-20 alertes/jour)  - ✅ Démarrer/arrêter tous les monitors en un clic

python scripts/intraday_trader.py --aggressive- 📊 Voir les alertes en temps réel

```- ⚙️ Configurer les canaux d'alerte

- 📈 Consulter les statistiques de performance

📖 **Guide complet** : [`docs/INTRADAY_TRADING_GUIDE.md`](docs/INTRADAY_TRADING_GUIDE.md)

#### **Option 3 : Monitoring Direct 24/7**

---

```bash

## 🚀 Démarrage Rapide# Mode standard (seuils équilibrés)

python scripts/pro_trader_monitor.py

### 1️⃣ Installation

# Mode agressif (plus d'alertes, seuils plus bas)

```bashpython scripts/pro_trader_monitor.py --aggressive

# Cloner

git clone https://github.com/Danalisao/ai-stock-dashboard.git# Prémarché uniquement (4h-9h30 AM ET)

cd ai-stock-dashboardpython scripts/pro_trader_monitor.py --premarket-only

```

# Environnement virtuel

python -m venv .venv### **Configuration Obligatoire (5 minutes)**

.\.venv\Scripts\Activate.ps1  # Windows

# source .venv/bin/activate    # Linux/MacPour recevoir les alertes instantanées, configurez **au minimum Telegram**

# Dépendances1. **Créer `.env` depuis le template**

pip install -r requirements.txt   ```bash

```   cp .env.example .env

   ```

### 2️⃣ Configuration

2. **Configurer Telegram** (PRIORITAIRE - alertes < 5 sec) :

Créer `.env` :   - Créer un bot : chercher `@BotFather` sur Telegram

- Obtenir le token : `/newbot`

```env   - Obtenir votre chat ID : https://api.telegram.org/bot<TOKEN>/getUpdates

# Telegram (OBLIGATOIRE)   - Ajouter dans `.env` :

TELEGRAM_BOT_TOKEN=your_token     ```bash

TELEGRAM_CHAT_ID=your_chat_id     TELEGRAM_BOT_TOKEN=123456789:ABC...

     TELEGRAM_CHAT_ID=987654321

# Gemini AI (optionnel)     ```

GEMINI_API_KEY=your_key

```3. **Configurer Gemini AI** (OPPORTUNITÉS) :

   - Obtenir une clé : https://aistudio.google.com/app/apikey

### 3️⃣ Test   - Ajouter dans `.env` :

     ```bash

```bash     GEMINI_API_KEY=AIzaSy...

python scripts/test_intraday_system.py     ```

```

4. **Tester les alertes** :

### 4️⃣ Lancement   ```bash

   python -c "from modules.alert_manager import AlertManager; from modules.utils import load_config; print(AlertManager(load_config()).test_alerts())"

```bash```

# Dashboard

python -m streamlit run app.py### **Documentation Complète**

# Intraday trader📖 **[Guide Setup Professionnel Complet](docs/PRO_TRADER_SETUP.md)** ⭐ NOUVEAU

python scripts/intraday_trader.py

```- Installation détaillée

- Configuration des alertes (Telegram, Email, Audio)

---- Déploiement 24/7 (cron, Task Scheduler)

- Optimisation et personnalisation

## ⚡ Trading Intraday- Stratégies de trading recommandées

- Dépannage

### Exemple Notification

---

```

🟢 INTRADAY ENTRY SIGNAL 🟢![Main Dashboard](screenshots/main_dashboard.jpg)

📊 Symbol: TSLA## ✨ Fonctionnalités Principales

🎯 Setup: Momentum Breakout

💯 Score: 87.3/100### 🎯 **Signaux Mensuels Décisifs**

💰 Entry: $245.80- **Score 0-100** avec 5 composants pondérés (trend, momentum, sentiment, divergence, volume)

🛑 Stop: $241.30 (-1.8%)- **Recommandations claires**: STRONG BUY → STRONG SELL

🎯 Target: $253.80 (+3.3%)- **Paramètres de trading**: Entry, Stop Loss, Take Profit, Risk/Reward

📊 R/R: 1:1.8- **Position sizing** recommandé selon le score

- **Historique des scores** avec graphiques

⚡ ACTION: BUY @ $245.80

```### 📰 **News & Sentiment Analysis**



### Auto-Start Windows- **Multi-sources**: Yahoo Finance, Finviz, Reddit (r/stocks, r/wallstreetbets)

- **Sentiment analysis**: VADER + TextBlob + Keywords

Task Scheduler :- **Tendances**: Graphiques de sentiment sur 30 jours

- Program: `.venv\Scripts\python.exe`- **100% gratuit** - Aucun API payant requis

- Arguments: `scripts\start_intraday_system.py`

- Trigger: At startup### 💼 **Portfolio Tracking**



---- **Suivi positions**: P&L réalisé et non-réalisé

- **Métriques**: Sharpe Ratio, Sortino, Calmar, Max Drawdown

## 📚 Documentation- **Win rate** et profit factor

- **Paper trading** simulator

- 📖 [Guide Intraday](docs/INTRADAY_TRADING_GUIDE.md) - **Guide complet**

- 🎯 [Quick Start](docs/QUICKSTART.md)### 🔙 **Backtesting Engine**

- 🔧 [Setup Pro](docs/PRO_TRADER_SETUP.md)

- 🤖 [Gemini AI](docs/GEMINI_SETUP.md)- **Tests historiques** de stratégies mensuelles

- 📧 [Gmail](docs/GMAIL_APP_PASSWORD_GUIDE.md)- **Performance metrics** complets

- **Comparaison vs SPY** benchmark

---- **Trade-by-trade** breakdown



## 🏗️ Architecture### 🚨 **Système d'Alertes**



```- **Multi-canaux**: Desktop, Email, Telegram, Audio

ai-stock-dashboard/- **9 types d'alertes**: RSI, volume, sentiment, breakouts, etc.

├── app.py                          # Dashboard Streamlit- **🌅 Alertes Pré-Marchés**: Earnings, FDA, M&A, guidance (4:00-9:30 AM ET)

├── modules/                        # Modules Python- **Priorités automatiques**: CRITICAL → LOW

│   ├── alert_manager.py

│   ├── technical_indicators.py## 🚀 Démarrage Rapide (2 minutes)

│   ├── monthly_signals.py

│   ├── gemini_analyzer.py### Installation

│   └── ...

├── scripts/```bash

│   ├── intraday_trader.py         # ⭐ Scanner intraday# 1. Cloner le projet

│   ├── start_intraday_system.py   # ⭐ Auto-startgit clone https://github.com/yourusername/ai-stock-dashboard.git

│   └── ...cd ai-stock-dashboard

├── docs/                           # Documentation

└── data/                           # Données# 2. Créer l'environnement virtuel

```python3 -m venv venv

source venv/bin/activate  # Windows: venv\Scripts\activate

---

# 3. Installer les dépendances

## 🎮 Commandespip install -r requirements.txt



```bash# 4. Lancer le dashboard

# Dashboard./run.sh

python -m streamlit run app.py# Ou: streamlit run app.py



# Intraday standard# 💡 BONUS: Utilisez le Makefile pour des commandes simplifiées!

python scripts/intraday_trader.pymake help      # Voir toutes les commandes

make install   # Installation auto

# Intraday agressifmake run       # Lancement rapide

python scripts/intraday_trader.py --aggressive```



# Tests**Le dashboard s'ouvre à:** <http://localhost:8501>

python scripts/test_intraday_system.py

### Configuration Optionnelle

# Lanceur Windows

launch_intraday.batPour utiliser Reddit sentiment et alertes Telegram:

```

```bash

---cp .env.example .env

# Éditer .env avec vos API keys (optionnel)

## ⚠️ Disclaimer```



- ❌ Éducatif uniquement - Pas de conseil financier## 📊 Utilisation

- ❌ Risques de perte en capital

- ✅ Consultez un conseiller agréé### Workflow Quotidien

- ✅ Commencez en paper trading

- ✅ Utilisez toujours des stop loss1. **Matin (8h-9h30)**: Lancer le scanner



---   ```bash

   ./run.sh  # Choix 1: Dashboard

## 📄 Licence   ```



MIT License   - Cliquer "🚀 Lancer Scan Complet"

   - Analyser les 2-5 pépites détectées (score ≥ 85)

---

2. **Pendant Marché**: Surveiller positions

**Version** : 2.0 Intraday     - Onglet "💼 Portfolio" pour P&L temps réel

**Status** : ✅ Production Ready   - Alertes automatiques sur mouvements importants



**💰 Bon trading ! 📈🚀**3. **Après Marché**: Review et préparation

   - Onglet "🔙 Backtesting" pour tester stratégies
   - Ajuster watchlist si nécessaire

### Les 7 Onglets

- **🚨 Monthly Signals**: Score 0-100 et recommandations
- **📰 News & Sentiment**: Agrégation multi-sources
- **💼 Portfolio**: Suivi positions et performance
- **📈 Technical Analysis**: Charts et indicateurs
- **🔮 ML Predictions**: Prédictions machine learning
- **🔙 Backtesting**: Tests historiques de stratégies
- **⚙️ Settings**: Configuration et alertes

## 🧠 Algorithme de Scoring

Le score 0-100 est calculé avec **5 composants pondérés**:

```
Score = (Trend × 30%) + (Momentum × 20%) + (Sentiment × 25%) + 
        (Divergence × 15%) + (Volume × 10%)
```

**Mapping Score → Action:**

- **90-100**: STRONG BUY 🟢🟢🟢 (5-10% position)
- **75-89**: BUY 🟢🟢 (3-5% position)
- **60-74**: MODERATE BUY 🟢 (1-3% position)
- **40-59**: HOLD ⚖️ (attendre meilleur setup)
- **26-39**: MODERATE SELL 🔴
- **11-25**: SELL 🔴🔴
- **0-10**: STRONG SELL 🔴🔴🔴

## 📊 Architecture

```
ai-stock-dashboard/
├── app.py                    # Dashboard principal
├── modules/                  # 10 modules core
│   ├── monthly_signals.py    # 🎯 Algorithme de scoring
│   ├── news_aggregator.py    # Yahoo + Finviz + Reddit
│   ├── sentiment_analyzer.py # VADER + TextBlob
│   ├── alert_manager.py      # Multi-channel alerts
│   ├── portfolio_tracker.py  # Performance tracking
│   ├── backtester.py         # Backtesting engine
│   └── ...
├── scripts/                 # Automation
│   ├── daily_update.py       # Mise à jour quotidienne
│   ├── realtime_monitor.py   # Monitoring temps réel
│   └── backup_database.py    # Backups auto
├── data/                    # SQLite database
└── config.yaml              # Configuration
```

## ⚠️ Professional Risk Disclosure

**🛡️ PROFESSIONAL TRADING SYSTEM**

This is a professional-grade trading system designed for experienced traders and institutions.

**Risk Management Protocols:**
- ✅ Mandatory 8% stop loss on all positions
- ✅ Maximum 2% risk per trade (institutional standard)
- ✅ Real-time portfolio risk monitoring
- ✅ Professional position sizing algorithms
- ✅ Minimum 2.5:1 risk/reward ratio

**Legal Notice:**
Trading involves substantial risk of loss. Past performance does not guarantee future results. 
All trading decisions remain your sole responsibility. You must comply with all applicable 
securities regulations in your jurisdiction. Professional risk management protocols are mandatory.

## 📚 Documentation

- **[QUICKSTART.md](docs/QUICKSTART.md)** - Guide de démarrage rapide (5 minutes)
- **[GEMINI_SETUP.md](docs/GEMINI_SETUP.md)** - Configuration AI Gemini (détection opportunités explosives)
- **[REDDIT_SETUP.md](docs/REDDIT_SETUP.md)** - Configuration Reddit API (sentiment social)
- **[ALERT_SETUP_GUIDE.md](docs/ALERT_SETUP_GUIDE.md)** - Configuration système d'alertes
- **[PREMARKET_ALERTS_GUIDE.md](docs/PREMARKET_ALERTS_GUIDE.md)** - 🌅 Alertes pré-marchés (earnings, FDA, M&A)
- **config.yaml** - Configuration système
- **.env.example** - Template pour API keys
- **docs/** - Documentation complète (guides et historique)

Pour plus d'informations, voir le dossier `docs/`.

## 📝 License

MIT License - Voir [LICENSE](LICENSE) pour détails.

## 🙏 Remerciements

Conçu avec:

- **Python 3.13** - Langage principal
- **Streamlit** - Framework dashboard
- **yfinance** - Données stocks (gratuit)
- **VADER** - Analyse de sentiment
- **PRAW** - Reddit API
- **Plotly** - Graphiques interactifs

---

**Built with ❤️ for decisive traders**

*"In God we trust. All others must bring data."* — W. Edwards Deming
