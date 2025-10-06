# 💬 Reddit API Integration - Social Sentiment Analysis

## Overview

L'application utilise l'**API Reddit (PRAW)** pour collecter et analyser les discussions sur les actions à partir de subreddits populaires comme r/wallstreetbets, r/stocks et r/investing.

## 🚀 Fonctionnalités Social Media

### 1. Reddit Mentions Tracking
Collecte automatique des mentions sur Reddit :
- 💬 **Subreddits surveillés** : r/stocks, r/investing, r/wallstreetbets
- 🔍 **Détection de symboles** : Recherche de mentions ($AAPL, TSLA, etc.)
- 📊 **Score d'engagement** : Upvotes, commentaires, activité
- 📈 **Analyse de tendances** : Détection de spikes d'activité
- ⏱️ **Données temps réel** : Dernières 24h à 30 jours
- 🎯 **Top posts** : Posts les plus populaires par symbole

### 2. Social Sentiment Analysis
Analyse du sentiment social :
- 💎 **Sentiment Score** : Basé sur upvotes et engagement
- 🗣️ **Buzz Level** : low/medium/high/very_high
- 📊 **Confidence** : Score de confiance basé sur le volume
- ⚡ **Unusual Activity** : Détection d'activité inhabituelle (spikes 3x+)
- 📈 **Trending Tickers** : Actions les plus mentionnées

### 3. Intégration Dashboard
Les données Reddit sont intégrées :
- **📊 Company Info Tab** : Social sentiment dans l'analyse
- **🔔 Alert System** : Alertes sur spikes d'activité sociale
- **📈 Monthly Score** : Le sentiment social contribue au score global
- **🤖 Daily Update** : Mise à jour automatique du sentiment

### 4. Données Collectées
Pour chaque mention :
- Platform, subreddit, type (submission/comment)
- Title, content (500 premiers caractères)
- Author, URL, score
- Number of comments
- Posted date, fetched timestamp

---

## Configuration

### Étape 1: Créer une Application Reddit

1. Allez sur [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Connectez-vous avec votre compte Reddit
3. Faites défiler vers le bas et cliquez sur **"create another app..."**

### Étape 2: Remplir le Formulaire

**Configurez votre application** :
- **name** : `StockAnalyse` (ou votre choix)
- **App type** : Sélectionnez **"script"** (personnel use script)
- **description** : (optionnel) `Stock market social sentiment analysis`
- **about url** : (optionnel, peut être votre GitHub ou profil)
- **redirect uri** : `http://localhost:8080` (requis même si non utilisé)

4. Cliquez sur **"create app"**

### Étape 3: Récupérer les Credentials

Une fois l'app créée, vous verrez :

```
personal use script
[CLIENT_ID]          ← Code sous "personal use script" (14 caractères)

secret
[CLIENT_SECRET]      ← Clé secrète (27 caractères)
```

**Important** : 
- Le `CLIENT_ID` est le code sous "personal use script"
- Le `CLIENT_SECRET` est marqué "secret"

### Étape 4: Configurer le Fichier .env

Ouvrez le fichier `.env` à la racine du projet et ajoutez :

```bash
# Reddit API Configuration
REDDIT_CLIENT_ID=votre_client_id_ici
REDDIT_CLIENT_SECRET=votre_client_secret_ici
REDDIT_USER_AGENT=StockAnalyse/1.0
```

**Exemple réel** :
```bash
REDDIT_CLIENT_ID=RyB_bJEBH0Az5mMY1ep4H1_ZxMQJw
REDDIT_CLIENT_SECRET=dE3_fG7hK9lMnP2qR4sT6vW8xY0zA
REDDIT_USER_AGENT=StockAnalyse/1.0
```

### Étape 5: Vérifier la Configuration

Ouvrez le fichier `config.yaml` et vérifiez que Reddit est activé :

```yaml
news:
  sources:
    yahoo_finance: true
    finviz: true
    reddit: true          # ← Doit être true
  
  # Subreddits à surveiller
  reddit_subs:
    - stocks
    - investing
    - wallstreetbets
```

---

## Utilisation

### Dans l'Application

Une fois configuré, Reddit s'intègre automatiquement :

1. **Company Info Tab** :
   - Section "Social Sentiment" avec données Reddit
   - Mentions totales, average score, buzz level
   - Top posts les plus populaires

2. **Alertes Automatiques** :
   - Détection de spikes d'activité (3x+ baseline)
   - Notifications par email si configuré

3. **Daily Update Script** :
   ```bash
   python scripts/daily_update.py
   ```
   Met à jour automatiquement le sentiment social

### Fonctions Disponibles

```python
from modules.social_aggregator import SocialAggregator

social = SocialAggregator(config)

# Récupérer les mentions
mentions = social.fetch_reddit_mentions('AAPL', days=7)

# Calculer le sentiment
sentiment = social.calculate_social_sentiment(mentions)

# Trending tickers
trending = social.get_trending_tickers('wallstreetbets', limit=10)

# Détecter activité inhabituelle
activity = social.detect_unusual_activity('TSLA')
```

---

## Limites de l'API

### Reddit API Rate Limits
- **60 requêtes/minute** sans authentification OAuth
- **600 requêtes/10 minutes** avec script app
- Gestion automatique des rate limits dans le code

### Configuration Rate Limiting

Dans `config.yaml` :
```yaml
rate_limits:
  reddit_requests_per_minute: 60
```

---

## Dépannage

### Erreur : "Reddit API credentials not found"
**Cause** : Variables d'environnement non configurées  
**Solution** : Vérifiez que `.env` contient `REDDIT_CLIENT_ID` et `REDDIT_CLIENT_SECRET`

### Erreur : "401 Unauthorized"
**Cause** : Credentials invalides  
**Solution** : 
1. Vérifiez que vous avez copié le bon CLIENT_ID (sous "personal use script")
2. Régénérez le SECRET si nécessaire sur Reddit Apps

### Erreur : "429 Too Many Requests"
**Cause** : Rate limit dépassé  
**Solution** : Le code attend automatiquement, mais vous pouvez réduire la fréquence des scans

### Pas de données récupérées
**Cause** : Subreddit ou symbole sans mentions récentes  
**Solution** : 
1. Essayez avec des actions populaires (AAPL, TSLA, GME)
2. Augmentez la période (days=30)
3. Vérifiez les logs pour plus de détails

---

## Sécurité

### Bonnes Pratiques

✅ **À FAIRE** :
- Gardez `.env` privé (déjà dans `.gitignore`)
- Ne partagez JAMAIS vos credentials
- Utilisez `REDDIT_USER_AGENT` unique et descriptif
- Régénérez les secrets si compromis

❌ **À NE PAS FAIRE** :
- Commit `.env` dans Git
- Hardcoder les credentials dans le code
- Partager vos credentials publiquement
- Utiliser un user agent générique

---

## Ressources

- 📚 [PRAW Documentation](https://praw.readthedocs.io/)
- 🔑 [Reddit Apps Management](https://www.reddit.com/prefs/apps)
- 📖 [Reddit API Wiki](https://github.com/reddit-archive/reddit/wiki/API)
- 💬 [r/redditdev](https://www.reddit.com/r/redditdev/) - Support communautaire

---

## Support

Pour toute question ou problème :
1. Consultez les logs : `logs/app.log`
2. Vérifiez la configuration : `config.yaml`
3. Testez avec : `python tests/test_api_keys.py`

**Note** : L'intégration Reddit est **optionnelle**. Si non configurée, l'application fonctionnera normalement sans les données sociales.
