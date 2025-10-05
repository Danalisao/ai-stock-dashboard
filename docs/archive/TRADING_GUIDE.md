# 💎 GUIDE D'UTILISATION - DÉTECTEUR DE PÉPITES

## 🎯 Vue d'Ensemble

Cet outil est un **détecteur automatique de pépites boursières** qui scanne 120+ actions chaque jour pour identifier uniquement les **meilleures opportunités de trading du mois**.

**Ce n'est PAS un outil éducatif. C'est un outil de DÉCISION TRADING.**

---

## 🚀 Démarrage Rapide

### Installation (Une seule fois)

```bash
# 1. Aller dans le dossier
cd ai-stock-dashboard

# 2. Rendre le script exécutable
chmod +x run_trading_scanner.sh

# 3. Lancer
./run_trading_scanner.sh
```

### Lancement Quotidien

```bash
./run_trading_scanner.sh
```

Ensuite, choisissez votre mode:
- **Option 1**: Dashboard interactif (recommandé pour débuter)
- **Option 2**: Scan unique avec alertes
- **Option 3**: Scanner automatique (toutes les 4h)
- **Option 4**: Monitoring temps réel (market hours)

---

## 🔍 Critères de Détection des Pépites

Pour être considérée comme une **pépite**, une action doit répondre à **TOUS** ces critères:

### Critères Obligatoires

| Critère | Valeur | Description |
|---------|--------|-------------|
| **Score Global** | ≥ 85/100 | Score composite basé sur 5 composants |
| **Risk/Reward** | ≥ 2.5 | Minimum 2.5$ de gain pour 1$ de risque |
| **Confiance** | ≥ 70% | Niveau de confiance de l'analyse |
| **Volume** | ≥ 1.3x | Volume supérieur à 1.3x la moyenne |
| **Tous Composants** | ≥ 70/100 | Aucun point faible (trend, momentum, etc.) |
| **Volatilité** | 15-80% | Ni trop calme, ni trop volatile |

### Score Composite (0-100)

Le score est calculé ainsi:

```
Score = (Trend × 30%) + (Momentum × 20%) + (Sentiment × 25%) + 
        (Divergence × 15%) + (Volume × 10%)
```

**Composants:**
- **Trend (30%)**: Alignement SMA 20/50/200, ADX, direction mensuelle
- **Momentum (20%)**: RSI, MACD, ROC
- **Sentiment (25%)**: News (60%) + Social media (40%)
- **Divergence (15%)**: Prix vs RSI/MACD/OBV
- **Volume (10%)**: Trend volume, VWAP, MFI

---

## 📊 Comment Utiliser le Dashboard

### 1. Lancer un Scan

1. Cliquez sur **"🚀 Lancer Scan Complet"** dans la sidebar
2. Attendez 1-2 minutes (le scanner analyse 120+ actions)
3. Les pépites apparaissent automatiquement

### 2. Analyser une Pépite

Pour chaque pépite détectée, vous voyez:

**Informations Principales:**
- 🎯 **Score**: 85-100 (plus c'est haut, mieux c'est)
- 📊 **Recommandation**: STRONG BUY / BUY
- 💪 **Conviction**: HIGH / VERY HIGH

**Paramètres de Trading:**
- 🟢 **Prix d'Entrée**: Prix auquel acheter
- 🎯 **Take Profit**: Objectif de prix (+X%)
- 🛑 **Stop Loss**: Prix de sortie si ça baisse (-X%)
- ⚖️ **Risk/Reward**: Ratio risque/récompense

**Exemple:**
```
Score: 88.5/100
Entrée: $150.00
Take Profit: $187.50 (+25%)
Stop Loss: $141.00 (-6%)
Risk/Reward: 1:4.17
```

### 3. Passer un Trade

#### Option A: Copier/Coller le Plan
1. Cliquez sur "📋 Copier Message"
2. Copiez les paramètres dans votre broker

#### Option B: Configuration Broker
1. **Symbol**: Celui affiché (ex: AAPL)
2. **Entry**: Market order au prix d'entrée
3. **Stop Loss**: Stop order au prix SL
4. **Take Profit**: Limit order au prix TP

#### Option C: Ordre Manuel
```
BUY AAPL
Entry: $150.00
Stop Loss: -6% ($141.00)
Take Profit: +25% ($187.50)
Position: 3-5% du portfolio
```

---

## 📈 Interprétation des Scores

### Score Global

| Score | Signification | Action |
|-------|---------------|--------|
| **90-100** | 🌟 Pépite exceptionnelle | Position 5-10% |
| **85-89** | 💎 Pépite forte | Position 3-5% |
| **80-84** | ✅ Bonne opportunité | Position 1-3% |
| **< 80** | ❌ N'apparaît pas | Ignoré |

### Composants

Chaque composant doit être **≥ 70/100** pour qu'une pépite soit détectée:

- **Trend 70+**: Tendance haussière confirmée
- **Momentum 70+**: Momentum positif
- **Sentiment 70+**: Sentiment positif (news + social)
- **Divergence 70+**: Pas de divergence baissière
- **Volume 70+**: Volume confirmant la tendance

