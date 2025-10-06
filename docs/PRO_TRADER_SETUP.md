# 🚀 PROFESSIONAL TRADER SETUP GUIDE

> **Setup complet pour trader professionnel opportuniste**  
> Détection d'opportunités explosives 24/7 avec alertes instantanées

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Installation rapide](#installation-rapide)
3. [Configuration des alertes](#configuration-des-alertes)
4. [Lancement du système](#lancement-du-système)
5. [Monitoring 24/7](#monitoring-247)
6. [Dashboard de contrôle](#dashboard-de-contrôle)
7. [Optimisation](#optimisation)
8. [Dépannage](#dépannage)

---

## 🎯 Vue d'ensemble

### Architecture du système professionnel

```
┌─────────────────────────────────────────────────────────────┐
│                    PRO TRADER PLATFORM                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🌅 PREMARKET (4h-9h30 AM ET)                              │
│     ├─ Earnings announcements                              │
│     ├─ FDA approvals                                        │
│     ├─ M&A news                                             │
│     └─ Guidance updates                                     │
│                                                             │
│  📊 MARKET HOURS (9h30-16h ET)                             │
│     ├─ Pump stock detection (volume + price surge)         │
│     ├─ Real-time price monitoring                          │
│     ├─ Technical breakouts                                 │
│     └─ Volatility spikes                                   │
│                                                             │
│  🤖 AI DISCOVERY (24/7)                                    │
│     ├─ Gemini-powered opportunity detection                │
│     ├─ Multi-source news analysis                          │
│     ├─ Sentiment analysis                                  │
│     └─ Catalyst identification                             │
│                                                             │
│  🚨 INSTANT ALERTS                                         │
│     ├─ Telegram (< 5 sec)                                  │
│     ├─ Email (< 30 sec)                                    │
│     ├─ Desktop notifications                               │
│     └─ Audio alerts                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Caractéristiques principales

- **🌅 Détection prémarché** : Catalyseurs explosifs avant l'ouverture (4h-9h30 AM ET)
- **💎 Pump stocks** : Détection automatique volume surge + price spike
- **🤖 Intelligence IA** : Gemini AI pour découverte d'opportunités cachées
- **⚡ Latence minimale** : Alertes en < 30 secondes
- **📱 Multi-canal** : Telegram prioritaire, email backup, desktop, audio
- **🔄 Monitoring 24/7** : Système qui tourne en continu

---

## 🚀 Installation rapide

### 1. Prérequis

```bash
# Python 3.9+
python --version

# pip installé
pip --version
```

### 2. Installation des dépendances

```bash
# Dans le dossier du projet
pip install -r requirements.txt
```

### 3. Vérification

```bash
# Test rapide
python -c "import streamlit, yfinance, google.generativeai; print('✅ All dependencies OK')"
```

---

## 🔔 Configuration des alertes

### Configuration Telegram (RECOMMANDÉ - Alertes instantanées)

#### Étape 1 : Créer un bot Telegram

1. Ouvrir Telegram et chercher `@BotFather`
2. Envoyer `/newbot`
3. Suivre les instructions pour créer votre bot
4. **Copier le token** fourni (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Étape 2 : Obtenir votre Chat ID

1. Chercher votre bot dans Telegram
2. Cliquer "Start" ou envoyer `/start`
3. Ouvrir dans votre navigateur :
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
4. Chercher `"chat":{"id":` et **copier le numéro**

#### Étape 3 : Configurer le fichier .env

```bash
# Copier le template
cp .env.example .env

# Éditer .env
nano .env  # ou notepad .env sur Windows
```

**Contenu du .env :**

```bash
# Telegram Configuration (PRIORITAIRE)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321

# Email Configuration (BACKUP)
GMAIL_EMAIL=votre.email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

# Gemini AI (OPPORTUNITÉ AI)
GEMINI_API_KEY=your-gemini-api-key-here

# Reddit (SENTIMENT SOCIAL - OPTIONNEL)
REDDIT_CLIENT_ID=your-client-id
REDDIT_CLIENT_SECRET=your-client-secret
REDDIT_USER_AGENT=your-app-name
```

#### Étape 4 : Tester les alertes

```bash
# Test Telegram
python -c "from modules.alert_manager import AlertManager; from modules.utils import load_config; am = AlertManager(load_config()); print('✅ Telegram OK' if am.test_alerts().get('telegram') else '❌ Telegram FAILED')"
```

### Configuration Email (BACKUP)

#### Gmail App Password

1. Aller sur [Google Account Security](https://myaccount.google.com/security)
2. Activer "2-Step Verification"
3. Chercher "App passwords"
4. Générer un mot de passe pour "Mail"
5. **Copier le mot de passe** (16 caractères)
6. Ajouter dans `.env` :
   ```bash
   GMAIL_EMAIL=votre.email@gmail.com
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

### Configuration Gemini AI (OPPORTUNITÉS EXPLOSIVES)

#### Obtenir une clé API Gemini

1. Aller sur [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Cliquer "Get API Key"
3. Créer une clé
4. **Copier la clé**
5. Ajouter dans `.env` :
   ```bash
   GEMINI_API_KEY=AIzaSy...
   ```

---

## 🎛️ Lancement du système

### Option 1 : Control Center (RECOMMANDÉ)

Le Control Center est un dashboard de contrôle graphique pour gérer tous les monitors.

```bash
# Lancer le Control Center
streamlit run scripts/control_center.py
```

**Interface graphique :**
- ✅ Start/Stop monitors en un clic
- 📊 Statistiques en temps réel
- 🚨 Alertes récentes
- ⚙️ Configuration simplifiée

### Option 2 : Lancement manuel

#### Monitoring complet 24/7

```bash
# Mode standard (recommandé pour commencer)
python scripts/pro_trader_monitor.py

# Mode agressif (seuils plus bas, scans plus fréquents)
python scripts/pro_trader_monitor.py --aggressive

# Prémarché uniquement (4h-9h30 AM ET)
python scripts/pro_trader_monitor.py --premarket-only
```

#### En arrière-plan

**Linux/Mac :**
```bash
# Lancer en arrière-plan
nohup python scripts/pro_trader_monitor.py > logs/monitor.log 2>&1 &

# Vérifier le processus
ps aux | grep pro_trader_monitor

# Arrêter le processus
pkill -f pro_trader_monitor.py
```

**Windows :**
```powershell
# Lancer en arrière-plan (nouvelle console)
Start-Process python -ArgumentList "scripts\pro_trader_monitor.py" -WindowStyle Hidden

# Arrêter le processus
Stop-Process -Name python -Force
```

### Option 3 : Démarrage automatique

#### Linux/Mac (cron)

```bash
# Éditer crontab
crontab -e

# Ajouter cette ligne pour démarrage au reboot
@reboot cd /path/to/ai-stock-dashboard && nohup python scripts/pro_trader_monitor.py &

# OU pour lancer à 4h AM tous les jours
0 4 * * 1-5 cd /path/to/ai-stock-dashboard && python scripts/pro_trader_monitor.py --premarket-only
```

#### Windows (Task Scheduler)

1. Ouvrir **Task Scheduler**
2. Cliquer **Create Basic Task**
3. **Nom** : "Pro Trader Monitor"
4. **Trigger** : "When the computer starts" ou "Daily at 4:00 AM"
5. **Action** : "Start a program"
6. **Program** : `python.exe`
7. **Arguments** : `C:\path\to\ai-stock-dashboard\scripts\pro_trader_monitor.py`
8. **Start in** : `C:\path\to\ai-stock-dashboard`
9. **Finish**

---

## 📊 Monitoring 24/7

### Phases de monitoring

#### 1. 🌅 PREMARKET (4h00 - 9h30 AM ET)

**Focus : Catalyseurs explosifs**

- **Earnings** : Détection automatique des résultats
- **FDA** : Approbations de médicaments
- **M&A** : Annonces de fusions/acquisitions
- **Guidance** : Révisions de prévisions

**Alertes :**
- ✅ Telegram instantané (< 5 sec)
- ✅ Email backup
- ✅ Desktop CRITICAL uniquement

**Scan interval :** 10-15 minutes

#### 2. 📊 MARKET HOURS (9h30 - 16h00 ET)

**Focus : Pump stocks et mouvements explosifs**

- **Volume surge** : Détection 2x+ volume moyen
- **Price spike** : Mouvements 5%+ en quelques minutes
- **Breakouts** : Cassures de résistances
- **Momentum** : Accélérations de tendance

**Alertes :**
- ✅ Toutes les alertes (Telegram, Email, Desktop, Audio)

**Scan interval :** 1-3 minutes

#### 3. 🌙 AFTER HOURS (16h00 - 4h00 AM ET)

**Focus : Opportunités AI et préparation**

- **AI Discovery** : Analyse Gemini des news
- **Sentiment analysis** : Évolution du sentiment
- **Watchlist preparation** : Stocks à surveiller demain

**Alertes :**
- ✅ Opportunités high-confidence uniquement
- ✅ Telegram + Email

**Scan interval :** 30-60 minutes

### Que surveiller ?

#### Dashboard principal (app.py)

```bash
streamlit run app.py
```

- **🎯 AI-Discovered Opportunities** : Opportunités trouvées par Gemini
- **🚨 Monthly Signals** : Scores 0-100 et recommandations
- **📰 News & Sentiment** : Actualités agrégées
- **📈 Technical Analysis** : Indicateurs techniques

#### Logs en temps réel

```bash
# Suivre les logs
tail -f logs/pro_monitor.log

# Sur Windows
Get-Content logs/pro_monitor.log -Wait -Tail 50
```

#### Alertes Telegram

- **Chaque alerte arrive sur votre téléphone**
- **Format :**
  ```
  🚀 PUMP STOCK DETECTED 🚀

  📊 Symbol: AAPL
  💰 Price: $180.50 (+7.2%)
  📊 Volume: 3.5x average
  📈 Direction: UP

  ⚡ INSTANT ACTION REQUIRED
  ```

---

## 🎛️ Dashboard de contrôle

### Lancer le Control Center

```bash
streamlit run scripts/control_center.py
```

### Fonctionnalités

#### 1. 📡 Monitors Tab

- **Pro Trader Monitor** : 24/7 opportunity hunter
  - Status : ONLINE/OFFLINE
  - Actions : Start / Stop / Start Aggressive
  
- **Premarket Monitor** : Catalyst detection
  - Status : ONLINE/OFFLINE
  - Actions : Start / Stop
  
- **Realtime Monitor** : Live price monitoring
  - Status : ONLINE/OFFLINE
  - Actions : Start / Stop

#### 2. 🚨 Alerts Tab

- **Statistiques du jour** : Total, Critical, High, Medium
- **Timeline** : Graphique des alertes par heure
- **Détails** : Liste des 20 dernières alertes

#### 3. ⚙️ Configuration Tab

- **Channels** : Telegram, Email, Desktop, Audio
- **Thresholds** : Prix, Volume, Confidence AI
- **Test** : Boutons de test pour chaque canal

#### 4. 📊 Performance Tab

- **Métriques** : Alertes du jour, temps de réponse
- **Symboles uniques** : Nombre d'actions alertées
- **Timeline** : Distribution horaire

---

## ⚡ Optimisation

### Mode Agressif

Pour traders très actifs cherchant TOUTES les opportunités :

```bash
python scripts/pro_trader_monitor.py --aggressive
```

**Différences vs mode standard :**

| Paramètre | Standard | Agressif |
|-----------|----------|----------|
| Price Threshold | 5% | 3% |
| Volume Threshold | 2.0x | 1.5x |
| Premarket Scan | 15 min | 10 min |
| Market Scan | 3 min | 1 min |
| AI Scan | 60 min | 30 min |

**⚠️ Attention** : Mode agressif génère plus d'alertes (risque de sur-notification)

### Configuration personnalisée

Éditer `config.yaml` pour personnaliser :

```yaml
# Alert Settings
alerts:
  enabled: true
  channels:
    telegram: true     # Telegram prioritaire
    email: true        # Email backup
    desktop: true      # Notifications système
    audio: false       # Sons (peut déranger)
  
  conditions:
    price_change_pct: 5           # Alerte sur 5%+ moves
    volume_surge_multiplier: 2.0  # Alerte sur 2x avg volume
    rsi_oversold: 30
    rsi_overbought: 70
```

### Optimiser les performances

#### 1. Réduire la watchlist

Si trop d'alertes, réduire la watchlist dans `config.yaml` :

```yaml
watchlist:
  stocks:
    - AAPL
    - TSLA
    - NVDA
    # ... garder seulement vos préférées
  max_stocks: 50  # Limite à 50 au lieu de 250
```

#### 2. Filtrer par priorité

Recevoir seulement les alertes CRITICAL et HIGH :

```python
# Dans scripts/pro_trader_monitor.py
# Ligne ~290
if priority in ['CRITICAL', 'HIGH']:
    self.alert_manager.send_alert(...)
```

#### 3. Horaires personnalisés

Modifier les heures de monitoring :

```python
# Prémarché personnalisé (ex: 5h-9h au lieu de 4h-9h30)
premarket_start = now_et.replace(hour=5, minute=0)
premarket_end = now_et.replace(hour=9, minute=0)
```

---

## 🔧 Dépannage

### Problème : Aucune alerte Telegram

**Diagnostic :**
```bash
python -c "
from modules.alert_manager import AlertManager
from modules.utils import load_config
am = AlertManager(load_config())
print(am.test_alerts())
"
```

**Solutions :**
1. Vérifier `.env` : `TELEGRAM_BOT_TOKEN` et `TELEGRAM_CHAT_ID`
2. Tester le bot : envoyer `/start` dans Telegram
3. Vérifier le chat ID : `https://api.telegram.org/bot<TOKEN>/getUpdates`

### Problème : Monitor ne démarre pas

**Diagnostic :**
```bash
# Vérifier les logs
cat logs/pro_monitor.log

# Vérifier les processus
ps aux | grep pro_trader  # Linux/Mac
tasklist | findstr python  # Windows
```

**Solutions :**
1. Vérifier Python : `python --version` (3.9+)
2. Vérifier dépendances : `pip install -r requirements.txt`
3. Vérifier config : `python -c "from modules.utils import load_config; load_config()"`

### Problème : Trop d'alertes

**Solutions :**
1. Passer en mode standard (retirer `--aggressive`)
2. Augmenter les thresholds dans `config.yaml`
3. Réduire la watchlist
4. Filtrer par priorité (CRITICAL/HIGH uniquement)

### Problème : Gemini AI ne fonctionne pas

**Diagnostic :**
```bash
python -c "
from modules.gemini_analyzer import GeminiAnalyzer
from modules.utils import load_config
ga = GeminiAnalyzer(load_config())
print('Enabled' if ga.enabled else 'Disabled')
"
```

**Solutions :**
1. Vérifier `.env` : `GEMINI_API_KEY`
2. Vérifier la clé : [Google AI Studio](https://aistudio.google.com/app/apikey)
3. Vérifier les quotas : Gemini free tier = 60 requests/min

### Problème : Email ne fonctionne pas

**Solutions :**
1. Vérifier Gmail App Password (pas le mot de passe normal)
2. Activer "2-Step Verification" sur Google
3. Générer un nouveau App Password
4. Vérifier `.env` : `GMAIL_EMAIL` et `GMAIL_APP_PASSWORD`

---

## 📱 Utilisation quotidienne

### Routine du matin (avant 9h30 AM)

1. **Vérifier les alertes prémarché** (Telegram)
2. **Ouvrir le Control Center** : `streamlit run scripts/control_center.py`
3. **Vérifier les monitors** : Tous ONLINE
4. **Consulter les opportunités AI** : Dashboard principal
5. **Préparer la watchlist** : Ajouter les symboles alertés

### Pendant la journée (9h30-16h)

1. **Recevoir les alertes** : Telegram en temps réel
2. **Analyser les pump stocks** : Dashboard principal onglet "Monthly Signals"
3. **Vérifier le sentiment** : Onglet "News & Sentiment"
4. **Suivre les positions** : Onglet "Portfolio"

### Après la fermeture (après 16h)

1. **Revoir les alertes du jour** : Control Center > Alerts tab
2. **Analyser les performances** : Control Center > Performance tab
3. **Préparer le lendemain** : Opportunités AI pour demain
4. **Laisser tourner les monitors** : Préparation prémarché automatique

---

## 🎯 Stratégie de trading recommandée

### Pour profiter des alertes

#### 1. Pump Stocks (haute volatilité)

**Alerte :**
```
🚀 PUMP STOCK DETECTED
📊 AAPL | +6.5% | 3.2x volume
```

**Action :**
1. Ouvrir le dashboard : `streamlit run app.py`
2. Sélectionner le symbole alerté
3. Vérifier **Monthly Signal** (score 0-100)
4. Vérifier **Technical Analysis** (RSI, MACD, support/résistance)
5. Vérifier **News & Sentiment** (catalyseur ?)

**Critères d'entrée :**
- ✅ Score ≥ 75 (BUY ou STRONG BUY)
- ✅ RSI < 70 (pas overbought)
- ✅ News positives récentes
- ✅ Volume confirmé (pas de faux signal)

#### 2. Opportunités AI (Gemini Discovery)

**Alerte :**
```
💎 TRADING OPPORTUNITY
📊 NVDA | LOW risk | 85% confidence
💡 Strong earnings + AI growth catalysts
```

**Action :**
1. Lire le raisonnement complet (dashboard)
2. Vérifier **validation news** (confirmé/rejeté)
3. Vérifier **late entry risk** (pas trop tard ?)
4. Analyser **Monthly Signal**

**Critères d'entrée :**
- ✅ Confidence ≥ 70%
- ✅ Risk = LOW ou MEDIUM
- ✅ Validation confirmée
- ✅ Late entry risk ≤ MEDIUM

#### 3. Catalyseurs prémarché (haute probabilité)

**Alerte :**
```
🚨 PREMARKET ALERT
📊 MRNA | CRITICAL
⚡ FDA approval + Earnings beat
```

**Action :**
1. **Recherche immédiate** : Google le catalyseur
2. Vérifier si le marché a déjà réagi (prémarché price)
3. Attendre **l'ouverture** (9h30 AM ET)
4. Analyser les **5 premières minutes** (confirmation volume)

**Critères d'entrée :**
- ✅ Catalyseur confirmé (pas rumeur)
- ✅ Prémarché positif (+3%+)
- ✅ Volume d'ouverture élevé
- ✅ Pas de gap trop important (risque de pullback)

### Gestion des risques

**TOUJOURS appliquer :**

1. **Stop loss** : -8% automatique
2. **Position sizing** : Max 5% du capital par trade
3. **Risk/Reward** : Minimum 2.5:1
4. **Diversification** : Max 10 positions simultanées
5. **Trailing stop** : 5% en profit

---

## 🆘 Support et ressources

### Documentation

- **[README.md](../README.md)** : Vue d'ensemble du projet
- **[GEMINI_SETUP.md](GEMINI_SETUP.md)** : Configuration Gemini AI
- **[ALERT_SETUP_GUIDE.md](ALERT_SETUP_GUIDE.md)** : Configuration alertes détaillée
- **[PREMARKET_ALERTS_GUIDE.md](PREMARKET_ALERTS_GUIDE.md)** : Guide prémarché

### Logs

```bash
# Application principale
logs/app.log

# Monitoring professionnel
logs/pro_monitor.log

# Database
logs/database.log
```

### Commandes utiles

```bash
# Vérifier les processus en cours
ps aux | grep python  # Linux/Mac
tasklist | findstr python  # Windows

# Arrêter tous les monitors
pkill -f pro_trader_monitor  # Linux/Mac
Stop-Process -Name python -Force  # Windows

# Nettoyer les logs
rm logs/*.log  # Linux/Mac
del logs\*.log  # Windows

# Backup de la database
python scripts/backup_database.py
```

---

## 🎉 Félicitations !

Votre setup professionnel est maintenant opérationnel.

**Checklist finale :**

- ✅ Alertes Telegram configurées et testées
- ✅ Gemini AI activé (clé API configurée)
- ✅ Pro Trader Monitor lancé (24/7)
- ✅ Control Center accessible
- ✅ Dashboard principal fonctionnel
- ✅ Watchlist personnalisée

**Vous êtes maintenant équipé pour :**

- 🌅 Capter les opportunités prémarché
- 💎 Détecter les pump stocks en temps réel
- 🤖 Découvrir les pépites cachées avec l'IA
- 📱 Recevoir des alertes instantanées
- 📊 Analyser avec des outils professionnels

**Bon trading ! 🚀💰**

---

*"The stock market is a device for transferring money from the impatient to the patient." — Warren Buffett*

*"In trading, the goal is not to be right. The goal is to make money." — Alexander Elder*
