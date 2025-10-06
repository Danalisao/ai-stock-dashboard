# 🚀 GUIDE TRADING INTRADAY AUTOMATIQUE

> **Système 100% automatique** - Recevez des notifications Telegram pour chaque opportunité intraday  
> **Aucune action humaine requise** - Le système scanne et alerte 24/7

---

## 🎯 Qu'est-ce que le Trading Intraday ?

Le **trading intraday** (ou "day trading") consiste à ouvrir ET fermer des positions **le même jour**.

**Avantages**:
- ✅ Pas de risque overnight (positions fermées avant 16h)
- ✅ Profits rapides (2-5% par trade)
- ✅ Plusieurs trades par jour possibles
- ✅ Réaction immédiate aux nouvelles du marché

**Ce système détecte automatiquement**:
- 📈 Momentum breakouts (prix + volume explosifs)
- 🎯 Opening Range Breakouts (cassures après ouverture)
- 💹 VWAP reversals (retournements autour VWAP)
- 🚀 Volume surge plays (volumes anormaux)
- 📊 Bollinger Band breakouts

---

## 📱 Exemple de Notification Telegram

Vous recevrez des alertes structurées comme ceci :

### 🟢 ENTRY Signal (Entrée)

```
🟢 INTRADAY ENTRY SIGNAL 🟢

📊 Symbol: TSLA
🎯 Setup: Momentum Breakout
📈 Direction: BULLISH
💯 Score: 87.3/100
⭐ Confidence: 90%

💰 Entry: $245.80
🛑 Stop Loss: $241.30 (-1.8%)
🎯 Target: $253.80 (+3.3%)
📊 R/R: 1:1.8

📊 Price: $245.80 (+4.2% today)
📈 Volume: 6.2x average

📊 Technical:
  • RSI: 68.5
  • MACD: Bullish ✅
  • vs VWAP: +1.2%
  • ATR: 2.1%

🕐 Time: 10:23:45 ET

⚡ ACTION: BUY @ $245.80
```

### 💰 EXIT Signal (Sortie)

```
💰 INTRADAY EXIT SIGNAL 💰

📊 Symbol: TSLA
📉 Exit Reason: ✅ Target Hit

💰 Entry: $245.80
💵 Exit: $253.50
📊 P&L: +3.1%

🕐 Time: 11:47:22 ET

🎉 PROFIT!
```

---

## ⚙️ Configuration Initiale (5 minutes)

### 1️⃣ Configurer Telegram Bot

Le système envoie **TOUTES** les alertes via Telegram.

#### Étape 1: Créer un Bot

1. Ouvrir Telegram
2. Chercher `@BotFather`
3. Envoyer `/newbot`
4. Choisir un nom (ex: "My Intraday Trader")
5. Copier le **token** (format: `1234567890:ABCdefGHI...`)

#### Étape 2: Obtenir votre Chat ID

1. Démarrer conversation avec votre bot (cliquer "Start")
2. Envoyer un message (ex: "/start")
3. Ouvrir cette URL dans navigateur (remplacer `YOUR_TOKEN`):
   ```
   https://api.telegram.org/botYOUR_TOKEN/getUpdates
   ```
4. Chercher `"chat":{"id":123456789}` et copier le nombre

#### Étape 3: Configurer .env

Ouvrir le fichier `.env` à la racine du projet et ajouter :

```env
# Telegram Configuration (OBLIGATOIRE)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHI...
TELEGRAM_CHAT_ID=123456789

# Gemini AI (optionnel mais recommandé)
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2️⃣ Installer les dépendances

```bash
# Activer environnement virtuel
.\.venv\Scripts\Activate.ps1

# Installer dépendances
pip install -r requirements.txt
```

### 3️⃣ Tester le système

```bash
# Test complet
python scripts/test_trading_system.py

# Si test Telegram réussit, c'est bon ! ✅
```

---

## 🚀 Lancement du Système

### Option 1: Lancement Manuel (pour tester)

```bash
# Mode standard (recommandé pour commencer)
python scripts/intraday_trader.py

