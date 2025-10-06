# 🤖 Guide des Alertes Automatiques

## Vue d'Ensemble

Le système d'alertes automatiques détecte les opportunités **LOW RISK** grâce à Gemini AI et envoie automatiquement des alertes (Telegram/Email/Desktop) pendant les heures de marché.

---

## 🚀 Utilisation

### Mode 1: Scan Continu (Recommandé)

Lance le scanner qui tourne en continu pendant les heures de marché :

```bash
python scripts/auto_opportunity_alerts.py
```

**Comportement:**
- ✅ Scanne toutes les 60 minutes (par défaut)
- ✅ Respect automatique des heures de marché (9:30-16:00 ET, Lun-Ven)
- ✅ Dort automatiquement quand le marché est fermé
- ✅ Reprend automatiquement à la prochaine ouverture
- ✅ Alertes uniquement pour opportunités LOW RISK

### Mode 2: Scan Unique

Lance un scan unique et arrête :

```bash
python scripts/auto_opportunity_alerts.py --once
```

**Parfait pour:**
- 🔄 Cron jobs (automatisation)
- 🧪 Tests rapides
- 📊 Scans ponctuels

### Mode 3: Interval Personnalisé

Change l'intervalle entre les scans :

```bash
# Scan toutes les 30 minutes
python scripts/auto_opportunity_alerts.py --interval 30

# Scan toutes les 2 heures  
python scripts/auto_opportunity_alerts.py --interval 120
```

---

## ⏰ Heures de Marché

**Le scanner respecte automatiquement les heures d'ouverture US :**

- **Jours**: Lundi à Vendredi
- **Heures**: 9:30 AM - 4:00 PM (Eastern Time)
- **Fermé**: Week-ends et jours fériés

**Quand le marché est fermé:**
- Le scanner dort automatiquement
- Se réveille à la prochaine ouverture
- Aucun scan inutile

---

## 📋 Workflow Automatique

```
1️⃣  Vérification: Marché ouvert?
     ↓ OUI
2️⃣  Fetch: 100 articles de marché (multi-sources)
     ↓
3️⃣  Analyse: Gemini AI détecte opportunités
     ↓
4️⃣  Filtrage: Garde uniquement LOW RISK
     ↓
5️⃣  Alertes: Envoie Telegram → Email → Desktop
     ↓
6️⃣  Sauvegarde: BDD pour historique
     ↓
7️⃣  Attente: 60 minutes
     ↓
8️⃣  Retour à l'étape 1
```

---

## 🎯 Critères de Détection

### LOW RISK Opportunities

Pour qu'une alerte soit envoyée automatiquement, l'opportunité doit être :

1. **Risk Level**: LOW (vs MEDIUM ou HIGH)
2. **Confidence**: ≥ 70% (recommandé par Gemini AI)
3. **Catalysts**: Au moins 2-3 événements majeurs
4. **News Volume**: Minimum 10+ articles pertinents
5. **Timing**: Catalyseurs récents (< 7 jours)

### Exemples d'Opportunités LOW RISK:

✅ **Entreprises établies** avec earnings beat  
✅ **Leaders de marché** avec nouveaux contrats  
✅ **Blue chips** avec upgrades d'analystes  
✅ **Secteurs défensifs** avec momentum positif  

❌ **Évite automatiquement:**
- Penny stocks < $5
- Entreprises sans revenue
- Pure spéculation
- Volatilité excessive

---

## 🚨 Système d'Alertes

### Priorité de Fallback

```
1. Telegram (Instant, Mobile)
   ↓ Si échec
2. Email (Fiable, Archive)
   ↓ Si échec  
3. Desktop + Audio (Local)
```

### Message d'Alerte Type

```
💎 TRADING OPPORTUNITY DETECTED 💎

📊 Symbol: AAPL
🎯 Risk Level: LOW
📈 Confidence: 85%

💡 Reasoning:
Apple beat earnings by 15% with strong iPhone sales.
Three major analyst upgrades to $200 target.
Partnership with major automotive manufacturer announced.

⚡ Catalysts:
  • Earnings beat expectations by 20%
  • New AI chip announcement
  • Partnership with major automaker
  • Stock buyback program expansion

🚀 Source: Gemini AI Discovery
```

---

## 📊 Logs & Monitoring

### Voir les Logs en Direct

```bash
tail -f logs/app.log
```

### Logs Importants

- ✅ `🟢 Market is OPEN - Starting scan...`
- ✅ `✅ Found 4 opportunities`
- ✅ `💎 LOW RISK opportunities: 2`
- ✅ `✅ Alert sent successfully for AAPL`
- 🔴 `🔴 Market closed. Next open: 2025-10-07 09:30 EDT`

---

## 🔧 Configuration

### Variables d'Environnement (.env)

```env
# Gemini AI (REQUIS)
GEMINI_API_KEY=your_gemini_api_key_here

# Telegram (Recommandé)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# Email (Backup)
GMAIL_EMAIL=your@gmail.com
GMAIL_APP_PASSWORD=your_app_password
```

