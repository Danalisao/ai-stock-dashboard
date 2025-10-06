# ═══════════════════════════════════════════════════════════════════════
#    PROFESSIONAL TRADER LAUNCHER - PowerShell Edition
# ═══════════════════════════════════════════════════════════════════════
#    Lancement moderne du système de trading professionnel (Windows)
# ═══════════════════════════════════════════════════════════════════════

# Require PowerShell 5.1+
#Requires -Version 5.1

# Set error action
$ErrorActionPreference = "Stop"

# Colors
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Banner
function Show-Banner {
    Write-ColorOutput ""
    Write-ColorOutput "╔═══════════════════════════════════════════════════════════════════╗" "Cyan"
    Write-ColorOutput "║                                                                   ║" "Cyan"
    Write-ColorOutput "║        🚀 PROFESSIONAL TRADER PLATFORM - LAUNCHER 🚀             ║" "Cyan"
    Write-ColorOutput "║                                                                   ║" "Cyan"
    Write-ColorOutput "╚═══════════════════════════════════════════════════════════════════╝" "Cyan"
    Write-ColorOutput ""
}

# Check Python
function Test-Python {
    try {
        $pythonVersion = python --version 2>&1
        Write-ColorOutput "✅ Python détecté: $pythonVersion" "Green"
        return $true
    }
    catch {
        Write-ColorOutput "❌ ERREUR: Python n'est pas installé ou pas dans PATH" "Red"
        Write-ColorOutput ""
        Write-ColorOutput "Installez Python 3.9+ depuis: https://www.python.org/downloads/" "Yellow"
        return $false
    }
}

# Menu
function Show-Menu {
    Write-ColorOutput "╔═══════════════════════════════════════════════════════════════════╗" "Cyan"
    Write-ColorOutput "║                    CHOISISSEZ VOTRE MODE                          ║" "Cyan"
    Write-ColorOutput "╚═══════════════════════════════════════════════════════════════════╝" "Cyan"
    Write-ColorOutput ""
    Write-ColorOutput "  1. 🎛️  Control Center (Dashboard de contrôle - RECOMMANDÉ)" "White"
    Write-ColorOutput "  2. 🚀 Système complet (Prémarché + Temps réel + IA)" "White"
    Write-ColorOutput "  3. 🔥 Système agressif (Scans rapides, plus d'alertes)" "White"
    Write-ColorOutput "  4. 🌅 Prémarché uniquement (4h-9h30 AM ET)" "White"
    Write-ColorOutput "  5. 💎 Temps réel uniquement (9h30-16h ET)" "White"
    Write-ColorOutput "  6. 📊 Dashboard principal (Analyse et signaux)" "White"
    Write-ColorOutput "  7. ❌ Arrêter tous les monitors" "White"
    Write-ColorOutput "  8. 🧪 Tester le système" "White"
    Write-ColorOutput "  9. 📊 Statut du système" "White"
    Write-ColorOutput "  0. 🚪 Quitter" "White"
    Write-ColorOutput ""
}

# Launch Control Center
function Start-ControlCenter {
    Write-ColorOutput ""
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════" "Cyan"
    Write-ColorOutput " 🎛️  LANCEMENT DU CONTROL CENTER" "Cyan"
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════" "Cyan"
    Write-ColorOutput ""
    Write-ColorOutput "Le Control Center va s'ouvrir dans votre navigateur..." "Yellow"
    Write-ColorOutput "URL: http://localhost:8502" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "Appuyez sur Ctrl+C pour arrêter" "Yellow"
    Write-ColorOutput ""
    
    streamlit run scripts\control_center.py
}

# Launch Full System
function Start-FullSystem {
    param([bool]$Aggressive = $false)
    
    Write-ColorOutput ""
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════" "Cyan"
    if ($Aggressive) {
        Write-ColorOutput " 🔥 LANCEMENT DU SYSTÈME AGRESSIF" "Cyan"
    }
    else {
        Write-ColorOutput " 🚀 LANCEMENT DU SYSTÈME COMPLET" "Cyan"
    }
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════" "Cyan"
    Write-ColorOutput ""
    
    $args = @("--all")
    if ($Aggressive) {
        $args += "--aggressive"
    }
    
    Write-ColorOutput "Démarrage des monitors..." "Yellow"
    python scripts\launch_trading_system.py @args
    
    Write-ColorOutput ""
    Write-ColorOutput "✅ Système lancé avec succès" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "Pour gérer les monitors, utilisez le Control Center:" "Yellow"
    Write-ColorOutput "  streamlit run scripts\control_center.py" "Cyan"
    Write-ColorOutput ""
}

