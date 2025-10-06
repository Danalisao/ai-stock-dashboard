# ⚡ QUICKSTART PROFESSIONNEL - 5 Minutes

> **Setup minimal pour commencer à trader avec alertes instantanées**

---

## 🚀 Installation (2 minutes)

### 1. Cloner et installer

```bash
git clone https://github.com/yourusername/ai-stock-dashboard.git
cd ai-stock-dashboard
pip install -r requirements.txt
```

### 2. Configuration Telegram (OBLIGATOIRE - 3 minutes)

**Pourquoi Telegram ?** Alertes instantanées (< 5 sec) directement sur votre téléphone.

#### Étape 1 : Créer un bot

1. Ouvrir Telegram
2. Chercher `@BotFather`
3. Envoyer `/newbot`
4. Suivre les instructions
5. **COPIER le token** (ex: `123456789:ABCdefGHIjklMNOpqrs`)

#### Étape 2 : Obtenir votre Chat ID

1. Chercher votre bot dans Telegram
2. Cliquer "Start"
3. Ouvrir dans votre navigateur :
   ```
   https://api.telegram.org/bot<VOTRE_TOKEN>/getUpdates
   ```
4. Chercher `"chat":{"id":` et **copier le numéro**

#### Étape 3 : Configurer .env

```bash
# Copier le template
cp .env.example .env

# Éditer (Windows: notepad .env, Linux/Mac: nano .env)
```

**Contenu minimal du .env :**

```bash
# Telegram (OBLIGATOIRE)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrs
TELEGRAM_CHAT_ID=987654321

# Gemini AI (FORTEMENT RECOMMANDÉ)
GEMINI_API_KEY=votre-clé-ici
```

**Obtenir une clé Gemini (GRATUIT) :**
- Aller sur https://aistudio.google.com/app/apikey
- Cliquer "Get API Key"
- Copier la clé

---

## 🎛️ Lancement (1 minute)

### Option 1 : Launcher Automatique (LE PLUS SIMPLE)

**Windows :**
```bash
# Double-cliquer sur le fichier
launch_pro_trading.bat
```

**Linux/Mac :**
```bash
chmod +x launch_pro_trading.sh
./launch_pro_trading.sh
```

### Option 2 : Control Center

```bash
streamlit run scripts/control_center.py
```

### Option 3 : Direct 24/7

```bash
# Monitoring complet
python scripts/pro_trader_monitor.py

# Mode agressif (plus d'alertes)
python scripts/pro_trader_monitor.py --aggressive
```

---

## ✅ Vérification

### Test des alertes

```bash
python -c "from modules.alert_manager import AlertManager; from modules.utils import load_config; print(AlertManager(load_config()).test_alerts())"
```

**Résultat attendu :**
```
telegram: True
email: False (optionnel)
desktop: True
```

Si Telegram = **True**, c'est BON ! Vous allez recevoir les alertes.

---

## 📱 Utilisation Quotidienne

### Matin (avant 9h30)

1. **Vérifier Telegram** : Alertes prémarché (earnings, FDA, M&A)
2. **Ouvrir le dashboard** : `streamlit run app.py`
3. **Consulter les opportunités AI** : En haut du dashboard

### Pendant la journée

1. **Recevoir les alertes** : Telegram vous notifie automatiquement
2. **Analyser** : Ouvrir le dashboard, sélectionner le symbole alerté
3. **Décider** : Score ≥ 75 = BUY signal

### Format des alertes

#### Pump Stock

```
🚀 PUMP STOCK DETECTED 🚀

📊 Symbol: AAPL
💰 Price: $180.50 (+7.2%)
📊 Volume: 3.5x average
📈 Direction: UP

⚡ INSTANT ACTION REQUIRED
```

#### Opportunité AI

```
💎 TRADING OPPORTUNITY DETECTED 💎

📊 Symbol: NVDA
🎯 Risk Level: LOW
📈 Confidence: 85%

💡 Reasoning:
Strong AI growth catalysts + positive earnings

⚡ Catalysts:
  • AI chip demand surge
  • Earnings beat expectations
  • New product launches

🚀 Source: Gemini AI Discovery
```

#### Prémarché

```
🚨 PREMARKET ALERT 🚨

📊 Symbol: MRNA
🎯 Priority: CRITICAL
⚡ FDA approval + Earnings beat

📰 Headline:
FDA approves new mRNA vaccine...

🔗 Source: Reuters
```

