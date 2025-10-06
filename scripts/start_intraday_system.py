#!/usr/bin/env python3
"""
🤖 AUTO-START INTRADAY SYSTEM
=============================

Lance automatiquement le système de trading intraday.
Conçu pour tourner en arrière-plan 24/7 sans intervention humaine.

CONFIGURATION WINDOWS (Task Scheduler):
1. Ouvrir "Task Scheduler" (Planificateur de tâches)
2. Create Task → "Intraday Trading System"
3. Triggers → "At log on" ou "At startup"
4. Actions → python.exe C:\path\to\scripts\start_intraday_system.py
5. Settings → "Run whether user is logged on or not"

Le système:
- Démarre automatiquement au démarrage Windows
- Tourne en arrière-plan (pas de fenêtre)
- Envoie notifications Telegram automatiquement
- Se relance en cas d'erreur
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import logging
import subprocess
from datetime import datetime
import pytz

from modules.alert_manager import AlertManager
from modules.utils import load_config

# Configure logging
log_file = Path(__file__).parent.parent / 'logs' / 'auto_start.log'
log_file.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutoStartSystem:
    """
    Système de démarrage automatique pour trading intraday.
    """
    
    def __init__(self):
        self.config = load_config()
        self.alert_manager = AlertManager(self.config)
        self.scripts_dir = Path(__file__).parent
        self.process = None
        
        logger.info("✅ Auto-Start System initialized")
    
    def send_startup_notification(self):
        """Envoyer notification de démarrage."""
        et_tz = pytz.timezone('America/New_York')
        now_et = datetime.now(et_tz)
        
        message = f"""
🤖 **INTRADAY SYSTEM STARTED**

✅ Le système de trading intraday est maintenant actif.

🕐 **Startup Time**: {now_et.strftime('%Y-%m-%d %H:%M:%S ET')}

📊 **Mode**: Automatic Intraday Trading
⏰ **Active Hours**: 9:30-16:00 ET (Mon-Fri)
🔔 **Notifications**: Telegram enabled

💡 **Vous recevrez des alertes pour**:
  • 🟢 Entry signals (ENTRY)
  • 🎯 Exit signals (EXIT)
  • ⚠️ Stop loss warnings
  • 🔔 Auto-close avant 16:00

📱 Surveillez vos notifications Telegram !

🚀 **Le système tourne en arrière-plan 24/7**
"""
        
        self.alert_manager.send_alert(
            alert_type="system_startup",
            symbol="SYSTEM",
            message=message,
            priority="HIGH"
        )
        
        logger.info("📤 Startup notification sent")
    
    def start_intraday_trader(self, aggressive: bool = False):
        """
        Lancer le scanner intraday en arrière-plan.
        
        Args:
            aggressive: Mode agressif (plus de trades)
        """
        script_path = self.scripts_dir / 'intraday_trader.py'
        
        if not script_path.exists():
            logger.error(f"❌ Script not found: {script_path}")
            return False
        
        try:
            # Construire commande
            cmd = [sys.executable, str(script_path)]
            if aggressive:
                cmd.append('--aggressive')
            
            # Lancer en arrière-plan (CREATE_NO_WINDOW sur Windows)
            if sys.platform == 'win32':
                # Windows: pas de fenêtre
                CREATE_NO_WINDOW = 0x08000000
                self.process = subprocess.Popen(
                    cmd,
                    creationflags=CREATE_NO_WINDOW,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                # Linux/Mac
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            logger.info(f"✅ Intraday trader started (PID: {self.process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start intraday trader: {e}")
            return False
    
    def monitor_process(self):
        """
        Surveiller le processus et relancer en cas d'arrêt.
        """
        logger.info("👀 Monitoring intraday trader process...")
        
        while True:
            try:
                # Vérifier si processus est actif
                if self.process and self.process.poll() is not None:
                    # Processus arrêté
                    logger.warning("⚠️ Intraday trader stopped - restarting...")
                    
                    # Notification d'erreur
                    self.alert_manager.send_alert(
                        alert_type="system_restart",
                        symbol="SYSTEM",
                        message="⚠️ System Restarting\n\nLe système de trading s'est arrêté et redémarre automatiquement...",
                        priority="MEDIUM"
                    )
                    
                    # Attendre un peu avant de relancer
                    time.sleep(5)
                    
                    # Relancer
                    aggressive = '--aggressive' in sys.argv
                    self.start_intraday_trader(aggressive=aggressive)
                
                # Attendre avant prochaine vérification
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info("\n🛑 Stopping auto-start system (user interrupt)")
                if self.process:
                    self.process.terminate()
                break
            except Exception as e:
                logger.error(f"❌ Error in monitor: {e}")
                time.sleep(10)
    
    def run(self, aggressive: bool = False):
        """
        Démarrer le système complet.
        
        Args:
            aggressive: Mode agressif
        """
        logger.info("🚀 Starting Auto-Start System...")
        
        # Envoyer notification de démarrage
        self.send_startup_notification()
        
        # Lancer intraday trader
        if not self.start_intraday_trader(aggressive=aggressive):
            logger.error("❌ Failed to start system")
            return
        
        # Surveiller le processus
        self.monitor_process()


def main():
    """Entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-Start Intraday Trading System")
    parser.add_argument(
        '--aggressive',
        action='store_true',
        help='Mode agressif (plus de trades)'
    )
    parser.add_argument(
        '--no-notify',
        action='store_true',
        help='Ne pas envoyer notification de démarrage'
    )
    
    args = parser.parse_args()
    
    # Créer et lancer système
    system = AutoStartSystem()
    
    # Skip notification si demandé
    if args.no_notify:
        logger.info("ℹ️ Skipping startup notification")
    
    system.run(aggressive=args.aggressive)


if __name__ == "__main__":
    main()