# Mode agressif (plus d'alertes, critères plus souples)
python scripts/intraday_trader.py --aggressive
```

Le système va :
1. ✅ Envoyer notification de démarrage
2. ⏰ Attendre les heures de marché (9:30-16:00 ET)
3. 🔍 Scanner automatiquement toutes les 30 secondes
4. 📱 Envoyer alertes Telegram pour chaque opportunité

### Option 2: Lancement Automatique (24/7 sans intervention)

#### Windows Task Scheduler (Démarrage automatique au boot)

1. **Ouvrir Task Scheduler**
   - Appuyer sur `Win + R`
   - Taper `taskschd.msc`
   - Appuyer sur Entrée

2. **Créer une nouvelle tâche**
   - Cliquer `Create Task` (Action → Create Task)
   - Onglet **General**:
     - Name: `Intraday Trading System`
     - Description: `Système automatique de trading intraday`
     - ✅ Cocher `Run whether user is logged on or not`
     - ✅ Cocher `Run with highest privileges`

3. **Configurer le déclencheur (Trigger)**
   - Onglet **Triggers** → New
   - Begin the task: `At startup` (au démarrage)
   - ✅ Cocher `Enabled`
   - OK

4. **Configurer l'action**
   - Onglet **Actions** → New
   - Action: `Start a program`
   - Program/script: `C:\Mes Projets AI\ai-stock-dashboard\.venv\Scripts\python.exe`
   - Add arguments: `C:\Mes Projets AI\ai-stock-dashboard\scripts\start_intraday_system.py`
   - Start in: `C:\Mes Projets AI\ai-stock-dashboard`
   - OK

5. **Configurer les paramètres**
   - Onglet **Settings**:
     - ✅ `Allow task to be run on demand`
     - ✅ `Run task as soon as possible after a scheduled start is missed`
     - ✅ `If the task fails, restart every: 1 minute`
     - ✅ `Attempt to restart up to: 3 times`
     - ❌ Décocher `Stop the task if it runs longer than`

6. **Sauvegarder**
   - Cliquer OK
   - Entrer mot de passe Windows si demandé

**✅ C'est fait ! Le système démarrera automatiquement à chaque boot Windows.**

#### Tester le Task Scheduler

```bash
# Option 1: Redémarrer Windows et vérifier Telegram
# Option 2: Clic droit sur la tâche → Run
```

Vous devriez recevoir une notification Telegram :
```
🤖 INTRADAY SYSTEM STARTED

✅ Le système de trading intraday est maintenant actif.
...
```

---

## 📊 Fonctionnement du Système

### Heures d'Activité

- **9:30-15:45 ET**: Scan actif + alertes entry/exit
- **15:45-16:00 ET**: Auto-close toutes positions (éviter overnight)
- **16:00-9:30 ET**: Veille (pas de scan)

### Critères de Détection

#### Mode Standard (recommandé)
- 📈 Prix: +3% minimum
- 📊 Volume: 5x la moyenne
- 💹 Volatilité (ATR): > 1.5%
- 🎯 Score minimum: 75/100
- ⏱️ Scan: toutes les 30 secondes

#### Mode Agressif (plus de trades)
- 📈 Prix: +2% minimum
- 📊 Volume: 3x la moyenne
- 💹 Volatilité (ATR): > 1.0%
- 🎯 Score minimum: 70/100
- ⏱️ Scan: toutes les 15 secondes

### Watchlist Intraday

Le système surveille automatiquement:

**Tech High Volume**:
- AAPL, TSLA, NVDA, AMD, MSFT, GOOGL, META, AMZN

**Momentum Stocks**:
- GME, AMC, PLTR, SOFI, RIOT, MARA

**Indices ETF**:
- SPY, QQQ, IWM

**High Volatility**:
- NIO, LCID, RIVN, F, BAC, T, INTC

**💡 Personnaliser la watchlist**: Éditer `config.yaml` section `watchlist.intraday`

---

## 🎯 Types de Setups Détectés

### 1. Opening Range Breakout (ORB)

**Définition**: Prix casse le range des 5 premières minutes

**Exemple**:
```
📊 Setup: Opening Range Breakout
📈 Direction: BULLISH
🎯 Le prix casse au-dessus du high des 5 premières minutes
```

**Quand entrer**: Dès réception alerte ENTRY

---

### 2. Momentum Breakout

**Définition**: Prix explose avec volume massif

**Exemple**:
```
📊 Setup: Momentum Breakout
💯 Score: 92/100
📈 Prix: +6.2% avec 8x volume
```

**Quand entrer**: Immédiatement (momentum fort)

---

### 3. VWAP Reversal

**Définition**: Prix rebondit autour du VWAP

**Exemple**:
```
📊 Setup: VWAP Reversal
📈 Direction: BULLISH
💹 Prix au-dessus VWAP + RSI oversold
```

**Quand entrer**: Confirmation RSI (< 35 pour BULLISH)

---

### 4. Volume Surge Play

**Définition**: Volume anormal avec mouvement prix

**Exemple**:
```
📊 Setup: Volume Surge
📈 Volume: 12x average
💰 Prix: +4.5%
```

**Quand entrer**: Si score > 80

---

## 📱 Interpréter les Alertes

### Priorités

| Priorité | Signification | Action |
|----------|---------------|--------|
| **HIGH** | Score > 85, setup très fort | ✅ Entrer immédiatement |
| **MEDIUM** | Score 75-85, setup correct | ⚠️ Vérifier chart avant entrée |

### Informations Clés

#### Entry Alert

```
💰 Entry: $245.80          ← Prix d'entrée recommandé
🛑 Stop Loss: $241.30      ← Sortir si prix atteint (limite pertes)
🎯 Target: $253.80         ← Objectif de profit
📊 R/R: 1:1.8              ← Risk/Reward (min 1:1.5 pour être valable)
```

**Comment utiliser**:
1. Vérifier R/R (doit être ≥ 1:1.5)
2. Placer ordre d'achat @ Entry
3. Placer stop loss @ Stop Loss
4. Placer take profit @ Target

#### Exit Alert

```
💰 Entry: $245.80
💵 Exit: $253.50
📊 P&L: +3.1%              ← Profit/Perte du trade
```

**Types de sortie**:
- ✅ `Target Hit`: Objectif atteint (PROFIT)
- 🛑 `Stop Loss`: Stop touché (PERTE)
- 🔔 `AUTO_CLOSE`: Fermeture avant 16h (éviter overnight)

---

## ⚠️ Gestion du Risque

### Règles ESSENTIELLES

1. **❌ JAMAIS ignorer le stop loss**
   - Le stop est calculé pour limiter la perte à ~2% maximum
   - Si stop touché = sortir immédiatement

2. **❌ JAMAIS garder position après 15:45 ET**
   - Le système ferme automatiquement avant 16h
   - Évite le risque overnight (gap down du lendemain)

3. **✅ TOUJOURS vérifier le Risk/Reward**
   - R/R minimum acceptable: 1:1.5
   - Idéal: 1:2 ou plus
   - Si R/R < 1:1.5, ignorer le trade

4. **✅ Limiter la taille de position**
   - Recommandé: 2-5% du capital par trade
   - Maximum: 10% du capital
   - Exemple: Capital $10,000 → Max $500 par trade

5. **✅ Pas plus de 3 positions simultanées**
   - Diversifier mais pas trop
   - Éviter surexposition

---

## 🔧 Commandes Utiles

### Vérifier le statut

```bash
# Voir si le système tourne
python scripts/launch_trading_system.py --status
```

### Arrêter le système

```bash
# Arrêter tous les monitors
python scripts/launch_trading_system.py --stop-all