---

## 🚨 Système d'Alertes

### Types d'Alertes

Le système envoie des alertes automatiques pour:

1. **Nouvelle pépite détectée** (Score ≥ 85)
2. **Pépite exceptionnelle** (Score ≥ 90)
3. **Score > 92** = Alerte CRITIQUE

### Canaux d'Alerte

**Desktop** (✅ Activé par défaut)
- Notifications système
- Sons d'alerte

**Email** (Configure dans `.env`)
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=votre@email.com
SENDER_PASSWORD=votre_mot_de_passe_app
RECIPIENT_EMAIL=destination@email.com
```

**Telegram** (Configure dans `.env`)
```bash
TELEGRAM_BOT_TOKEN=votre_bot_token
TELEGRAM_CHAT_ID=votre_chat_id
```

---

## 🤖 Modes de Scan

### Mode 1: Dashboard Interactif (Recommandé)

**Usage:** Analyse visuelle et prise de décision

```bash
./run_trading_scanner.sh
# Choix 1
```

**Avantages:**
- Interface visuelle complète
- Graphiques interactifs
- Analyse détaillée par action
- Export CSV

**Quand l'utiliser:**
- Tous les jours avant le marché
- Pour analyse approfondie
- Pour sélectionner vos trades

---

### Mode 2: Scan Unique

**Usage:** Scan rapide en ligne de commande

```bash
./run_trading_scanner.sh
# Choix 2
```

**Avantages:**
- Rapide (1-2 minutes)
- Résultats en console
- Alertes automatiques
- Sauvegarde CSV

**Quand l'utiliser:**
- Avant l'ouverture du marché
- Pour vérification rapide
- En complément du dashboard

---

### Mode 3: Scanner Automatique

**Usage:** Scan toutes les 4 heures

```bash
./run_trading_scanner.sh
# Choix 3
```

**Fonctionnement:**
- Scan automatique toutes les 4h pendant les heures de marché
- Alertes envoyées uniquement pour NOUVELLES pépites
- Évite les doublons

**Quand l'utiliser:**
- Laisser tourner en arrière-plan
- Pendant votre journée de travail
- Pour ne rien rater

**Horaire de Scan:**
- 9h30 (ouverture)
- 13h30
- 17h30
- Arrêt automatique après clôture

---

### Mode 4: Monitoring Temps Réel

**Usage:** Scan toutes les 15 minutes

```bash
./run_trading_scanner.sh
# Choix 4
```

**Fonctionnement:**
- Scan toutes les 15 min durant market hours
- Alerte immédiate sur nouvelles pépites
- 4 scans par heure

**⚠️ Attention:**
- Consomme plus de ressources
- Peut générer beaucoup d'alertes
- Réservé aux day traders actifs

**Horaire:**
- 9:30am - 4:00pm ET uniquement

---

## 💼 Gestion de Position

### Taille de Position Recommandée

Basé sur le score:

| Score | Position Size | Exemple (10k$) |
|-------|---------------|----------------|
| 90-100 | 5-10% | $500-$1000 |
| 87-89 | 3-5% | $300-$500 |
| 85-86 | 2-3% | $200-$300 |

### Règles de Risk Management

1. **Ne jamais risquer plus de 2% du capital par trade**
   ```
   Capital: $10,000
   Risque max par trade: $200
   ```

2. **Calculer la taille de position selon le Stop Loss**
   ```
   Risque par trade: $200
   Stop Loss: -6%
   Taille position max: $200 / 0.06 = $3,333
   ```

3. **Diversification**
   - Maximum 10 positions ouvertes simultanément
   - Pas plus de 30% dans un secteur

---

## 📝 Workflow Quotidien Recommandé

### Avant Marché (8h-9h30)

1. **Lancer le scan**
   ```bash
   ./run_trading_scanner.sh
   # Choix 1 (Dashboard)
   ```

2. **Analyser les pépites**
   - Vérifier le score (≥ 85)
   - Vérifier le R/R (≥ 2.5)
   - Lire l'analyse détaillée

3. **Sélectionner 2-3 meilleures opportunités**
   - Prioriser score ≥ 90
   - Prioriser R/R ≥ 3.0
   - Vérifier les graphiques

4. **Préparer vos ordres**
   - Entrée: Limit order légèrement sous le prix
   - Stop Loss: Stop order au prix calculé
   - Take Profit: Limit order au prix cible

### Pendant Marché (9h30-16h)

5. **Monitorer vos positions**
   - Vérifier que les ordres sont executés
   - Ajuster si nécessaire

6. **Scanner automatique en arrière-plan** (Optionnel)
   ```bash
   ./run_trading_scanner.sh
   # Choix 3
   ```

### Après Marché (16h-18h)

7. **Bilan de la journée**
   - Vérifier les trades exécutés
   - Noter les résultats
   - Préparer le lendemain

---

## 📊 Exemples de Pépites Réelles

### Exemple 1: Pépite Exceptionnelle

```
🚨 PÉPITE DÉTECTÉE - NVDA 🚨

