#!/usr/bin/env python3
"""
🎯 PROFESSIONAL TRADING SYSTEM - MASTER LAUNCHER
═══════════════════════════════════════════════════════════════════
Lance et gère tous les monitors de trading professionnel

COMPONENTS:
- 🌅 Pre-market Catalyst Scanner (4h-9h30 AM)
- 💎 Real-time Pump Scanner (9h30-16h)
- 🤖 AI Opportunity Discovery (24/7)
- 📊 Dashboard (on-demand)

USAGE:
    python scripts/launch_trading_system.py --all         # Tout lancer
    python scripts/launch_trading_system.py --premarket   # Prémarché uniquement
    python scripts/launch_trading_system.py --realtime    # Temps réel uniquement
    python scripts/launch_trading_system.py --dashboard   # Dashboard uniquement
    
AUTO-START:
    # Add to crontab (Linux/Mac)
    @reboot cd /path/to/project && python scripts/launch_trading_system.py --all
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
import subprocess
import logging
import time
import os
from datetime import datetime
from typing import List, Dict
import psutil

from modules.utils import load_config


class TradingSystemLauncher:
    """Professional trading system launcher and manager"""
    
    def __init__(self):
        """Initialize launcher"""
        self.config = load_config()
        self.logger = self._setup_logger()
        self.processes: Dict[str, subprocess.Popen] = {}
        
        # Script paths
        self.scripts = {
            'premarket': 'scripts/premarket_catalyst_scanner.py',
            'realtime': 'scripts/realtime_pump_scanner.py',
            'dashboard': 'app.py',
            'control_center': 'scripts/control_center.py'
        }
        
        self.logger.info("=" * 70)
        self.logger.info("🎯 PROFESSIONAL TRADING SYSTEM LAUNCHER")
        self.logger.info("=" * 70)
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger"""
        logger = logging.getLogger('TradingSystemLauncher')
        logger.setLevel(logging.INFO)
        
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console.setFormatter(formatter)
        
        logger.addHandler(console)
        
        return logger
    
    def is_process_running(self, script_name: str) -> bool:
        """Check if a script is already running"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any(script_name in arg for arg in cmdline):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception as e:
            self.logger.error(f"Error checking process: {e}")
            return False
    
    def launch_script(self, script_key: str, args: List[str] = None) -> bool:
        """
        Launch a monitoring script
        
        Args:
            script_key: Key from self.scripts
            args: Optional command line arguments
            
        Returns:
            True if launched successfully
        """
        try:
            script_path = self.scripts.get(script_key)
            if not script_path:
                self.logger.error(f"Unknown script: {script_key}")
                return False
            
            # Check if already running
            if self.is_process_running(script_path):
                self.logger.warning(f"⚠️ {script_key} already running")
                return True
            
            # Build command
            if script_key in ['dashboard', 'control_center']:
                # Streamlit apps
                cmd = ['streamlit', 'run', script_path, '--server.headless', 'true']
            else:
                # Python scripts
                cmd = [sys.executable, script_path]
            
            if args:
                cmd.extend(args)
            
            # Launch process
            if os.name == 'nt':  # Windows
                process = subprocess.Popen(
                    cmd,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    cwd=project_root
                )
            else:  # Linux/Mac
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    cwd=project_root,
                    start_new_session=True
                )
            
            self.processes[script_key] = process
            self.logger.info(f"✅ Launched: {script_key} (PID: {process.pid})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error launching {script_key}: {e}")
            return False
    
    def stop_script(self, script_key: str) -> bool:
        """Stop a running script"""
        try:
            script_path = self.scripts.get(script_key)
            
            # Kill process
            killed = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any(script_path in arg for arg in cmdline):
                        proc.terminate()
                        proc.wait(timeout=5)
                        killed = True
                        self.logger.info(f"🛑 Stopped: {script_key}")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    continue
            
            return killed
            
        except Exception as e:
            self.logger.error(f"Error stopping {script_key}: {e}")
            return False
    
    def launch_premarket_system(self):
        """Launch pre-market monitoring system"""
        self.logger.info("")
        self.logger.info("🌅 LAUNCHING PRE-MARKET SYSTEM")
        self.logger.info("-" * 70)
        
        # Launch pre-market catalyst scanner
        if self.launch_script('premarket'):
            self.logger.info("   ✅ Pre-market catalyst scanner started")
        else:
            self.logger.error("   ❌ Failed to start pre-market scanner")
        
        self.logger.info("")
        self.logger.info("Pre-market system is now running")
        self.logger.info("Monitoring: 4:00 AM - 9:30 AM ET")
        self.logger.info("Alerts: Telegram, Email, Desktop")
        self.logger.info("")
    
    def launch_realtime_system(self, aggressive: bool = False):
        """Launch real-time market monitoring system"""
        self.logger.info("")
        self.logger.info("💎 LAUNCHING REAL-TIME SYSTEM")
        self.logger.info("-" * 70)
        
        # Launch real-time pump scanner
        args = ['--aggressive'] if aggressive else []
        if self.launch_script('realtime', args):
            mode = "AGGRESSIVE" if aggressive else "STANDARD"
            self.logger.info(f"   ✅ Real-time pump scanner started ({mode} mode)")
        else:
            self.logger.error("   ❌ Failed to start pump scanner")
        
        self.logger.info("")
        self.logger.info("Real-time system is now running")
        self.logger.info("Monitoring: 9:30 AM - 4:00 PM ET")
        self.logger.info("Alerts: Telegram, Email, Desktop, Audio")
        self.logger.info("")
    
    def launch_all_systems(self, aggressive: bool = False):
        """Launch all monitoring systems"""
        self.logger.info("")
        self.logger.info("🚀 LAUNCHING ALL SYSTEMS")
        self.logger.info("=" * 70)
        self.logger.info("")
        
        # Pre-market
        self.logger.info("1️⃣ Pre-market Catalyst Scanner")
        self.launch_script('premarket')
        time.sleep(2)
        
        # Real-time
        self.logger.info("")
        self.logger.info("2️⃣ Real-time Pump Scanner")
        args = ['--aggressive'] if aggressive else []
        self.launch_script('realtime', args)
        time.sleep(2)
        
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("✅ ALL SYSTEMS LAUNCHED")
        self.logger.info("=" * 70)
        self.logger.info("")
        self.logger.info("📊 MONITORING STATUS:")
        self.logger.info("   🌅 Pre-market: 4:00 AM - 9:30 AM ET")
        self.logger.info("   💎 Real-time: 9:30 AM - 4:00 PM ET")
        self.logger.info("")
        self.logger.info("🔔 ALERT CHANNELS:")
        self.logger.info("   📱 Telegram (PRIMARY)")
        self.logger.info("   📧 Email (BACKUP)")
        self.logger.info("   🔔 Desktop Notifications")
        self.logger.info("   🔊 Audio Alerts")
        self.logger.info("")
        self.logger.info("🎛️ To manage systems, use Control Center:")
        self.logger.info("   streamlit run scripts/control_center.py")
        self.logger.info("")
        self.logger.info("🛑 To stop all systems:")
        self.logger.info("   python scripts/launch_trading_system.py --stop-all")
        self.logger.info("")
    
    def launch_dashboard(self):
        """Launch main dashboard"""
        self.logger.info("")
        self.logger.info("📊 LAUNCHING DASHBOARD")
        self.logger.info("-" * 70)
        
        if self.launch_script('dashboard'):
            self.logger.info("   ✅ Dashboard started")
            self.logger.info("   🌐 URL: http://localhost:8501")
        else:
            self.logger.error("   ❌ Failed to start dashboard")
        
        self.logger.info("")
    
    def launch_control_center(self):
        """Launch control center"""
        self.logger.info("")
        self.logger.info("🎛️ LAUNCHING CONTROL CENTER")
        self.logger.info("-" * 70)
        
        if self.launch_script('control_center'):
            self.logger.info("   ✅ Control center started")
            self.logger.info("   🌐 URL: http://localhost:8502")
        else:
            self.logger.error("   ❌ Failed to start control center")
        
        self.logger.info("")
    
    def stop_all_systems(self):
        """Stop all running systems"""
        self.logger.info("")
        self.logger.info("🛑 STOPPING ALL SYSTEMS")
        self.logger.info("-" * 70)
        
        for script_key in self.scripts.keys():
            if self.stop_script(script_key):
                self.logger.info(f"   ✅ Stopped: {script_key}")
        
        self.logger.info("")
        self.logger.info("All systems stopped")
        self.logger.info("")
    
    def show_status(self):
        """Show status of all systems"""
        self.logger.info("")
        self.logger.info("📊 SYSTEM STATUS")
        self.logger.info("=" * 70)
        self.logger.info("")
        
        for script_key, script_path in self.scripts.items():
            running = self.is_process_running(script_path)
            status = "🟢 ONLINE" if running else "🔴 OFFLINE"
            self.logger.info(f"   {script_key:20} {status}")
        
        self.logger.info("")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Professional Trading System Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Launch complete system
  python scripts/launch_trading_system.py --all
  
  # Launch pre-market only
  python scripts/launch_trading_system.py --premarket
  
  # Launch real-time with aggressive mode
  python scripts/launch_trading_system.py --realtime --aggressive
  
  # Launch dashboard
  python scripts/launch_trading_system.py --dashboard
  
  # Launch control center
  python scripts/launch_trading_system.py --control-center
  
  # Show system status
  python scripts/launch_trading_system.py --status
  
  # Stop all systems
  python scripts/launch_trading_system.py --stop-all

AUTO-START (Linux/Mac cron):
  @reboot cd /path/to/project && python scripts/launch_trading_system.py --all

AUTO-START (Windows Task Scheduler):
  Action: Start program
  Program: python.exe
  Arguments: C:\\path\\to\\project\\scripts\\launch_trading_system.py --all
  Start in: C:\\path\\to\\project
        """
    )
    
    parser.add_argument('--all', action='store_true', help='Launch all systems')
    parser.add_argument('--premarket', action='store_true', help='Launch pre-market system')
    parser.add_argument('--realtime', action='store_true', help='Launch real-time system')
    parser.add_argument('--dashboard', action='store_true', help='Launch main dashboard')
    parser.add_argument('--control-center', action='store_true', help='Launch control center')
    parser.add_argument('--aggressive', action='store_true', help='Use aggressive mode (faster scans)')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--stop-all', action='store_true', help='Stop all systems')
    
    args = parser.parse_args()
    
    # Initialize launcher
    launcher = TradingSystemLauncher()
    
    # Execute actions
    if args.stop_all:
        launcher.stop_all_systems()
    
    elif args.status:
        launcher.show_status()
    
    elif args.all:
        launcher.launch_all_systems(aggressive=args.aggressive)
    
    elif args.premarket:
        launcher.launch_premarket_system()
    
    elif args.realtime:
        launcher.launch_realtime_system(aggressive=args.aggressive)
    
    elif args.dashboard:
        launcher.launch_dashboard()
    
    elif args.control_center:
        launcher.launch_control_center()
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
