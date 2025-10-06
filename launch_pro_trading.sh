#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
#    PROFESSIONAL TRADER LAUNCHER - Linux/Mac
# ═══════════════════════════════════════════════════════════════════════
#    Lancement rapide du système de trading professionnel
# ═══════════════════════════════════════════════════════════════════════

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Header
echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                                                                   ║"
echo "║        🚀 PROFESSIONAL TRADER PLATFORM - LAUNCHER 🚀             ║"
echo "║                                                                   ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Démarrage du système professionnel de trading...${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ ERREUR: Python 3 n'est pas installé${NC}"
    echo ""
    echo "Installez Python 3.9+ :"
    echo "  • Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  • macOS: brew install python3"
    exit 1
fi

echo -e "${GREEN}✅ Python détecté${NC}"
echo ""

# Function to check if process is running
check_process() {
    pgrep -f "$1" > /dev/null 2>&1
}

# Function to start monitor in background
start_monitor() {
    local script="$1"
    shift
    local args="$@"
    
    nohup python3 "scripts/${script}" $args > "logs/$(basename ${script} .py).log" 2>&1 &
    echo -e "${GREEN}✅ Monitor lancé (PID: $!)${NC}"
    echo -e "${CYAN}Logs: logs/$(basename ${script} .py).log${NC}"
}

# Function to stop monitors
stop_monitors() {
    echo ""
    echo -e "${YELLOW}Arrêt de tous les monitors...${NC}"
    
    pkill -f "pro_trader_monitor.py" 2>/dev/null && echo "  ✓ Pro Trader Monitor arrêté" || true
    pkill -f "premarket_monitor.py" 2>/dev/null && echo "  ✓ Premarket Monitor arrêté" || true
    pkill -f "realtime_monitor.py" 2>/dev/null && echo "  ✓ Realtime Monitor arrêté" || true
    
    echo -e "${GREEN}✅ Tous les monitors arrêtés${NC}"
}

# Function to check monitor status
check_status() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  📊 STATUS DES MONITORS"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    
    if check_process "pro_trader_monitor.py"; then
        echo -e "  Pro Trader Monitor:  ${GREEN}● ONLINE${NC}"
    else
        echo -e "  Pro Trader Monitor:  ${RED}● OFFLINE${NC}"
    fi
    
    if check_process "premarket_monitor.py"; then
        echo -e "  Premarket Monitor:   ${GREEN}● ONLINE${NC}"
    else
        echo -e "  Premarket Monitor:   ${RED}● OFFLINE${NC}"
    fi
    
    if check_process "realtime_monitor.py"; then
        echo -e "  Realtime Monitor:    ${GREEN}● ONLINE${NC}"
    else
        echo -e "  Realtime Monitor:    ${RED}● OFFLINE${NC}"
    fi
    
    echo ""
}

# Main menu
show_menu() {
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║                    CHOISISSEZ VOTRE MODE                          ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "   1. 🎛️  Control Center (Dashboard de contrôle - RECOMMANDÉ)"
    echo "   2. 🚀 Pro Trader Monitor (24/7 - Mode standard)"
    echo "   3. 🔥 Pro Trader Monitor (24/7 - Mode agressif)"
    echo "   4. 🌅 Premarket Monitor (4h-9h30 AM ET uniquement)"
    echo "   5. 📊 Dashboard Principal (Analyse et signaux)"
    echo "   6. 📡 Voir le status des monitors"
    echo "   7. ❌ Arrêter tous les monitors"
    echo "   8. 🧪 Test des alertes"
    echo "   9. ℹ️  Documentation"
    echo "  10. 🚪 Quitter"
    echo ""
    read -p "Votre choix (1-10): " choice
    
    case $choice in
        1) control_center ;;
        2) pro_monitor_standard ;;
        3) pro_monitor_aggressive ;;
        4) premarket_monitor ;;
        5) main_dashboard ;;
        6) check_status; pause_menu ;;
        7) stop_monitors; pause_menu ;;
        8) test_alerts; pause_menu ;;
        9) documentation; pause_menu ;;
        10) quit_launcher ;;
        *) 
            echo -e "${RED}❌ Choix invalide${NC}"
            sleep 2
            show_menu
            ;;
    esac
}

control_center() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  🎛️  LANCEMENT DU CONTROL CENTER"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "Le Control Center va s'ouvrir dans votre navigateur..."
    echo "Utilisez-le pour:"
    echo "  - Démarrer/arrêter les monitors"
    echo "  - Voir les alertes en temps réel"
    echo "  - Configurer les canaux d'alerte"
    echo "  - Consulter les statistiques"
    echo ""
    echo -e "${YELLOW}Appuyez sur Ctrl+C pour arrêter le Control Center${NC}"
    echo ""
    streamlit run scripts/control_center.py
}

