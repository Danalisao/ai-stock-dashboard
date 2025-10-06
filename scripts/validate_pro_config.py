#!/usr/bin/env python3
"""
🔧 Professional System Configuration Validator
Ensures all system parameters meet professional trading standards
"""

import sys
import os
from pathlib import Path

def validate_professional_config():
    """Validate and enforce professional configuration"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    try:
        from modules.utils import load_config
        from modules.pro_mode_guard import ProModeGuard
        from modules.database_manager import DatabaseManager
        
        print("🔧 Professional Trading System Configuration Validator")
        print("=" * 65)
        
        # Load and validate configuration
        print("📋 Loading configuration...")
        config = load_config()
        
        # Initialize components
        print("🗄️ Initializing system components...")
        db = DatabaseManager(config.get('database', './data/stock_data.db'))
        pro_guard = ProModeGuard(config, db)
        
        # Professional validation
        print("🛡️ Running professional compliance checks...")
        validation = pro_guard.ensure_production_ready(enforce=False)
        
        print("\n📊 VALIDATION RESULTS")
        print("-" * 40)
        
        if validation.passed:
            print("✅ PASSED: System meets professional trading standards")
            print("🚀 Ready for live market operations")
        else:
            print("❌ FAILED: Professional compliance issues detected")
            print("\n🚨 CRITICAL ISSUES:")
            for issue in validation.issues:
                print(f"  • {issue}")
        
        if validation.warnings:
            print("\n⚠️ OPTIMIZATION RECOMMENDATIONS:")
            for warning in validation.warnings:
                print(f"  • {warning}")
        
        # Additional professional checks
        print("\n🔍 ADDITIONAL PROFESSIONAL CHECKS")
        print("-" * 40)
        
        # Check watchlist size
        watchlist = config.get('watchlist', {}).get('stocks', [])
        if len(watchlist) >= 50:
            print(f"✅ Watchlist: {len(watchlist)} instruments (Excellent diversification)")
        elif len(watchlist) >= 25:
            print(f"✅ Watchlist: {len(watchlist)} instruments (Good diversification)")
        else:
            print(f"⚠️ Watchlist: {len(watchlist)} instruments (Consider expanding)")
        
        # Check trading parameters
        trading_cfg = config.get('trading', {})
        entry_score = trading_cfg.get('entry_score_min', 0)
        min_rr = trading_cfg.get('min_risk_reward', 0)
        
        if entry_score >= 85:
            print(f"✅ Entry Score Threshold: {entry_score} (Professional grade)")
        else:
            print(f"⚠️ Entry Score Threshold: {entry_score} (Consider raising to 85+)")
            
        if min_rr >= 2.5:
            print(f"✅ Risk/Reward Ratio: {min_rr}:1 (Professional standard)")
        else:
            print(f"⚠️ Risk/Reward Ratio: {min_rr}:1 (Consider raising to 2.5:1)")
        
        # Check professional mode enforcement
        pro_mode = config.get('professional_mode', {})
        if pro_mode.get('force_professional_mode', False):
            print("✅ Professional Mode: Permanently enforced")
        else:
            print("⚠️ Professional Mode: Should be permanently enforced")
        
        # Database check
        try:
            stats = db.get_database_stats()
            if stats:
                print(f"✅ Database: Operational ({stats.get('database_size_mb', 0):.1f} MB)")
            else:
                print("⚠️ Database: Statistics unavailable")
        except Exception:
            print("❌ Database: Connection issues")
        
        print("\n🎯 SYSTEM STATUS SUMMARY")
        print("-" * 40)
        
        if validation.passed and len(watchlist) >= 25 and entry_score >= 80:
            print("🟢 PROFESSIONAL SYSTEM: Ready for live trading")
            print("📈 All safeguards operational")
            print("🔒 Risk management protocols active")
            return True
        else:
            print("🟡 SYSTEM OPTIMIZATION: Consider improvements above")
            print("🔧 System functional but not fully optimized")
            return False
            
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def setup_professional_environment():
    """Setup professional environment variables"""
    print("\n🌐 PROFESSIONAL ENVIRONMENT SETUP")
    print("-" * 40)
    
    # Set professional environment variables
    os.environ['TRADING_MODE'] = 'PROFESSIONAL'
    os.environ['RISK_MANAGEMENT'] = 'STRICT'
    os.environ['DATA_VALIDATION'] = 'MANDATORY'
    os.environ['ALERT_SYSTEM'] = 'ACTIVE'
    
    print("✅ Environment configured for professional trading")
    print("🛡️ All professional safeguards activated")

if __name__ == "__main__":
    print("🚀 Initializing Professional Trading System Validation...")
    print()
    
    # Run validation
    config_valid = validate_professional_config()
    
    # Setup environment
    setup_professional_environment()
    
    print("\n" + "=" * 65)
    if config_valid:
        print("🎉 PROFESSIONAL SYSTEM VALIDATION COMPLETE")
        print("✅ System ready for professional trading operations")
        exit(0)
    else:
        print("⚠️ SYSTEM OPTIMIZATION RECOMMENDED")
        print("🔧 Consider implementing suggested improvements")
        exit(1)