# 💎 AI Stock Trading Dashboard

[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)]()

> **Détecteur de pépites mensuelles avec scoring 0-100, news, sentiment et alertes**

Dashboard professionnel de trading qui scanne automatiquement **120+ actions** et détecte les meilleures opportunités avec signaux décisifs et backtesting complet.

![Main Dashboard](screenshots/main_dashboard.jpg)

## ✨ Fonctionnalités Principales

### 🎯 **Signaux Mensuels Décisifs**

- **Score 0-100** avec 5 composants pondérés (trend, momentum, sentiment, divergence, volume)
- **Recommandations claires**: STRONG BUY → STRONG SELL
- **Paramètres de trading**: Entry, Stop Loss, Take Profit, Risk/Reward
- **Position sizing** recommandé selon le score
- **Historique des scores** avec graphiques

### 📰 **News & Sentiment Analysis**

- **Multi-sources**: Yahoo Finance, Finviz, Reddit (r/stocks, r/wallstreetbets)
- **Sentiment analysis**: VADER + TextBlob + Keywords
- **Tendances**: Graphiques de sentiment sur 30 jours
- **100% gratuit** - Aucun API payant requis

### 💼 **Portfolio Tracking**

- **Suivi positions**: P&L réalisé et non-réalisé
- **Métriques**: Sharpe Ratio, Sortino, Calmar, Max Drawdown
- **Win rate** et profit factor
- **Paper trading** simulator

### 🔙 **Backtesting Engine**

- **Tests historiques** de stratégies mensuelles
- **Performance metrics** complets
- **Comparaison vs SPY** benchmark
- **Trade-by-trade** breakdown

### 🚨 **Système d'Alertes**

- **Multi-canaux**: Desktop, Email, Telegram, Audio
- **9 types d'alertes**: RSI, volume, sentiment, breakouts, etc.
- **Priorités automatiques**: CRITICAL → LOW

## 🚀 Démarrage Rapide (2 minutes)

### Installation

```bash
# 1. Cloner le projet
git clone https://github.com/yourusername/ai-stock-dashboard.git
cd ai-stock-dashboard

# 2. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer le dashboard
./run.sh
# Ou: streamlit run app.py

# 💡 BONUS: Utilisez le Makefile pour des commandes simplifiées!
make help      # Voir toutes les commandes
make install   # Installation auto
make run       # Lancement rapide
```

**Le dashboard s'ouvre à:** <http://localhost:8501>

### Configuration Optionnelle

Pour utiliser Reddit sentiment et alertes Telegram:

```bash
cp .env.example .env
# Éditer .env avec vos API keys (optionnel)
```

## 📊 Utilisation

### Workflow Quotidien

1. **Matin (8h-9h30)**: Lancer le scanner

   ```bash
   ./run.sh  # Choix 1: Dashboard
   ```

   - Cliquer "🚀 Lancer Scan Complet"
   - Analyser les 2-5 pépites détectées (score ≥ 85)

2. **Pendant Marché**: Surveiller positions
   - Onglet "💼 Portfolio" pour P&L temps réel
   - Alertes automatiques sur mouvements importants

3. **Après Marché**: Review et préparation
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

- **QUICKSTART.md** - Guide de démarrage rapide (5 minutes)
- **config.yaml** - Configuration système
- **.env.example** - Template pour API keys
- **docs/** - Documentation archivée (historique du projet)

Pour plus d'informations sur les anciennes versions, voir le dossier `docs/`.

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