pro_monitor_standard() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  🚀 LANCEMENT DU PRO TRADER MONITOR - MODE STANDARD"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "Fonctionnalités:"
    echo "  ✅ Monitoring 24/7"
    echo "  ✅ Détection prémarché (4h-9h30 AM ET)"
    echo "  ✅ Pump stocks (5%+ | 2.0x volume)"
    echo "  ✅ AI Discovery (Gemini)"
    echo "  ✅ Alertes multi-canaux"
    echo ""
    
    start_monitor "pro_trader_monitor.py"
    
    echo ""
    echo -e "${GREEN}Le monitor tourne en arrière-plan${NC}"
    echo -e "${CYAN}Vérifiez Telegram pour les alertes !${NC}"
    echo ""
    
    pause_menu
}

pro_monitor_aggressive() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  🔥 LANCEMENT DU PRO TRADER MONITOR - MODE AGRESSIF"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo -e "${YELLOW}⚠️  MODE AGRESSIF ACTIVÉ${NC}"
    echo ""
    echo "Différences vs mode standard:"
    echo "  • Seuil prix: 3% (au lieu de 5%)"
    echo "  • Seuil volume: 1.5x (au lieu de 2.0x)"
    echo "  • Scans plus fréquents (1 min vs 3 min)"
    echo ""
    echo -e "${YELLOW}⚡ ATTENTION: Plus d'alertes (risque de sur-notification)${NC}"
    echo ""
    
    start_monitor "pro_trader_monitor.py" "--aggressive"
    
    echo ""
    pause_menu
}

premarket_monitor() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  🌅 LANCEMENT DU PREMARKET MONITOR"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "Détection de catalyseurs prémarché:"
    echo "  • Earnings (résultats trimestriels)"
    echo "  • FDA approvals (médicaments)"
    echo "  • M&A (fusions/acquisitions)"
    echo "  • Guidance (révisions)"
    echo ""
    echo "Actif: 4h00 - 9h30 AM ET (heure New York)"
    echo "Scan: Toutes les 15 minutes"
    echo ""
    
    start_monitor "pro_trader_monitor.py" "--premarket-only"
    
    echo ""
    pause_menu
}

main_dashboard() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  📊 LANCEMENT DU DASHBOARD PRINCIPAL"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "Le dashboard va s'ouvrir dans votre navigateur..."
    echo ""
    echo "Fonctionnalités:"
    echo "  • 🎯 AI-Discovered Opportunities"
    echo "  • 🚨 Monthly Signals (Score 0-100)"
    echo "  • 📰 News & Sentiment"
    echo "  • 📈 Technical Analysis"
    echo "  • 💼 Portfolio Tracking"
    echo "  • 🔙 Backtesting"
    echo ""
    streamlit run app.py
}

test_alerts() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  🧪 TEST DES ALERTES"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "Test des canaux d'alerte configurés..."
    echo ""
    
    python3 << EOF
from modules.alert_manager import AlertManager
from modules.utils import load_config

am = AlertManager(load_config())
results = am.test_alerts()

print("\n🔔 RÉSULTATS DES TESTS:\n")
for channel, success in results.items():
    status = "✅ OK" if success else "❌ FAILED"
    print(f"  {channel.upper()}: {status}")
EOF

    echo ""
    echo "Si un test échoue, vérifiez votre fichier .env"
    echo "Documentation: docs/PRO_TRADER_SETUP.md"
    echo ""
}

documentation() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  ℹ️  DOCUMENTATION"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "Documentation disponible:"
    echo ""
    echo "  📖 README.md                         - Vue d'ensemble"
    echo "  🚀 docs/PRO_TRADER_SETUP.md          - Setup professionnel"
    echo "  🔔 docs/ALERT_SETUP_GUIDE.md         - Configuration alertes"
    echo "  🤖 docs/GEMINI_SETUP.md              - Configuration Gemini AI"
    echo "  🌅 docs/PREMARKET_ALERTS_GUIDE.md    - Guide prémarché"
    echo ""
    
    # Open documentation (macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        read -p "Ouvrir la documentation professionnelle ? (o/n) " open_doc
        if [[ "$open_doc" == "o" || "$open_doc" == "O" ]]; then
            open docs/PRO_TRADER_SETUP.md
        fi
    fi
    
    # Open documentation (Linux with xdg-open)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        read -p "Ouvrir la documentation professionnelle ? (o/n) " open_doc
        if [[ "$open_doc" == "o" || "$open_doc" == "O" ]]; then
            xdg-open docs/PRO_TRADER_SETUP.md 2>/dev/null || cat docs/PRO_TRADER_SETUP.md | less
        fi
    fi
    
    echo ""
}

pause_menu() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    read -p "Appuyez sur Entrée pour revenir au menu principal..."
    show_menu
}

quit_launcher() {
    echo ""
    echo "Au revoir ! Bon trading 🚀💰"
    echo ""
    exit 0
}

# Start
show_menu
