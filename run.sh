#!/bin/bash

# 🚀 AI Stock Trading Dashboard - Unified Launcher
# Replace run_dashboard.sh et run_trading_scanner.sh

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║         💎 AI STOCK TRADING DASHBOARD 💎                 ║"
echo "║                                                           ║"
echo "║     Outil Professionnel d'Analyse et Trading             ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Environnement virtuel non trouvé. Création..."
    python3 -m venv venv
    echo "✅ Environnement virtuel créé"
fi

# Activate virtual environment
echo "🔄 Activation de l'environnement virtuel..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Installation des dépendances..."
    pip install -r requirements.txt
    echo "✅ Dépendances installées"
fi

# Create directories
mkdir -p data logs

# Check for config file
if [ ! -f "config.yaml" ]; then
    echo "⚠️  config.yaml not found! Using default configuration."
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Social and alert features may be limited."
    echo "    Copy .env.example to .env and add your API keys."
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  SÉLECTIONNEZ LE MODE:"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  1) 📊 Dashboard Principal (Analyse complète)"
echo "  2) 💎 Scanner de Pépites (Trading signals)"
echo "  3) 🧪 Test du système"
echo "  4) 🔍 Scan Unique + Alertes"
echo "  5) 🤖 Scan Automatique (toutes les 4h)"
echo ""
read -p "Votre choix (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Lancement du dashboard principal..."
        echo "📊 Analyse technique avancée avec ML"
        echo "🌐 URL: http://localhost:8501"
        echo ""
        streamlit run app.py \
            --server.port=8501 \
            --server.address=localhost \
            --server.headless=false \
            --browser.gatherUsageStats=false \
            --theme.base=dark \
            --theme.primaryColor="#00ff88" \
            --theme.backgroundColor="#0e1117" \
            --theme.secondaryBackgroundColor="#262730" \
            --theme.textColor="#fafafa"
        ;;
    2)
        echo ""
        echo "💎 Lancement du scanner de pépites..."
        echo "📊 Détection automatique des meilleures opportunités"
        echo "🌐 URL: http://localhost:8501"
        echo ""
        streamlit run trading_dashboard.py
        ;;
    3)
        echo ""
        echo "🧪 Test du système..."
        python test_system.py
        ;;
    4)
        echo ""
        echo "🔍 Lancement du scan unique..."
        python scripts/auto_scan_opportunities.py
        ;;
    5)
        echo ""
        echo "🤖 Lancement du scanner automatique..."
        echo "⏰ Le scan s'exécutera toutes les 4 heures"
        echo "📢 Les alertes seront envoyées automatiquement"
        echo ""
        python scripts/auto_scan_opportunities.py --schedule
        ;;
    *)
        echo ""
        echo "❌ Choix invalide. Lancement du dashboard principal par défaut..."
        streamlit run app.py
        ;;
esac
