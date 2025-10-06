@echo off
REM ====================================================
REM  INTRADAY TRADING SYSTEM - Quick Launcher
REM ====================================================

title Intraday Trading System

:menu
cls
echo ================================================
echo    INTRADAY TRADING SYSTEM - LAUNCHER
echo ================================================
echo.
echo   Trading automatique avec notifications Telegram
echo   Focus: Intraday trades (9:30-16:00 ET)
echo.
echo ================================================
echo.
echo  1. Lancer Intraday Trader (Mode Standard)
echo  2. Lancer Intraday Trader (Mode Agressif)
echo  3. Configurer Auto-Start (Task Scheduler)
echo  4. Tester le systeme
echo  5. Arreter tous les monitors
echo  6. Voir les logs
echo  7. Ouvrir Dashboard (Live Alerts)
echo  8. Documentation Intraday
echo  9. Quitter
echo.
echo ================================================
echo.

set /p choice="Votre choix (1-9): "

if "%choice%"=="1" goto standard
if "%choice%"=="2" goto aggressive
if "%choice%"=="3" goto autostart
if "%choice%"=="4" goto test
if "%choice%"=="5" goto stop
if "%choice%"=="6" goto logs
if "%choice%"=="7" goto dashboard
if "%choice%"=="8" goto docs
if "%choice%"=="9" goto end

echo.
echo Choix invalide !
timeout /t 2 >nul
goto menu

:standard
echo.
echo ================================================
echo  Lancement Intraday Trader (Mode Standard)
echo ================================================
echo.
echo  Criteres:
echo    - Prix: +3%% minimum
echo    - Volume: 5x average
echo    - Score minimum: 75/100
echo    - Scan: toutes les 30s
echo.
echo  Demarrage...
python scripts\intraday_trader.py
pause
goto menu

:aggressive
echo.
echo ================================================
echo  Lancement Intraday Trader (Mode Agressif)
echo ================================================
echo.
echo  Criteres:
echo    - Prix: +2%% minimum
echo    - Volume: 3x average
echo    - Score minimum: 70/100
echo    - Scan: toutes les 15s
echo.
echo  ATTENTION: Plus d'alertes !
echo.
echo  Demarrage...
python scripts\intraday_trader.py --aggressive
pause
goto menu

:autostart
echo.
echo ================================================
echo  Configuration Auto-Start
echo ================================================
echo.
echo  Pour configurer le demarrage automatique:
echo.
echo  1. Ouvrir Task Scheduler (Win+R: taskschd.msc)
echo  2. Create Task: "Intraday Trading System"
echo  3. Trigger: At startup
echo  4. Action: 
echo     - Program: %cd%\.venv\Scripts\python.exe
echo     - Arguments: %cd%\scripts\start_intraday_system.py
echo     - Start in: %cd%
echo  5. Settings: Run with highest privileges
echo.
echo  Documentation complete: docs\INTRADAY_TRADING_GUIDE.md
echo.
pause
goto menu

:test
echo.
echo ================================================
echo  Test du Systeme
echo ================================================
echo.
echo  Verification de tous les composants...
echo.
python scripts\test_trading_system.py
echo.
pause
goto menu

:stop
echo.
echo ================================================
echo  Arret de tous les monitors
echo ================================================
echo.
python scripts\launch_trading_system.py --stop-all
echo.
echo  Tous les monitors ont ete arretes.
pause
goto menu

:logs
echo.
echo ================================================
echo  Logs du Systeme
echo ================================================
echo.
echo  1. Logs Intraday Trader
echo  2. Logs Auto-Start
echo  3. Logs Application
echo  4. Retour
echo.
set /p logchoice="Votre choix (1-4): "

if "%logchoice%"=="1" (
    echo.
    echo ====== INTRADAY TRADER LOGS ======
    type logs\intraday_trader.log
    pause
    goto logs
)
if "%logchoice%"=="2" (
    echo.
    echo ====== AUTO-START LOGS ======
    type logs\auto_start.log
    pause
    goto logs
)
if "%logchoice%"=="3" (
    echo.
    echo ====== APPLICATION LOGS ======
    type logs\app.log
    pause
    goto logs
)
goto menu

:dashboard
echo.
echo ================================================
echo  Lancement Dashboard
echo ================================================
echo.
echo  Ouverture du dashboard avec onglet Live Alerts...
echo  URL: http://localhost:8501
echo.
start streamlit run app.py
echo.
echo  Dashboard lance dans votre navigateur.
timeout /t 3 >nul
goto menu

:docs
echo.
echo ================================================
echo  Documentation Intraday
echo ================================================
echo.
echo  Ouverture de la documentation...
start docs\INTRADAY_TRADING_GUIDE.md
echo.
timeout /t 2 >nul
goto menu

:end
echo.
echo Au revoir !
timeout /t 1 >nul
exit
