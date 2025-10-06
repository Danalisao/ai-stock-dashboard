@echo off
REM ═══════════════════════════════════════════════════════════════════════
REM    PROFESSIONAL TRADER LAUNCHER - Windows
REM ═══════════════════════════════════════════════════════════════════════
REM    Lancement rapide du système de trading professionnel
REM ═══════════════════════════════════════════════════════════════════════

echo.
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║                                                                   ║
echo ║        🚀 PROFESSIONAL TRADER PLATFORM - LAUNCHER 🚀             ║
echo ║                                                                   ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.
echo Démarrage du système professionnel de trading...
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERREUR: Python n'est pas installé ou pas dans PATH
    echo.
    echo Installez Python 3.9+ depuis: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python détecté
echo.

REM Menu de sélection
echo ╔═══════════════════════════════════════════════════════════════════╗
echo ║                    CHOISISSEZ VOTRE MODE                          ║
echo ╚═══════════════════════════════════════════════════════════════════╝
echo.
echo   1. 🎛️  Control Center (Dashboard de contrôle - RECOMMANDÉ)
echo   2. 🚀 Pro Trader Monitor (24/7 - Mode standard)
echo   3. 🔥 Pro Trader Monitor (24/7 - Mode agressif)
echo   4. 🌅 Premarket Monitor (4h-9h30 AM ET uniquement)
echo   5. 📊 Dashboard Principal (Analyse et signaux)
echo   6. ❌ Arrêter tous les monitors
echo   7. 🧪 Test des alertes
echo   8. ℹ️  Documentation
echo   9. 🚪 Quitter
echo.
set /p choice="Votre choix (1-9): "

if "%choice%"=="1" goto control_center
if "%choice%"=="2" goto pro_monitor_standard
if "%choice%"=="3" goto pro_monitor_aggressive
if "%choice%"=="4" goto premarket_monitor
if "%choice%"=="5" goto main_dashboard
if "%choice%"=="6" goto stop_monitors
if "%choice%"=="7" goto test_alerts
if "%choice%"=="8" goto documentation
if "%choice%"=="9" goto quit

echo.
echo ❌ Choix invalide. Veuillez choisir entre 1 et 9.
pause
exit /b 1

:control_center
echo.
echo ═══════════════════════════════════════════════════════════════════
echo  🎛️  LANCEMENT DU CONTROL CENTER
echo ═══════════════════════════════════════════════════════════════════
echo.
echo Le Control Center va s'ouvrir dans votre navigateur...
echo Utilisez-le pour:
echo   - Démarrer/arrêter les monitors
echo   - Voir les alertes en temps réel
echo   - Configurer les canaux d'alerte
echo   - Consulter les statistiques
echo.
echo Appuyez sur Ctrl+C pour arrêter le Control Center
echo.
streamlit run scripts\control_center.py
goto end

:pro_monitor_standard
echo.
echo ═══════════════════════════════════════════════════════════════════
echo  🚀 LANCEMENT DU PRO TRADER MONITOR - MODE STANDARD
echo ═══════════════════════════════════════════════════════════════════
echo.
echo Fonctionnalités:
echo   ✅ Monitoring 24/7
echo   ✅ Détection prémarché (4h-9h30 AM ET)
echo   ✅ Pump stocks (5%+ | 2.0x volume)
echo   ✅ AI Discovery (Gemini)
echo   ✅ Alertes multi-canaux
echo.
echo Le monitor tourne en arrière-plan...
echo Vérifiez Telegram pour les alertes !
echo.
start /B python scripts\pro_trader_monitor.py
echo.
echo ✅ Monitor lancé en arrière-plan
echo ✅ Logs disponibles dans: logs\pro_monitor.log
echo.
echo Pour arrêter, choisissez option 6 ou fermez cette fenêtre
pause
goto end