# Launch Premarket Only
function Start-Premarket {
    Write-ColorOutput ""
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════" "Cyan"
    Write-ColorOutput " 🌅 LANCEMENT DU SCANNER PRÉMARCHÉ" "Cyan"
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════" "Cyan"
    Write-ColorOutput ""
    
    python scripts\launch_trading_system.py --premarket
    
    Write-ColorOutput ""
    Write-ColorOutput "✅ Scanner prémarché lancé" "Green"
    Write-ColorOutput "   Actif: 4h00 - 9h30 AM ET" "Yellow"
}

# Launch Realtime Only
function Start-Realtime {
    Write-ColorOutput ""
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════" "Cyan"
    Write-ColorOutput " 💎 LANCEMENT DU SCANNER TEMPS RÉEL" "Cyan"
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════" "Cyan"
    Write-ColorOutput ""
    
    python scripts\launch_trading_system.py --realtime
    
    Write-ColorOutput ""
    Write-ColorOutput "✅ Scanner temps réel lancé" "Green"
    Write-ColorOutput "   Actif: 9h30 - 16h00 ET" "Yellow"
}

# Launch Dashboard
function Start-Dashboard {
    Write-ColorOutput ""
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════" "Cyan"
    Write-ColorOutput " 📊 LANCEMENT DU DASHBOARD" "Cyan"
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════" "Cyan"
    Write-ColorOutput ""
    Write-ColorOutput "Le dashboard va s'ouvrir dans votre navigateur..." "Yellow"
    Write-ColorOutput "URL: http://localhost:8501" "Green"
    Write-ColorOutput ""
    
    streamlit run app.py
}

# Stop All Monitors
function Stop-AllMonitors {
    Write-ColorOutput ""
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════" "Cyan"
    Write-ColorOutput " ❌ ARRÊT DE TOUS LES MONITORS" "Cyan"
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════" "Cyan"
    Write-ColorOutput ""
    
    python scripts\launch_trading_system.py --stop-all
    
    Write-ColorOutput ""
    Write-ColorOutput "✅ Tous les monitors ont été arrêtés" "Green"
}

# Test System
function Test-System {
    Write-ColorOutput ""
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════" "Cyan"
    Write-ColorOutput " 🧪 TEST DU SYSTÈME COMPLET" "Cyan"
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════" "Cyan"
    Write-ColorOutput ""
    
    python scripts\test_trading_system.py
}

# Show Status
function Show-Status {
    Write-ColorOutput ""
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════" "Cyan"
    Write-ColorOutput " 📊 STATUT DU SYSTÈME" "Cyan"
    Write-ColorOutput "═══════════════════════════════════════════════════════════════════" "Cyan"
    Write-ColorOutput ""
    
    python scripts\launch_trading_system.py --status
}

# Main
function Main {
    Show-Banner
    
    # Check Python
    if (-not (Test-Python)) {
        Write-ColorOutput ""
        Write-Host "Appuyez sur une touche pour quitter..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
    
    Write-ColorOutput ""
    
    while ($true) {
        Show-Menu
        
        $choice = Read-Host "Votre choix (0-9)"
        
        switch ($choice) {
            "1" {
                Start-ControlCenter
                break
            }
            "2" {
                Start-FullSystem -Aggressive $false
                break
            }
            "3" {
                Start-FullSystem -Aggressive $true
                break
            }
            "4" {
                Start-Premarket
                break
            }
            "5" {
                Start-Realtime
                break
            }
            "6" {
                Start-Dashboard
                break
            }
            "7" {
                Stop-AllMonitors
                Write-ColorOutput ""
                Write-Host "Appuyez sur une touche pour continuer..."
                $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            }
            "8" {
                Test-System
                Write-ColorOutput ""
                Write-Host "Appuyez sur une touche pour continuer..."
                $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            }
            "9" {
                Show-Status
                Write-ColorOutput ""
                Write-Host "Appuyez sur une touche pour continuer..."
                $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            }
            "0" {
                Write-ColorOutput ""
                Write-ColorOutput "Au revoir ! Bon trading 🚀💰" "Green"
                Write-ColorOutput ""
                exit 0
            }
            default {
                Write-ColorOutput ""
                Write-ColorOutput "❌ Choix invalide. Veuillez choisir entre 0 et 9." "Red"
                Write-ColorOutput ""
                Write-Host "Appuyez sur une touche pour continuer..."
                $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            }
        }
    }
}

# Run
Main