### Config.yaml

```yaml
alerts:
  enabled: true
  channels:
    telegram: true  # Priorité 1
    email: true     # Priorité 2
    desktop: true   # Priorité 3
    audio: true     # Priorité 3
```

---

## 🖥️ Lancer au Démarrage

### Windows (Task Scheduler)

1. Ouvrir Task Scheduler
2. Create Basic Task
3. Trigger: "At system startup"
4. Action: Start program
   - Program: `C:\Path\To\Python\python.exe`
   - Arguments: `C:\Path\To\ai-stock-dashboard\scripts\auto_opportunity_alerts.py`
   - Start in: `C:\Path\To\ai-stock-dashboard`

### Linux/Mac (systemd ou cron)

**Systemd Service:**

```bash
sudo nano /etc/systemd/system/stock-alerts.service
```

```ini
[Unit]
Description=AI Stock Opportunity Alerts
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/ai-stock-dashboard
ExecStart=/path/to/python scripts/auto_opportunity_alerts.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable stock-alerts
sudo systemctl start stock-alerts
```

**Cron (scan unique toutes les heures):**

```bash
crontab -e
```

```cron
# Toutes les heures pendant les heures de marché
0 10-16 * * 1-5 cd /path/to/ai-stock-dashboard && python scripts/auto_opportunity_alerts.py --once
```

---

## 📈 Exemples d'Utilisation

### Trader Actif (Scan fréquent)

```bash
# Scan toutes les 15 minutes pendant le marché
python scripts/auto_opportunity_alerts.py --interval 15
```

### Investisseur Long-Terme (Scan espacé)

```bash
# Scan toutes les 4 heures
python scripts/auto_opportunity_alerts.py --interval 240
```

### Démo / Test

```bash
# Un seul scan pour tester
python scripts/auto_opportunity_alerts.py --once
```

---

## 🛡️ Sécurité & Best Practices

### ✅ À FAIRE

- ✅ Lancer dans un environnement virtuel (venv)
- ✅ Configurer .env avec vos vraies clés API
- ✅ Vérifier les logs régulièrement
- ✅ Tester avec `--once` avant mode continu
- ✅ Utiliser Telegram pour alertes temps réel

### ❌ À ÉVITER

- ❌ Ne jamais commit le fichier .env
- ❌ Ne pas scanner trop fréquemment (< 15 min)
- ❌ Ne pas ignorer les alertes LOW RISK
- ❌ Ne pas trader sans analyse personnelle

---

## 🐛 Troubleshooting

### "Gemini AI not enabled"

➡️ Vérifiez `GEMINI_API_KEY` dans .env

```bash
# Test rapide
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅ OK' if os.getenv('GEMINI_API_KEY') else '❌ Missing')"
```

### "No opportunities found"

➡️ **Normal !** Les opportunités LOW RISK sont rares (c'est bon signe)

- Attendez le prochain scan (60 min)
- Vérifiez que le marché est ouvert
- Consultez les logs pour détails

### "Alert failed to send"

➡️ Vérifiez la configuration Telegram/Email

```bash
# Test les alertes
python test_alerts.py
```

### Scanner ne se réveille pas

➡️ Vérifiez le timezone et l'heure système

```bash
python -c "from modules.utils import is_market_open; print('Market Open' if is_market_open() else 'Market Closed')"
```

---

## 📊 Statistiques

### Voir l'Historique des Opportunités

```python
from modules.database_manager import DatabaseManager
from modules.utils import load_config

db = DatabaseManager(load_config().get('database', {}))

# Créer une requête SQL pour les opportunités
conn = db._get_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM opportunities ORDER BY created_at DESC LIMIT 20")
for row in cursor.fetchall():
    print(dict(row))
```

---

## 💡 Conseils

1. **Commencez avec `--once`** pour tester
2. **Utilisez Telegram** pour alertes mobiles
3. **Logs dans un fichier** séparé pour analyse
4. **Ne tradez pas tout** ce qui est alerté (faites votre DD)
5. **Combinez avec Monthly Signals** dans le dashboard

---

## 🎯 Workflow Recommandé

### Matin (8:30 AM)

```bash
# Lance le scanner avant ouverture
python scripts/auto_opportunity_alerts.py
```

### Pendant la Journée

- 📱 Recevez alertes Telegram en temps réel
- 📊 Analysez opportunités dans le dashboard
- ✅ Validez avec Monthly Signals
- 💼 Prenez décisions éclairées

### Soir (après fermeture)

- 📈 Reviewez opportunités du jour
- 📝 Préparez watchlist pour demain
- 🔄 Scanner se met en veille automatiquement

---

**Le scanner tourne en fond. Vous vivez votre vie. Les pépites arrivent automatiquement.** 💎📲

---

## Support

Problème ? Vérifiez :

1. Logs: `logs/app.log`
2. Config: `config.yaml`
3. Credentials: `.env`
4. Tests: `python test_alerts.py`

**Le système est conçu pour tourner H24, 7j/7, sans intervention.** 🚀