:pro_monitor_aggressive
echo.
echo ═══════════════════════════════════════════════════════════════════
echo  🔥 LANCEMENT DU PRO TRADER MONITOR - MODE AGRESSIF
echo ═══════════════════════════════════════════════════════════════════
echo.
echo ⚠️  MODE AGRESSIF ACTIVÉ
echo.
echo Différences vs mode standard:
echo   • Seuil prix: 3%% (au lieu de 5%%)
echo   • Seuil volume: 1.5x (au lieu de 2.0x)
echo   • Scans plus fréquents (1 min vs 3 min)
echo.
echo ⚡ ATTENTION: Plus d'alertes (risque de sur-notification)
echo.
start /B python scripts\pro_trader_monitor.py --aggressive
echo.
echo ✅ Monitor agressif lancé
echo ✅ Logs disponibles dans: logs\pro_monitor.log
echo.
pause
goto end

:premarket_monitor
echo.
echo ═══════════════════════════════════════════════════════════════════
echo  🌅 LANCEMENT DU PREMARKET MONITOR
echo ═══════════════════════════════════════════════════════════════════
echo.
echo Détection de catalyseurs prémarché:
echo   • Earnings (résultats trimestriels)
echo   • FDA approvals (médicaments)
echo   • M^&A (fusions/acquisitions)
echo   • Guidance (révisions)
echo.
echo Actif: 4h00 - 9h30 AM ET (heure New York)
echo Scan: Toutes les 15 minutes
echo.
start /B python scripts\pro_trader_monitor.py --premarket-only
echo.
echo ✅ Premarket monitor lancé
echo.
pause
goto end

:main_dashboard
echo.
echo ═══════════════════════════════════════════════════════════════════
echo  📊 LANCEMENT DU DASHBOARD PRINCIPAL
echo ═══════════════════════════════════════════════════════════════════
echo.
echo Le dashboard va s'ouvrir dans votre navigateur...
echo.
echo Fonctionnalités:
echo   • 🎯 AI-Discovered Opportunities
echo   • 🚨 Monthly Signals (Score 0-100)
echo   • 📰 News ^& Sentiment
echo   • 📈 Technical Analysis
echo   • 💼 Portfolio Tracking
echo   • 🔙 Backtesting
echo.
streamlit run app.py
goto end

:stop_monitors
echo.
echo ═══════════════════════════════════════════════════════════════════
echo  ❌ ARRÊT DE TOUS LES MONITORS
echo ═══════════════════════════════════════════════════════════════════
echo.
echo Arrêt en cours...
taskkill /F /FI "WINDOWTITLE eq pro_trader_monitor*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq premarket_monitor*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq realtime_monitor*" >nul 2>&1
echo.
echo ✅ Tous les monitors ont été arrêtés
echo.
pause
goto end

:test_alerts
echo.
echo ═══════════════════════════════════════════════════════════════════
echo  🧪 TEST DU SYSTÈME COMPLET
echo ═══════════════════════════════════════════════════════════════════
echo.
echo Test de tous les composants du système...
echo.
python scripts\test_trading_system.py
echo.
echo Si des tests échouent, consultez la documentation
echo Documentation: docs\PRO_TRADER_SETUP.md
echo.
pause
goto end

:documentation
echo.
echo ═══════════════════════════════════════════════════════════════════
echo  ℹ️  DOCUMENTATION
echo ═══════════════════════════════════════════════════════════════════
echo.
echo Documentation disponible:
echo.
echo   📖 README.md                  - Vue d'ensemble du projet
echo   🚀 docs\PRO_TRADER_SETUP.md   - Setup professionnel complet
echo   🔔 docs\ALERT_SETUP_GUIDE.md  - Configuration des alertes
echo   🤖 docs\GEMINI_SETUP.md       - Configuration Gemini AI
echo   🌅 docs\PREMARKET_ALERTS_GUIDE.md - Guide prémarché
echo.
echo Ouvrir la documentation professionnelle ? (O/N)
set /p open_doc="> "
if /i "%open_doc%"=="O" (
    start docs\PRO_TRADER_SETUP.md
)
echo.
pause
goto end

:quit
echo.
echo Au revoir ! Bon trading 🚀💰
echo.
exit /b 0

:end
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
choice /C OQ /N /M "Options: [O] Menu principal  [Q] Quitter  > "
if errorlevel 2 goto quit
if errorlevel 1 goto start
