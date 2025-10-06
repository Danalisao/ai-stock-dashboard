# 🌅 Pre-Market Alerts Guide

## Overview

Le système d'alertes pré-marchés surveille automatiquement les **annonces importantes** avant l'ouverture du marché (4:00 AM - 9:30 AM ET) et vous envoie des notifications instantanées.

## 🎯 Annonces Surveillées

### CRITICAL Priority 🚨
- **Faillites** : Bankruptcy, Chapter 11
- **Fusions & Acquisitions** : Merger, acquisition, buyout, takeover
- **FDA Approvals** : FDA approval, FDA clearance

### HIGH Priority ⚡
- **Résultats trimestriels** : Earnings, quarterly results, Q1/Q2/Q3/Q4
- **Guidance** : Financial guidance, upgrades, downgrades
- **Clinical Trials** : Phase 2, Phase 3 results

### MEDIUM Priority 📢
- **Dividendes** : Dividend announcements, special dividends
- **Buybacks** : Share repurchase programs
- **Leadership** : CEO changes, executive appointments
- **SEC Filings** : 8-K, 10-Q, 10-K

## 🚀 Installation

### Prérequis

Le système d'alertes pré-marchés est déjà installé avec l'application. Assurez-vous d'avoir :

```bash
# Dependencies are in requirements.txt
pip install -r requirements.txt
```

Packages requis :
- `pytz` : Gestion des fuseaux horaires
- `requests` : Requêtes HTTP
- `feedparser` : Lecture RSS
- `beautifulsoup4` : Scraping news

### Configuration des Alertes

**1. Configurez au moins un canal d'alerte** dans `config.yaml` :

```yaml
alerts:
  enabled: true
  channels:
    telegram: true    # Recommandé pour pre-market
    email: true       # Backup
    desktop: false    # Éviter spam
    audio: false
```

**2. Configurez vos credentials** dans `.env` :

```bash
# Telegram (RECOMMANDÉ pour pre-market)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Email (Backup)
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
```

> **💡 Telegram est fortement recommandé** pour les alertes pré-marchés car vous pouvez les recevoir sur votre téléphone même si vous dormez encore.

## 📱 Utilisation

### Mode Single Scan

Lance un scan unique et envoie les alertes :

```bash
# Scanner tout le marché
python scripts/premarket_monitor.py

# Scanner uniquement votre watchlist
python scripts/premarket_monitor.py --watchlist AAPL TSLA MSFT NVDA
```

### Mode Continuous

Lance un monitoring continu avec scans périodiques :

```bash
# Scan toutes les 30 minutes (défaut)
python scripts/premarket_monitor.py --continuous

# Scan toutes les 15 minutes
python scripts/premarket_monitor.py --continuous --interval 15

# Avec watchlist
python scripts/premarket_monitor.py --watchlist AAPL TSLA --continuous --interval 20
```

### Mode Automatique (Recommandé)

Configurez une tâche planifiée pour exécuter le script automatiquement chaque matin.

#### Windows (Task Scheduler)

1. Ouvrez **Task Scheduler** (Planificateur de tâches)
2. **Create Basic Task** → "Pre-Market Monitor"
3. **Trigger** : Daily, 4:00 AM
4. **Action** : Start a program
   - Program: `python`
   - Arguments: `C:\path\to\ai-stock-dashboard\scripts\premarket_monitor.py --continuous --interval 30`
   - Start in: `C:\path\to\ai-stock-dashboard`
5. **Settings** :
   - ✅ Run whether user is logged on or not
   - ✅ Wake computer to run
   - Stop task if runs longer than: 6 hours

#### Linux/Mac (Cron)

Éditez votre crontab :

```bash
crontab -e
```

Ajoutez cette ligne :

```bash
# Pre-market monitor: Run every 30 minutes from 4:00 AM - 9:30 AM ET, Monday-Friday
*/30 4-9 * * 1-5 cd /path/to/ai-stock-dashboard && /path/to/python scripts/premarket_monitor.py >> logs/premarket.log 2>&1
```

## 📊 Types d'Alertes

### Telegram Alert (Recommandé)
```
🚨 PRE-MARKET ALERT 🚨

📊 AAPL | HIGH
⚡ earnings, quarterly results, Q4

📰 Apple Reports Q4 Earnings Beat, Revenue Up 12%

🔗 MarketWatch
```

### Email Alert
Reçu sur votre email avec :
- Subject: `[HIGH] Pre-Market Alert: AAPL - PREMARKET`
- Corps HTML formaté avec détails complets
- Liens directs vers articles sources

### Desktop Notification
Uniquement pour **CRITICAL** priority pour éviter le spam :
```
🚨 PRE-MARKET: TSLA
merger, acquisition
Tesla announces acquisition of...
```

## ⏰ Heures de Fonctionnement

Le système fonctionne pendant les heures pré-marchés :

- **4:00 AM - 9:30 AM ET** (Eastern Time)
- **Lundi - Vendredi** (jours de marché)
- Détection automatique du fuseau horaire

Conversions selon votre timezone :
- **Paris (CET)** : 10:00 - 15:30
- **London (GMT)** : 09:00 - 14:30
- **Tokyo (JST)** : 18:00 - 23:30 (même jour)

## 🎯 Exemples Réels

### Exemple 1 : Earnings CRITICAL

```bash
# Situation: Apple annonce résultats Q1 avant ouverture
$ python scripts/premarket_monitor.py --watchlist AAPL

🌅 PRE-MARKET SCAN | 2025-01-15 07:30:00 EST
═══════════════════════════════════════════════
📋 Monitoring watchlist: AAPL
🔍 Scanning for pre-market announcements...
🎯 Found 1 new announcements
  • HIGH: 1 announcements
📢 Sending alerts for 1 announcements...
  → AAPL | HIGH | earnings, quarterly
    ✅ Alert sent for AAPL
✓ Sent 1/1 alerts successfully
```

