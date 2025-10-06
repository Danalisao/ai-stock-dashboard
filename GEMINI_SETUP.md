# 🤖 Google Gemini AI Integration

## Overview

L'application utilise **Google Gemini Flash 2.5** pour analyser l'actualité financière et identifier automatiquement l'action la plus tendance du moment.

## Fonctionnalités AI

### 1. Stock Trending Analysis
À l'ouverture de l'application, Gemini analyse automatiquement :
- ✅ Toutes les actualités récentes de votre watchlist
- ✅ Fréquence des mentions par action
- ✅ Importance des news (earnings, produits, régulation, etc.)
- ✅ Sentiment du marché (bullish/neutral/bearish)
- ✅ Impact potentiel sur le prix

### 2. Affichage Banner
Un banner en haut de l'application affiche :
- 🚀 **Action Tendance** : Le symbole identifié
- 🎯 **Confidence** : Score de confiance AI (0-100%)
- 📰 **Mentions** : Nombre d'articles
- 💹 **Sentiment** : Bullish/Neutral/Bearish
- 🤖 **Source** : gemini-2.0-flash-exp ou fallback

### 3. Fallback Mode
Si Gemini n'est pas configuré, un système de fallback compte simplement les mentions.

---

## Configuration

### Étape 1: Obtenir une clé API Gemini

1. Allez sur [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Connectez-vous avec votre compte Google
3. Cliquez sur "Create API Key"
4. Copiez la clé générée (format: `AIzaSy...`)

**Note :** Gemini Flash 2.5 est **gratuit** jusqu'à 1500 requêtes/jour !

### Étape 2: Configurer l'environnement

#### Option A: Fichier .env (Recommandé)

```bash
# Copiez .env.example vers .env
cp .env.example .env

# Éditez .env et ajoutez votre clé
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXX
```

#### Option B: Variable d'environnement

**Windows:**
```powershell
$env:GEMINI_API_KEY="AIzaSyXXXXXXXXXXXXXXXXXXXXXX"
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="AIzaSyXXXXXXXXXXXXXXXXXXXXXX"
```

### Étape 3: Redémarrer l'application

```bash
streamlit run app.py
```

---

## Utilisation

### Banner AI Trending Stock

Au démarrage, l'application :
1. Récupère les news des 20 premières actions de la watchlist
2. Envoie tout à Gemini Flash 2.5 pour analyse
3. Affiche l'action la plus tendance dans un banner coloré
4. Cache le résultat pendant 1 heure

### Actions Disponibles

**📊 Analyze {SYMBOL}** - Analyse immédiate de l'action tendance  
**🔄 Refresh AI Analysis** - Force une nouvelle analyse Gemini

### Mise à jour

- ⏱️ **Auto-refresh** : Toutes les 60 minutes
- 🔄 **Manuel** : Bouton "Refresh AI Analysis"
- 💾 **Cache** : Stocké dans `st.session_state`

---

## Exemple de Résultat

```markdown
🚀 AI Trending Stock: AAPL

Apple dominates today's financial news with 23 mentions across major outlets. 
Strong earnings beat and new product launch driving positive sentiment.

🎯 Confidence: 87%
📰 Mentions: 23
💹 Sentiment: BULLISH
🤖 Source: gemini-2.0-flash-exp
```

---

## Limites & Quotas

### Google Gemini Flash 2.5 (Gratuit)

| Métrique | Limite |
|----------|--------|
| Requêtes/jour | 1500 |
| Requêtes/minute | 15 |
| Tokens/requête | 32,000 input / 8,000 output |
| Coût | **GRATUIT** |

### Optimisations Implémentées

- ✅ Cache de 60 minutes pour éviter les requêtes répétées
- ✅ Limite à 20 stocks de la watchlist
- ✅ 5 articles max par stock
- ✅ Fallback automatique si quota dépassé

---

## Troubleshooting

### "Gemini API key not found"

**Cause :** Variable d'environnement non configurée

**Solution :**
```bash
# Vérifiez que .env existe et contient la clé
cat .env | grep GEMINI_API_KEY

# Ou définissez manuellement
export GEMINI_API_KEY="your_key_here"
```

### "API quota exceeded"

**Cause :** Limite de 1500 requêtes/jour dépassée

**Solution :**
- Attendez 24h pour reset
- Ou créez une nouvelle clé API
- Le fallback s'active automatiquement

### "Connection timeout"

**Cause :** Problème réseau ou firewall

**Solution :**
```bash
# Testez la connexion
curl https://generativelanguage.googleapis.com
```

### Banner ne s'affiche pas

**Cause :** Pas de news récentes ou watchlist vide

**Solution :**
- Vérifiez que votre watchlist contient des symboles
- Attendez quelques minutes (agrégation news en cours)

---

## Sécurité

### ⚠️ Bonnes Pratiques

1. **Jamais commit .env** ✅ (déjà dans .gitignore)
2. **Clé API secrète** - Ne la partagez jamais
3. **Rotation** - Régénérez si exposée
4. **Quotas** - Surveillez votre usage sur AI Studio

### Révocation

Si votre clé est compromise :
1. Allez sur [AI Studio](https://aistudio.google.com/app/apikey)
2. Cliquez sur "Delete" à côté de la clé
3. Créez une nouvelle clé
4. Mettez à jour `.env`

---

## Architecture Technique

```
┌─────────────────┐
│   Streamlit     │
│   Dashboard     │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Gemini  │  ← modules/gemini_analyzer.py
    │Analyzer │
    └────┬────┘
         │
    ┌────▼──────────┐
    │ Google Gemini │  ← gemini-2.0-flash-exp
    │  Flash 2.5    │
    └────┬──────────┘
         │
    [Analyse AI]
         │
    ┌────▼────┐
    │ Résultat│  → Trending stock + sentiment + reasoning
    └─────────┘
```

---

## Développement

### Test de l'intégration

```python
# Test rapide dans Python
from modules.gemini_analyzer import GeminiAnalyzer
import os

os.environ['GEMINI_API_KEY'] = 'your_key'
analyzer = GeminiAnalyzer()

# Test fallback
result = analyzer._fallback_analysis([], ['AAPL', 'MSFT'])
print(result)
```

### Personnalisation du prompt

Éditez `modules/gemini_analyzer.py`, méthode `analyze_trending_stock()` :

```python
prompt = f"""Votre prompt personnalisé ici...

WATCHLIST: {', '.join(watchlist)}
NEWS: {news_text}

Répondez en JSON...
"""
```

---

## Roadmap AI

- [ ] Sentiment analysis par action (en plus du trending)
- [ ] Prédiction de mouvement de prix avec Gemini
- [ ] Résumé quotidien du marché généré par AI
- [ ] Alertes intelligentes basées sur l'analyse AI
- [ ] Multi-langue (FR/EN) selon préférence utilisateur

---

**Version :** 2.0  
**Modèle :** gemini-2.0-flash-exp  
**Coût :** Gratuit (1500 req/jour)  
**Status :** ✅ Production Ready