---

## 🎯 Critères de Trading

### Quand ACHETER (suite à une alerte)

✅ **Score Monthly Signal** ≥ 75 (BUY ou STRONG BUY)  
✅ **RSI** < 70 (pas overbought)  
✅ **News positives** récentes (24h)  
✅ **Volume confirmé** (pas de faux signal)  
✅ **Confidence AI** ≥ 70% (pour opportunités Gemini)

### Gestion du risque (TOUJOURS)

- **Stop loss** : -8% automatique
- **Position size** : Max 5% du capital par trade
- **Risk/Reward** : Minimum 2.5:1
- **Max positions** : 10 simultanées

---

## 🔧 Dépannage Rapide

### ❌ Telegram ne fonctionne pas

```bash
# Vérifier la config
cat .env | grep TELEGRAM

# Tester manuellement
python -c "
import requests
BOT_TOKEN = 'VOTRE_TOKEN'
CHAT_ID = 'VOTRE_CHAT_ID'
url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
requests.post(url, json={'chat_id': CHAT_ID, 'text': 'Test OK'})
"
```

### ❌ Monitor ne démarre pas

```bash
# Vérifier Python
python --version  # Doit être 3.9+

# Réinstaller dépendances
pip install -r requirements.txt --force-reinstall

# Vérifier les logs
cat logs/pro_monitor.log
```

### ❌ Gemini AI ne fonctionne pas

```bash
# Vérifier la clé API
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print(os.getenv('GEMINI_API_KEY'))
"
```

Si la clé s'affiche, c'est OK. Sinon, vérifier `.env`.

---

## 📚 Documentation Complète

Pour aller plus loin :

- **[PRO_TRADER_SETUP.md](docs/PRO_TRADER_SETUP.md)** : Guide complet (installation, optimisation, stratégies)
- **[ALERT_SETUP_GUIDE.md](docs/ALERT_SETUP_GUIDE.md)** : Configuration détaillée des alertes
- **[GEMINI_SETUP.md](docs/GEMINI_SETUP.md)** : Configuration Gemini AI
- **[README.md](README.md)** : Vue d'ensemble du projet

---

## 💡 Conseils Pro

### 1. Laisser tourner 24/7

Le système doit tourner **en permanence** pour capter toutes les opportunités, surtout en prémarché (4h-9h30 AM ET).

**Déploiement permanent :**

**Windows** : Task Scheduler au démarrage  
**Linux/Mac** : cron avec `@reboot`

Voir [PRO_TRADER_SETUP.md](docs/PRO_TRADER_SETUP.md) section "Démarrage automatique"

### 2. Mode agressif pour day trading

Si vous faites du day trading actif :

```bash
python scripts/pro_trader_monitor.py --aggressive
```

**Attention** : Génère plus d'alertes (peut être sur-notifiant).

### 3. Filtrer par priorité

Si trop d'alertes, désactiver les alertes LOW/MEDIUM dans `config.yaml` :

```yaml
alerts:
  priority:
    critical_score: 85  # Seulement CRITICAL et HIGH
    high_score: 75
```

### 4. Watchlist personnalisée

Réduire la watchlist dans `config.yaml` pour moins d'alertes :

```yaml
watchlist:
  stocks:
    - AAPL
    - TSLA
    - NVDA
    # ... vos préférées seulement
  max_stocks: 50  # Au lieu de 250
```

---

## ✅ Checklist Finale

Avant de trader, vérifiez :

- ✅ Telegram configuré et testé
- ✅ Gemini AI activé (clé dans .env)
- ✅ Monitor lancé (pro_trader_monitor.py)
- ✅ Dashboard accessible (streamlit run app.py)
- ✅ Alertes reçues sur Telegram

**Si tout est ✅, vous êtes prêt à trader ! 🚀💰**

---

## 🆘 Support

**Problème persistant ?**

1. Consulter [PRO_TRADER_SETUP.md](docs/PRO_TRADER_SETUP.md) section "Dépannage"
2. Vérifier les logs : `logs/pro_monitor.log`
3. Réinstaller les dépendances : `pip install -r requirements.txt --force-reinstall`

---

*"The best time to start was yesterday. The second best time is now."*

**Bon trading ! 📈🚀**