📊 NVIDIA Corporation
🎯 Score: 92.5/100 - STRONG BUY
💪 Conviction: VERY HIGH

📈 PARAMÈTRES DE TRADING:
• Prix actuel: $475.50
• 🟢 Entrée: $475.50
• 🎯 Take Profit: $594.38 (+25%)
• 🛑 Stop Loss: $446.97 (-6%)
• ⚖️ Risk/Reward: 1:4.17

📊 ANALYSE:
• Trend: 95/100
• Momentum: 92/100
• Sentiment: 88/100
• Volume: 2.3x normal
• Volatilité: 45%

💼 POSITION:
• Taille recommandée: 5-10% portfolio
• Confiance: 87%
```

**Action à Prendre:**
1. Acheter NVDA à $475.50
2. Stop Loss à $446.97 (-6%)
3. Take Profit à $594.38 (+25%)
4. Position: 5-10% du portfolio

---

### Exemple 2: Pépite Forte

```
🚨 PÉPITE DÉTECTÉE - AAPL 🚨

📊 Apple Inc.
🎯 Score: 86.2/100 - STRONG BUY
💪 Conviction: HIGH

📈 PARAMÈTRES DE TRADING:
• Prix actuel: $178.25
• 🟢 Entrée: $178.25
• 🎯 Take Profit: $222.81 (+25%)
• 🛑 Stop Loss: $160.39 (-10%)
• ⚖️ Risk/Reward: 1:2.50

💼 POSITION:
• Taille recommandée: 3-5% portfolio
```

**Action à Prendre:**
1. Acheter AAPL à $178.25
2. Stop Loss à $160.39 (-10%)
3. Take Profit à $222.81 (+25%)
4. Position: 3-5% du portfolio

---

## ⚠️ Avertissements Importants

### 🚨 RISQUES

1. **Trading = Risque de Perte**
   - Vous pouvez perdre de l'argent
   - Ne tradez que ce que vous pouvez perdre
   - Utilisez TOUJOURS un Stop Loss

2. **Pas de Garantie**
   - Les signaux ne garantissent aucun profit
   - Performances passées ≠ résultats futurs
   - Faites votre propre analyse

3. **Responsabilité**
   - Vous êtes seul responsable de vos trades
   - Cet outil est une aide à la décision
   - Consultez un conseiller financier si nécessaire

### ✅ Bonnes Pratiques

1. **Commencer Petit**
   - Testez avec de petites positions
   - Augmentez progressivement
   - Ne risquez jamais plus de 2% par trade

2. **Tenir un Journal**
   - Notez tous vos trades
   - Analysez vos erreurs
   - Améliorez votre stratégie

3. **Respecter les Stops**
   - Ne JAMAIS déplacer un Stop Loss
   - Couper les pertes rapidement
   - Laisser courir les profits

---

## 🔧 Configuration Avancée

### Activer les Alertes Email

1. Éditer `.env`:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=votre@gmail.com
SENDER_PASSWORD=votre_mot_de_passe_app
RECIPIENT_EMAIL=votre@email.com
```

2. Éditer `config.yaml`:
```yaml
alerts:
  channels:
    email: true
```

### Activer Telegram

1. Créer un bot Telegram (@BotFather)
2. Obtenir le token et chat_id
3. Éditer `.env`:
```bash
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=123456789
```

4. Éditer `config.yaml`:
```yaml
alerts:
  channels:
    telegram: true
```

---

## 📞 Support & Troubleshooting

### Problèmes Courants

**❌ "Module not found"**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**❌ "No opportunities found"**
- Normal si le marché est en consolidation
- Essayez à un autre moment
- Ajustez les filtres dans la sidebar

**❌ Scan trop lent**
- Normal pour 120+ actions
- Patience: 1-2 minutes
- Réduisez le nombre d'actions dans `opportunity_scanner.py`

### Logs

Les logs sont dans `logs/dashboard.log`:
```bash
tail -f logs/dashboard.log
```

---

## 🎯 Objectif de l'Outil

**Détecter uniquement les MEILLEURES opportunités du mois.**

Vous ne verrez PAS:
- ❌ Toutes les actions du marché
- ❌ Des signaux moyens (score < 85)
- ❌ Des opportunités risquées (R/R < 2.5)
- ❌ Des actions sans confirmation

Vous verrez UNIQUEMENT:
- ✅ Les pépites (score ≥ 85)
- ✅ Excellents ratios R/R (≥ 2.5)
- ✅ Volume confirmé (≥ 1.3x)
- ✅ Tous indicateurs alignés

**C'est un filtre ultra-strict pour ne garder que le meilleur.**

---

## 📚 Ressources

- **Dashboard**: `./run_trading_scanner.sh` → Choix 1
- **Configuration**: `config.yaml`
- **Logs**: `logs/dashboard.log`
- **Exports**: `data/opportunities_*.csv`
- **Documentation technique**: `README_NEW.md`

---

**Bon trading! 💎📈**

*N'oubliez pas: La patience et la discipline sont les clés du succès en trading.*