# OU via Task Scheduler
# Task Scheduler → Clic droit sur tâche → End
```

### Consulter les logs

```bash
# Logs intraday trader
type logs\intraday_trader.log

# Logs auto-start
type logs\auto_start.log

# Logs app principal
type logs\app.log
```

### Tester les alertes manuellement

```bash
# Test complet
python scripts/test_trading_system.py

# Test Telegram uniquement
python -c "from modules.alert_manager import AlertManager; AlertManager().send_alert('Test', 'Test intraday', 'HIGH', 'test')"
```

---

## 📊 Dashboard & Suivi

### Accès au Dashboard

```bash
# Lancer dashboard
streamlit run app.py
```

**URL**: http://localhost:8501

### Onglet "Live Alerts"

- 📊 Status des monitors (online/offline)
- 📱 Historique des 50 dernières alertes
- 📈 Statistiques du jour
- 📉 Timeline graphique

### Control Center

```bash
# Lancer control center
streamlit run scripts/control_center.py
```

**URL**: http://localhost:8502

- 🎛️ Gérer tous les monitors
- 📊 Voir alertes en temps réel
- ✅ Tester les systèmes

---

## 🐛 Dépannage

### Problème: Pas de notification Telegram

**Solutions**:

1. Vérifier configuration `.env`:
   ```bash
   type .env
   # Doit contenir TELEGRAM_BOT_TOKEN et TELEGRAM_CHAT_ID
   ```

2. Tester Telegram:
   ```bash
   python scripts/test_trading_system.py
   # Voir si test Telegram passe ✅
   ```

3. Vérifier bot actif:
   - Ouvrir Telegram
   - Chercher votre bot
   - Envoyer `/start`

### Problème: Système ne démarre pas au boot

**Solutions**:

1. Vérifier Task Scheduler:
   - Ouvrir Task Scheduler
   - Chercher "Intraday Trading System"
   - Clic droit → Run (tester manuellement)

2. Vérifier logs:
   ```bash
   type logs\auto_start.log
   ```

3. Vérifier chemins dans Task Scheduler:
   - Program: Doit pointer vers `python.exe` du venv
   - Arguments: Doit pointer vers `start_intraday_system.py`

### Problème: Trop d'alertes (spam)

**Solutions**:

1. Passer en mode standard (si en mode agressif):
   ```bash
   # Arrêter mode agressif
   python scripts/launch_trading_system.py --stop-all
   
   # Relancer en mode standard
   python scripts/intraday_trader.py
   ```

2. Augmenter score minimum:
   - Éditer `scripts/intraday_trader.py`
   - Ligne ~80: `self.min_score = 80` (au lieu de 75)

3. Réduire watchlist:
   - Éditer `config.yaml`
   - Section `watchlist.intraday`: garder 5-10 symboles max

### Problème: Pas d'alertes du tout

**Solutions**:

1. Vérifier heures de marché:
   ```bash
   # Le système alerte uniquement 9:30-16:00 ET (lundi-vendredi)
   ```

2. Vérifier critères (peut-être trop stricts):
   - Essayer mode agressif:
     ```bash
     python scripts/intraday_trader.py --aggressive
     ```

3. Vérifier volatilité du marché:
   - Jours calmes = moins d'opportunités
   - Jours volatils (earnings, news) = plus d'alertes

---

## 📈 Stratégie Recommandée

### Pour Débutants

1. **Commencer en mode observation**
   - Lancer le système
   - Observer les alertes pendant 1 semaine
   - Ne PAS trader immédiatement

2. **Paper trading**
   - Noter entrée/sortie sur papier
   - Calculer résultats fictifs
   - Analyser performances

3. **Commencer petit**
   - 1-2 trades par jour max
   - Positions de $100-200 (petit capital)
   - Focus: respect du stop loss

### Pour Intermédiaires

1. **Mode standard**
   - 3-5 trades par jour
   - Positions 2-5% du capital
   - Ratio R/R minimum 1:2

2. **Tenir journal de trading**
   - Noter chaque trade
   - Analyser réussites/échecs
   - Améliorer stratégie

3. **Diversifier setups**
   - Tester différents types (ORB, Momentum, VWAP)
   - Identifier ceux qui fonctionnent le mieux
   - Se spécialiser

### Pour Avancés

1. **Mode agressif**
   - 5-10 trades par jour
   - Positions 5-10% du capital
   - Scalping rapide (< 1h holding)

2. **Optimisation**
   - Personnaliser watchlist
   - Ajuster seuils de score
   - Combiner avec analyse fondamentale

3. **Automation partielle**
   - Utiliser broker API (Alpaca, IB)
   - Auto-exécution des trades
   - Risk management automatique

---

## 🎓 Ressources Supplémentaires

### Apprendre le Trading Intraday

- 📚 [Investopedia - Day Trading](https://www.investopedia.com/day-trading-4689660)
- 📹 YouTube: "Day Trading For Beginners"
- 📖 Livre: "How to Day Trade for a Living" - Andrew Aziz

### Outils Complémentaires

- 📊 [TradingView](https://www.tradingview.com) - Charts professionnels
- 📱 [Webull](https://www.webull.com) - Trading mobile
- 💹 [Finviz](https://finviz.com) - Screener stocks

### Communautés

- 💬 Reddit: r/Daytrading
- 💬 Discord: Groupes day trading
- 💬 Twitter: Traders actifs (#DayTrading)

---

## ⚖️ Disclaimer

**⚠️ AVERTISSEMENT IMPORTANT**

Ce système est fourni **à titre éducatif uniquement**.

- ❌ Ce n'est **PAS** un conseil financier
- ❌ Les performances passées ne garantissent **PAS** les résultats futurs
- ❌ Le trading comporte des **risques de perte en capital**
- ❌ Ne tradez **jamais** avec de l'argent que vous ne pouvez pas perdre

**Recommandations**:
- ✅ Consultez un conseiller financier agréé
- ✅ Commencez avec un compte démo (paper trading)
- ✅ Ne risquez que ce que vous pouvez perdre
- ✅ Éduquez-vous continuellement

**Le trading intraday est une activité à haut risque.**

---

## 📞 Support

### Questions ?

1. Consulter cette documentation
2. Vérifier logs: `logs/intraday_trader.log`
3. Tester système: `python scripts/test_trading_system.py`
4. Vérifier configuration: `.env` et `config.yaml`

### Bugs ?

1. Consulter logs
2. Créer issue GitHub
3. Fournir logs + configuration

---

## 🚀 Prochaines Étapes

Maintenant que le système est configuré:

1. ✅ **Tester**: `python scripts/intraday_trader.py`
2. ✅ **Observer**: Recevoir quelques alertes Telegram
3. ✅ **Analyser**: Comprendre les setups détectés
4. ✅ **Configurer Task Scheduler**: Automatisation 24/7
5. ✅ **Paper trade**: Tester sans argent réel
6. ✅ **Live trading**: Commencer petit

---

**🎯 Vous êtes prêt ! Le système va scanner automatiquement et vous envoyer des alertes Telegram pour chaque opportunité intraday.**

**📱 Gardez votre téléphone à portée de main pendant les heures de marché (9:30-16:00 ET) !**

---

**Version**: 1.0  
**Date**: 6 Octobre 2025  
**Status**: ✅ Production Ready
