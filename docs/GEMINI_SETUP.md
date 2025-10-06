# 🤖 Google Gemini AI Integration - Explosive Opportunity Discovery

## Overview

L'application utilise **Google Gemini Flash 2.5** pour scanner **TOUT LE MARCHÉ** et identifier automatiquement l'action avec le **PLUS HAUT POTENTIEL EXPLOSIF** dans les 7-30 prochains jours.

## 🚀 Fonctionnalités AI - Market-Wide Discovery

### 1. Explosive Opportunity Scanning
À l'ouverture de l'application, Gemini analyse **100+ articles** de sources multiples :
- 📰 **MarketWatch, Seeking Alpha, Yahoo Finance, Benzinga**
- 🔍 **Détection intelligente de symboles** (même non-explicites)
- ⚡ **Identification de catalyseurs explosifs** (earnings, FDA, M&A, produits)
- 📈 **Analyse de momentum et sentiment surge**
- 💎 **Score de potentiel explosif** (0-100% confidence)
- ⏱️ **Timeframe estimé** pour l'explosion
- 🎯 **Niveau de risque** (low/medium/high)

### 2. Affichage Banner - Explosive Opportunity
Un banner premium en haut de l'application affiche :
- 💎 **Action à Potentiel Explosif** : Symbole identifié (n'importe quelle action du marché)
- 🎯 **Confidence** : Score de confiance AI (0-100%)
- ⚡ **Catalyseurs** : Événements spécifiques qui vont provoquer l'explosion
- 📰 **Articles** : Nombre d'articles analysés
- 💹 **Sentiment** : Bullish/Neutral/Bearish
- ⏱️ **Timeframe** : Estimation 7-30 jours
- 🎯 **Risk Level** : Niveau de risque évalué par AI
- 🤖 **Source** : gemini-2.0-flash-exp

### 3. Actions Rapides
- **📊 Deep Analysis** - Analyse complète immédiate de l'action
- **➕ Add to Watchlist** - Ajout automatique à votre liste
- **🔄 Refresh** - Force une nouvelle scan du marché

### 4. Intelligence Avancée
L'AI ne se limite **PAS** à votre watchlist :
- ✅ **Scan universel** : Analyse TOUT le marché (pas de restrictions)
- ✅ **Extraction intelligente** : Détecte les symboles même non-mentionnés explicitement
- ✅ **Priorisation dynamique** : Favorise votre watchlist si pertinent
- ✅ **Fallback automatique** : Système de secours si Gemini indisponible

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

## 🎯 Exemple de Résultat

### Scénario 1: High Explosive Potential
```markdown
💎 HIGH EXPLOSIVE POTENTIAL: NVDA                           [RISK: MEDIUM]

NVIDIA poised for explosive growth with new AI chip launch announcement 
generating massive buzz. Multiple analyst upgrades and partnership with 
major cloud providers signal significant revenue expansion incoming.

⚡ Catalysts: AI chip launch • Cloud partnerships • Analyst upgrades

🎯 Confidence: 89%
📰 Articles: 34
💹 Sentiment: BULLISH
⏱️ Timeframe: 7-14 days
🤖 Source: gemini-2.0-flash-exp

[📊 Deep Analysis NVDA] [➕ Add NVDA to Watchlist] [🔄 Refresh]
```

### Scénario 2: Strong Opportunity
```markdown
🚀 STRONG OPPORTUNITY: MRNA                                 [RISK: HIGH]

Moderna's Phase 3 trial results exceed expectations. FDA fast-track 
approval anticipated within 30 days. High volatility expected.

⚡ Catalysts: FDA approval • Trial success • Market expansion

🎯 Confidence: 72%
📰 Articles: 18
💹 Sentiment: BULLISH
⏱️ Timeframe: 14-30 days
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

- ✅ **Cache de 60 minutes** pour éviter les requêtes répétées
- ✅ **100 articles généraux** du marché entier (pas limité à watchlist)
- ✅ **4 sources premium** : MarketWatch, Seeking Alpha, Yahoo, Benzinga
- ✅ **Fallback intelligent** si quota dépassé
- ✅ **Extraction multi-symboles** : Détecte tous les tickers mentionnés
- ✅ **Priorisation optionnelle** de votre watchlist

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

## 🎯 Critères d'Analyse Explosive

Gemini évalue chaque action selon 5 critères :

1. **⚡ Catalysts** - Événements déclencheurs (earnings, FDA, M&A, produits)
2. **📈 Momentum** - Articles multiples, upgrades analystes, price action
3. **💰 Market Impact** - Annonces de revenus/croissance significatives
4. **🔥 Sentiment Surge** - Tone bullish, excitement, breakthrough news
5. **🎯 Timing** - Événements récents/imminents (pas old news)

## Roadmap AI

- [x] **Market-wide explosive opportunity detection** ✅
- [x] **Multi-source news aggregation** (4 sources premium) ✅
- [x] **Risk level assessment** ✅
- [ ] Sentiment analysis temps-réel par action
- [ ] Prédiction de mouvement de prix intraday avec Gemini
- [ ] Résumé quotidien personnalisé du marché
- [ ] Alertes intelligentes push notifications
- [ ] Multi-langue (FR/EN) selon préférence utilisateur
- [ ] Backtesting AI predictions pour améliorer accuracy

---

**Version :** 2.5  
**Modèle :** gemini-2.5-flash  
**Coût :** Gratuit (1500 req/jour)  
**Status :** ✅ Production Ready
