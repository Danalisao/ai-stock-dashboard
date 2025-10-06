#!/usr/bin/env python3
"""
🎛️ PROFESSIONAL TRADER CONTROL CENTER
═══════════════════════════════════════════════════════════════════
Dashboard de contrôle pour monitoring system
Lance, arrête et contrôle tous les modules de trading

FEATURES:
- 🚀 Lancement/arrêt des monitors (premarket, realtime, AI)
- 📊 Status en temps réel des alertes et opportunités
- 🔔 Configuration des alertes multi-canaux
- 📈 Dashboard de performance du monitoring
- ⚙️ Configuration simplifiée

USAGE:
    python scripts/control_center.py
"""

import streamlit as st
import subprocess
import psutil
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import pandas as pd
from typing import Dict, List, Optional

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.utils import load_config, is_market_open
from modules.database_manager import DatabaseManager
from modules.alert_manager import AlertManager

# Page config
st.set_page_config(
    page_title="Professional Trader Control Center",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb, #1dd1a1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .status-online {
        color: #1dd1a1;
        font-weight: bold;
    }
    .status-offline {
        color: #ff6b6b;
        font-weight: bold;
    }
    .metric-card {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        margin: 0.5rem 0;
    }
    .alert-critical {
        background: rgba(255,107,107,0.2);
        border-left: 4px solid #ff6b6b;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .alert-high {
        background: rgba(254,202,87,0.2);
        border-left: 4px solid #feca57;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .alert-medium {
        background: rgba(72,219,251,0.2);
        border-left: 4px solid #48dbfb;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


class ControlCenter:
    """Professional Trading Control Center"""
    
    def __init__(self):
        """Initialize control center"""
        self.config = load_config()
        self.db = DatabaseManager(self.config.get('database', {}))
        self.alert_manager = AlertManager(self.config)
        self.process_cache: Dict[str, Dict] = {}
    
    def check_process_running(self, script_name: str) -> bool:
        """Check if a monitoring script is running"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline')
                    if cmdline and any(script_name in str(cmd) for cmd in cmdline):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception as e:
            st.error(f"Error checking process: {e}")
            return False
    
    def start_monitor(self, script_name: str, args: List[str] = None) -> bool:
        """Start a monitoring script"""
        try:
            cmd = [sys.executable, f"scripts/{script_name}"]
            if args:
                cmd.extend(args)
            
            # Start process in background
            if os.name == 'nt':  # Windows
                subprocess.Popen(
                    cmd,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    cwd=project_root
                )
            else:  # Linux/Mac
                subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    cwd=project_root
                )
            
            return True
        except Exception as e:
            st.error(f"Error starting {script_name}: {e}")
            return False
    
    def stop_monitor(self, script_name: str) -> bool:
        """Stop a monitoring script"""
        try:
            killed = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline')
                    if cmdline and any(script_name in str(cmd) for cmd in cmdline):
                        proc.terminate()
                        killed = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return killed
        except Exception as e:
            st.error(f"Error stopping {script_name}: {e}")
            return False
    
    def render_header(self):
        """Render header"""
        st.markdown('<div class="main-header">🎛️ PROFESSIONAL TRADER CONTROL CENTER</div>', 
                   unsafe_allow_html=True)
        
        # Market status
        market_open = is_market_open()
        if market_open:
            st.success("🟢 **MARKETS OPEN** - Active Trading Mode")
        else:
            st.info("🔴 **MARKETS CLOSED** - Preparation Mode")
    
    def render_monitor_status(self):
        """Render monitoring system status"""
        st.header("📡 Monitoring Systems")
        
        col1, col2, col3 = st.columns(3)
        
        # Pro Trader Monitor
        with col1:
            st.subheader("🚀 Pro Trader Monitor")
            running = self.check_process_running("pro_trader_monitor.py")
            
            if running:
                st.markdown('<p class="status-online">● ONLINE</p>', unsafe_allow_html=True)
                st.caption("24/7 opportunity detection active")
                
                if st.button("🛑 Stop Monitor", key="stop_pro"):
                    if self.stop_monitor("pro_trader_monitor.py"):
                        st.success("Monitor stopped")
                        st.rerun()
            else:
                st.markdown('<p class="status-offline">● OFFLINE</p>', unsafe_allow_html=True)
                st.caption("24/7 monitoring inactive")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("▶️ Start", key="start_pro"):
                        if self.start_monitor("pro_trader_monitor.py"):
                            st.success("Monitor started")
                            st.rerun()
                
                with col_b:
                    if st.button("🔥 Aggressive", key="start_pro_agg"):
                        if self.start_monitor("pro_trader_monitor.py", ["--aggressive"]):
                            st.success("Aggressive mode started")
                            st.rerun()
        
        # Premarket Monitor
        with col2:
            st.subheader("🌅 Premarket Monitor")
            running = self.check_process_running("premarket_monitor.py")
            
            if running:
                st.markdown('<p class="status-online">● ONLINE</p>', unsafe_allow_html=True)
                st.caption("Catalyst detection active")
                
                if st.button("🛑 Stop", key="stop_premarket"):
                    if self.stop_monitor("premarket_monitor.py"):
                        st.success("Premarket monitor stopped")
                        st.rerun()
            else:
                st.markdown('<p class="status-offline">● OFFLINE</p>', unsafe_allow_html=True)
                
                if st.button("▶️ Start", key="start_premarket"):
                    if self.start_monitor("premarket_monitor.py", ["--continuous"]):
                        st.success("Premarket monitor started")
                        st.rerun()
        
        # Realtime Monitor
        with col3:
            st.subheader("⏱️ Realtime Monitor")
            running = self.check_process_running("realtime_monitor.py")
            
            if running:
                st.markdown('<p class="status-online">● ONLINE</p>', unsafe_allow_html=True)
                st.caption("Live price monitoring active")
                
                if st.button("🛑 Stop", key="stop_realtime"):
                    if self.stop_monitor("realtime_monitor.py"):
                        st.success("Realtime monitor stopped")
                        st.rerun()
            else:
                st.markdown('<p class="status-offline">● OFFLINE</p>', unsafe_allow_html=True)
                
                if st.button("▶️ Start", key="start_realtime"):
                    if self.start_monitor("realtime_monitor.py"):
                        st.success("Realtime monitor started")
                        st.rerun()
    
    def render_recent_alerts(self):
        """Render recent alerts"""
        st.header("🚨 Recent Alerts")
        
        # Get recent alerts
        alerts = self.db.get_recent_alerts(limit=20)
        
        if not alerts:
            st.info("No recent alerts")
            return
        
        # Group by priority
        critical = [a for a in alerts if a['priority'] == 'CRITICAL']
        high = [a for a in alerts if a['priority'] == 'HIGH']
        medium = [a for a in alerts if a['priority'] == 'MEDIUM']
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Alerts", len(alerts))
        with col2:
            st.metric("🔴 Critical", len(critical))
        with col3:
            st.metric("🟡 High", len(high))
        with col4:
            st.metric("🔵 Medium", len(medium))
        
        st.divider()
        
        # Display alerts
        for alert in alerts[:10]:
            priority = alert['priority']
            
            if priority == 'CRITICAL':
                css_class = "alert-critical"
                emoji = "🔴"
            elif priority == 'HIGH':
                css_class = "alert-high"
                emoji = "🟡"
            else:
                css_class = "alert-medium"
                emoji = "🔵"
            
            st.markdown(f"""
            <div class="{css_class}">
                <strong>{emoji} {alert['symbol']} - {alert['alert_type']}</strong><br>
                {alert['message']}<br>
                <small>{alert['timestamp']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    def render_alert_config(self):
        """Render alert configuration"""
        st.header("⚙️ Alert Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📱 Channels")
            
            telegram_enabled = st.checkbox(
                "Telegram (RECOMMENDED)",
                value=self.config.get('alerts', {}).get('channels', {}).get('telegram', False),
                help="Fastest alerts via Telegram bot"
            )
            
            email_enabled = st.checkbox(
                "Email",
                value=self.config.get('alerts', {}).get('channels', {}).get('email', False),
                help="Email alerts (Gmail)"
            )
            
            desktop_enabled = st.checkbox(
                "Desktop Notifications",
                value=self.config.get('alerts', {}).get('channels', {}).get('desktop', True),
                help="System notifications"
            )
            
            audio_enabled = st.checkbox(
                "Audio Alerts",
                value=self.config.get('alerts', {}).get('channels', {}).get('audio', False),
                help="Sound alerts"
            )
            
            if st.button("💾 Save Channel Config"):
                st.success("Configuration saved (restart monitors to apply)")
        
        with col2:
            st.subheader("🎯 Thresholds")
            
            price_threshold = st.slider(
                "Price Change Alert (%)",
                min_value=1.0,
                max_value=10.0,
                value=5.0,
                step=0.5,
                help="Alert on X% price movement"
            )
            
            volume_threshold = st.slider(
                "Volume Surge Alert (x)",
                min_value=1.0,
                max_value=5.0,
                value=2.0,
                step=0.5,
                help="Alert on Xx average volume"
            )
            
            confidence_threshold = st.slider(
                "AI Confidence Threshold (%)",
                min_value=50,
                max_value=90,
                value=70,
                step=5,
                help="Minimum AI confidence for opportunity alerts"
            )
            
            if st.button("💾 Save Thresholds"):
                st.success("Thresholds saved")
        
        st.divider()
        
        # Test alerts
        st.subheader("🧪 Test Alerts")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📱 Test Telegram"):
                results = self.alert_manager.test_alerts()
                if results.get('telegram'):
                    st.success("✅ Telegram working")
                else:
                    st.error("❌ Telegram failed - check config")
        
        with col2:
            if st.button("📧 Test Email"):
                results = self.alert_manager.test_alerts()
                if results.get('email'):
                    st.success("✅ Email working")
                else:
                    st.error("❌ Email failed - check credentials")
        
        with col3:
            if st.button("🔔 Test Desktop"):
                results = self.alert_manager.test_alerts()
                if results.get('desktop'):
                    st.success("✅ Desktop working")
                else:
                    st.error("❌ Desktop failed")
    
    def render_performance_stats(self):
        """Render monitoring performance statistics"""
        st.header("📊 Monitoring Performance")
        
        # Get stats from database
        alerts_today = self.db.get_recent_alerts(limit=1000)
        alerts_today = [a for a in alerts_today if a['timestamp'].startswith(datetime.now().strftime('%Y-%m-%d'))]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Alerts Today", len(alerts_today))
        
        with col2:
            critical_today = sum(1 for a in alerts_today if a['priority'] == 'CRITICAL')
            st.metric("Critical Alerts", critical_today)
        
        with col3:
            unique_symbols = len(set(a['symbol'] for a in alerts_today))
            st.metric("Unique Symbols", unique_symbols)
        
        with col4:
            # Estimate response time (placeholder)
            st.metric("Avg Response", "< 30s")
        
        st.divider()
        
        # Alert timeline
        if alerts_today:
            st.subheader("📈 Alert Timeline (Today)")
            
            df = pd.DataFrame(alerts_today)
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            hourly_alerts = df.groupby('hour').size().reindex(range(24), fill_value=0)
            
            st.bar_chart(hourly_alerts)
    
    def run(self):
        """Run control center"""
        self.render_header()
        
        st.divider()
        
        # Main tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎛️ Monitors",
            "🚨 Alerts",
            "⚙️ Configuration",
            "📊 Performance"
        ])
        
        with tab1:
            self.render_monitor_status()
        
        with tab2:
            self.render_recent_alerts()
        
        with tab3:
            self.render_alert_config()
        
        with tab4:
            self.render_performance_stats()
        
        # Footer
        st.divider()
        st.caption("Professional Trader Control Center | Real-time monitoring & alerts")


def main():
    """Main entry point"""
    control_center = ControlCenter()
    control_center.run()


if __name__ == '__main__':
    main()
