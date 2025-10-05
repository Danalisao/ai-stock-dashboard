#!/usr/bin/env python3
"""
🚀 Professional Trading System - Quick Launch
One-command professional trading system startup
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Quick launch for professional traders"""
    print("💼 PROFESSIONAL TRADING SYSTEM")
    print("🚀 Quick Launch Initiated...")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    venv_python = project_root / "venv" / "bin" / "python"
    
    if not venv_python.exists():
        print("❌ Virtual environment not found!")
        print("💡 Run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt")
        return 1
    
    # Step 1: Validate configuration
    print("🔧 Validating professional configuration...")
    result = subprocess.run([str(venv_python), "validate_pro_config.py"], 
                          cwd=project_root, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Configuration validation failed!")
        print(result.stdout)
        print(result.stderr)
        return 1
    
    print("✅ Professional configuration validated")
    
    # Step 2: Launch dashboard
    print("🌐 Starting professional trading dashboard...")
    print("📍 Dashboard: http://localhost:8501")
    print("🛡️ All professional safeguards active")
    print("🔄 Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        subprocess.run([
            str(venv_python), "-m", "streamlit", "run", "app.py",
            "--server.port=8501",
            "--server.headless=true"
        ], cwd=project_root)
    except KeyboardInterrupt:
        print("\n🛑 Professional trading system stopped")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())