### Exemple 2 : FDA Approval

```bash
# Situation: Small-cap biotech FDA approval
$ python scripts/premarket_monitor.py

🌅 PRE-MARKET SCAN | 2025-01-15 06:00:00 EST
═══════════════════════════════════════════════
📋 Monitoring ALL market
🔍 Scanning for pre-market announcements...
🎯 Found 3 new announcements
  • CRITICAL: 1 announcements
  • HIGH: 2 announcements
📢 Sending alerts for 3 announcements...
  → ABCD | CRITICAL | fda approval
    ✅ Alert sent for ABCD
  → XYZ | HIGH | earnings
    ✅ Alert sent for XYZ
  → DEF | HIGH | guidance, upgrades
    ✅ Alert sent for DEF
✓ Sent 3/3 alerts successfully
```

## 🔧 Configuration Avancée

### Personnaliser les Catalysts

Éditez `modules/news_aggregator.py` :

```python
# Ligne 504: Ajoutez vos propres keywords
catalyst_keywords = [
    'earnings', 'quarterly results',
    # Ajoutez ici:
    'votre keyword personnalisé',
]
```

### Ajuster les Priorités

Éditez `modules/news_aggregator.py`, fonction `_calculate_announcement_priority()` :

```python
# Ligne 604: Personnalisez les priorités
critical_keywords = ['bankruptcy', 'merger', 'fda approval']
high_keywords = ['earnings', 'guidance']
medium_keywords = ['dividend', 'ceo']
```

### Filtrer les Sources

Éditez `config.yaml` :

```yaml
news:
  sources:
    marketwatch: true
    seeking_alpha: true
    yahoo_finance: true
    benzinga: true  # Désactivez les sources non désirées
```

## 🔍 Logs et Debugging

Les logs sont stockés dans `logs/` :

```bash
# Voir les logs du monitoring
tail -f logs/premarket_monitor.log

# Voir les logs des alertes
tail -f logs/alert_manager.log

# Logs généraux de l'application
tail -f logs/app.log
```

Format des logs :

```
2025-01-15 07:30:15 - INFO - 🌅 PRE-MARKET SCAN | 2025-01-15 07:30:00 EST
2025-01-15 07:30:16 - INFO - 🔍 Scanning for pre-market announcements...
2025-01-15 07:30:18 - INFO - 🎯 Found 2 new announcements
2025-01-15 07:30:19 - INFO -   → AAPL | HIGH | earnings, quarterly
2025-01-15 07:30:20 - INFO -     ✅ Alert sent for AAPL
```

## 📈 Sources de Données

Le système agrège automatiquement les news de :

- **MarketWatch** : RSS feed top stories
- **Seeking Alpha** : RSS feed market news
- **Yahoo Finance** : Scraping homepage
- **Benzinga** : RSS feed breaking news

Total : **~100 articles scannés** par scan.

## ⚠️ Limitations

1. **Pas de données temps réel** : Le système scanne les RSS/scraping, délai possible de 5-15 minutes
2. **Extraction de symboles** : Peut rater certains symboles si mal formatés dans le titre
3. **Rate limiting** : Respecte les délais entre requêtes (1-2 secondes)
4. **Faux positifs** : Filtrage par mots-clés peut générer quelques faux positifs

## 💡 Best Practices

### ✅ Recommandations

1. **Utilisez Telegram** : Meilleur canal pour alertes matinales
2. **Watchlist focused** : Surveillez 10-20 actions max pour réduire le bruit
3. **Interval 30 min** : Balance entre réactivité et spam
4. **Test d'abord** : Lancez en mode single scan avant le mode continuous
5. **Vérifiez les logs** : Assurez-vous que les alertes partent correctement

### ❌ À Éviter

1. **Desktop alerts** : Trop de spam, désactivez pour pre-market
2. **Interval < 15 min** : Risk de rate limiting
3. **Pas de watchlist** : Trop d'alertes non pertinentes
4. **Audio alerts** : Sauf si vous êtes déjà réveillé

## 🆘 Troubleshooting

### Aucune alerte reçue

**Cause** : Canal d'alerte non configuré  
**Solution** :
```bash
# Testez vos canaux d'alertes
python tests/test_alerts.py
```

### Trop d'alertes

**Cause** : Pas de watchlist  
**Solution** :
```bash
# Ajoutez une watchlist
python scripts/premarket_monitor.py --watchlist AAPL TSLA MSFT
```

### Symbole "UNKNOWN"

**Cause** : Symbole non détecté dans le titre  
**Solution** : Normal pour certains articles généraux, vérifiez manuellement le lien

### Script ne démarre pas

**Cause** : Dépendances manquantes  
**Solution** :
```bash
pip install -r requirements.txt
pip install pytz  # Si nécessaire
```

## 📚 Ressources

- **[ALERT_SETUP_GUIDE.md](ALERT_SETUP_GUIDE.md)** : Configuration générale des alertes
- **[TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)** : Guide Telegram bot
- **[GMAIL_APP_PASSWORD_GUIDE.md](GMAIL_APP_PASSWORD_GUIDE.md)** : Configuration email

---

## Support

Pour questions ou problèmes :
1. Consultez les logs : `logs/premarket_monitor.log`
2. Testez les alertes : `python tests/test_alerts.py`
3. Vérifiez la configuration : `config.yaml`

**Note** : Le monitoring pré-marché est une **fonctionnalité premium** pour traders sérieux. Utilisez-le de manière responsable et toujours vérifiez les annonces avant de trader.
