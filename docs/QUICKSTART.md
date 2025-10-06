# ⚡ Quick Start - AI Stock Trading Dashboard

## 🚀 Installation (2 minutes)

### 1. Prérequis

- Python 3.10+ 
- Terminal (macOS/Linux) ou PowerShell (Windows)

### 2. Installation

```bash
# Cloner le projet
git clone https://github.com/yourusername/ai-stock-dashboard.git
cd ai-stock-dashboard

# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate  # macOS/Linux
# Ou sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Lancement

```bash
# Option A: Script automatique (recommandé)
./run.sh

# Option B: Manuel
streamlit run app.py
```

**Dashboard disponible à:** http://localhost:8501

---

## 📊 Première Utilisation

### Onglet 1: Monthly Signals

1. Sélectionner une action dans la watchlist (ex: AAPL)
2. Attendre 10-20 secondes (calcul du score)
3. Lire le **score 0-100** et la recommandation
4. Examiner le breakdown des 5 composants
5. Vérifier les paramètres de trading (Entry/Stop/Target)

### Onglet 2: News & Sentiment

1. Voir les dernières news agrégées
2. Analyser le sentiment global (-1 à +1)
3. Consulter le graphique de tendance sentiment
4. Lire les articles avec sentiment positif/négatif

### Onglet 3: Portfolio

1. Utiliser le Paper Trading Simulator
2. Ajouter une position test
3. Voir le P&L en temps réel
4. Consulter les métriques de performance

### Onglet 6: Backtesting

1. Sélectionner des actions (ex: AAPL, MSFT, GOOGL)
2. Définir une période (ex: 2024-01-01 à aujourd'hui)
3. Cliquer "Run Backtest"
4. Analyser les résultats (return, Sharpe, drawdown)

---

## ⚙️ Configuration Optionnelle

### Reddit Sentiment (optionnel)

Pour activer l'analyse social media:

```bash
cp .env.example .env
```

Éditer `.env` et ajouter:

```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=MyTradingBot/1.0
```

Obtenir les credentials: https://www.reddit.com/prefs/apps

### Alertes Telegram (optionnel)

Pour recevoir des alertes sur Telegram:

1. Créer un bot via @BotFather
2. Obtenir le bot token
3. Obtenir votre chat ID (via @userinfobot)
4. Ajouter dans `.env`:

```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Alertes Email (optionnel)

Pour recevoir des alertes par email (Gmail):

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your@gmail.com
SENDER_PASSWORD=your_app_password
RECIPIENT_EMAIL=destination@email.com
```

**Note:** Utiliser un App Password Gmail, pas votre mot de passe normal.

---

## 🎯 Les 4 Modes

### Mode 1: Dashboard Interactif (Principal)

```bash
./run_trading_scanner.sh  # Choix 1
```

Interface visuelle complète avec tous les onglets.

### Mode 2: Scanner de Pépites

```bash
./run_trading_scanner.sh  # Choix 2
```

Scan rapide des 120+ actions, affiche uniquement les pépites (score ≥ 85).

### Mode 3: Scanner Automatique (4h)

```bash
./run_trading_scanner.sh  # Choix 3
```

Scan automatique toutes les 4 heures pendant les heures de marché.

### Mode 4: Monitoring Temps Réel (15min)

```bash
./run_trading_scanner.sh  # Choix 4
```

Scan toutes les 15 minutes pour day trading actif.

---

## 📈 Workflow Recommandé

### Semaine 1: Observation

- ✅ Lancer scans quotidiens
- ✅ Observer les patterns
- ✅ Comprendre les scores
- ❌ **NE PAS TRADER**

### Semaine 2: Paper Trading

- ✅ Simuler trades sur papier
- ✅ Noter tous les résultats
- ✅ Calculer le win rate
- ❌ **PAS D'ARGENT RÉEL**

### Semaine 3: Petites Positions

- ✅ 1% capital max par position
- ✅ 1-2 trades seulement
- ✅ Respecter les stops
- ✅ Apprendre de chaque trade

### Semaine 4+: Progression

- ✅ Augmenter graduellement
- ✅ Analyser statistiques
- ✅ Améliorer constamment
- ✅ Rester discipliné

---

## 🔧 Troubleshooting

### Erreur "Module not found"

```bash
# Vérifier que l'environnement virtuel est actif
source venv/bin/activate

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Dashboard ne lance pas

```bash
# Vérifier la version Python
python --version  # Doit être 3.10+

# Lancer manuellement
streamlit run app.py
```

### Pas de pépites détectées

- **Normal!** Les critères sont ultra-stricts (score ≥ 85)
- Essayez à un autre moment de la journée
- Ajustez les filtres dans le sidebar du dashboard

### Erreur Reddit API

Si vous n'avez pas configuré Reddit:
- Les scores fonctionnent quand même (sentiment à 60% news, 40% social)
- Social sentiment sera basé sur les news uniquement
- Optionnel: Configurer Reddit dans `.env`

---

## 📚 Documentation Complète

Pour plus d'informations:

- **README.md** - Documentation principale
- **config.yaml** - Tous les paramètres configurables
- **docs/** - Documentation archivée (historique du projet)

---

## ⚠️ Rappel Important

**🛡️ PROFESSIONAL TRADING SYSTEM**

This is a professional-grade institutional trading platform with mandatory risk controls:

- ✅ Real-time risk management with automatic stop losses
- ✅ Professional position sizing (maximum 2% risk per trade)
- ✅ Live market data validation and quality controls
- ⚠️ Trading involves substantial risk - professional protocols mandatory
- Consultez un conseiller financier

---

**Prêt à commencer? Lancez le dashboard:**

```bash
./run_dashboard.sh
```

**Bon trading! 💎📈**
