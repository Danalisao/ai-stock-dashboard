#!/usr/bin/env python3
"""
🚀 Professional Trading Dashboard Launcher
Launch the AI Stock Trading Dashboard in professional mode
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Launch the professional trading dashboard"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    try:
        # Import modules to verify everything works
        from modules.utils import load_config
        from modules.pro_mode_guard import ProModeGuard
        from modules.database_manager import DatabaseManager
        
        print("🚀 AI Stock Trading Dashboard - Professional Mode")
        print("=" * 60)
        
        # Load configuration
        print("📋 Loading configuration...")
        config = load_config()
        
        # Initialize database
        print("🗄️ Initializing database...")
        db = DatabaseManager(config.get('database', './data/stock_data.db'))
        
        # Professional mode validation
        print("🛡️ Validating professional mode readiness...")
        pro_guard = ProModeGuard(config, db)
        
        validation = pro_guard.ensure_production_ready(enforce=False)
        
        if validation.warnings:
            print("\n⚠️ Professional Mode Warnings:")
            for warning in validation.warnings:
                print(f"  - {warning}")
        
        if not validation.passed:
            print("\n❌ Professional Mode Issues:")
            for issue in validation.issues:
                print(f"  - {issue}")
            print("\n🚫 Cannot start in professional mode. Please fix the issues above.")
            return 1
        
        print("✅ Professional mode validation passed!")
        print("\n🌐 Starting Streamlit dashboard...")
        print("📍 URL: http://localhost:8501")
        print("🔄 Press Ctrl+C to stop the server")
        print("\n" + "=" * 60)
        
        # Launch Streamlit
        venv_python = project_root / "venv" / "bin" / "python"
        if venv_python.exists():
            python_cmd = str(venv_python)
        else:
            python_cmd = sys.executable
        
        streamlit_cmd = [
            python_cmd, "-m", "streamlit", "run", 
            str(project_root / "app.py"),
            "--server.port=8501",
            "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ]
        
        # Set environment variables for professional mode
        env = os.environ.copy()
        env['PROFESSIONAL_MODE'] = 'true'
        
        subprocess.run(streamlit_cmd, cwd=project_root, env=env)
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
        return 0
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())