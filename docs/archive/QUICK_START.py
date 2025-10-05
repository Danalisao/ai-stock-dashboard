#!/usr/bin/env python3
"""
🚀 Quick Start Guide for AI Stock Trading Dashboard
Interactive tutorial to help you get started
"""

import sys
import os

def print_header():
    """Print welcome header"""
    print("\n" + "="*70)
    print("🚀 AI STOCK TRADING DASHBOARD - QUICK START GUIDE")
    print("="*70 + "\n")

def print_step(number, title, description, commands=None):
    """Print a step with formatting"""
    print(f"\n{'='*70}")
    print(f"STEP {number}: {title}")
    print(f"{'='*70}")
    print(f"\n{description}\n")
    
    if commands:
        print("Commands to run:")
        print("-" * 70)
        for cmd in commands:
            print(f"  $ {cmd}")
        print("-" * 70)

def main():
    """Run quick start guide"""
    print_header()
    
    print("This guide will help you launch your trading dashboard in 3 easy steps!")
    input("\nPress ENTER to continue...")
    
    # Step 1: Check environment
    print_step(
        1,
        "Verify Installation",
        """Let's check if your virtual environment is activated and all dependencies
are installed. You should see (venv) in your terminal prompt.""",
        [
            "source venv/bin/activate  # If not already active",
            "python --version          # Should be 3.10+",
            "pip list | grep streamlit # Should show streamlit 1.50+"
        ]
    )
    
    activated = input("\nIs your virtual environment activated? (y/n): ").lower()
    
    if activated != 'y':
        print("\n⚠️  Please activate your virtual environment first:")
        print("    $ source venv/bin/activate")
        print("\nThen run this guide again:")
        print("    $ python QUICK_START.py")
        return
    
    # Step 2: Optional configuration
    print_step(
        2,
        "Optional Configuration (Can Skip)",
        """The dashboard works with default settings, but you can optionally configure:

• Reddit API (for social sentiment)
  → Get keys at: https://www.reddit.com/prefs/apps
  
• Telegram (for alerts)
  → Get bot token from @BotFather
  
• Email SMTP (for email alerts)
  → Use Gmail or other SMTP server

If you want to configure these now, edit the .env file:""",
        ["cp .env.example .env", "nano .env  # Or use any text editor"]
    )
    
    configure = input("\nDo you want to configure APIs now? (y/n): ").lower()
    
    if configure == 'y':
        print("\n📝 Opening .env file...")
        print("Edit the file and save. Then come back here.")
        input("Press ENTER when done...")
    else:
        print("\n✅ Skipping configuration. You can always do this later!")
    
    # Step 3: Launch dashboard
    print_step(
        3,
        "Launch Dashboard",
        """Ready to launch! You have two options:

OPTION A - Use the launch script (Recommended):
  Easy, one-command launch with proper settings

OPTION B - Manual launch:
  More control over Streamlit settings

The dashboard will open at: http://localhost:8501""",
        [
            "# OPTION A:",
            "./run_dashboard.sh",
            "",
            "# OPTION B:",
            "streamlit run app.py"
        ]
    )
    
    launch = input("\nLaunch dashboard now? (y/n): ").lower()
    
    if launch == 'y':
        print("\n🚀 Launching dashboard...")
        print("Opening browser at http://localhost:8501")
        print("\n⏹️  To stop: Press Ctrl+C in the terminal\n")
        
        os.system("./run_dashboard.sh")
    else:
        print("\n✅ Setup complete! Launch when ready:")
        print("    $ ./run_dashboard.sh")
    
    # Usage tips
    print("\n" + "="*70)
    print("💡 QUICK TIPS")
    print("="*70)
    print("""
1. START WITH MONTHLY SIGNALS TAB
   → Get 0-100 scores for your watchlist
   → Clear BUY/SELL/HOLD recommendations

2. CHECK NEWS & SENTIMENT
   → See what's driving the score
   → Read article-level sentiment

3. TRACK YOUR PORTFOLIO
   → Add paper trading positions
   → Monitor P&L and performance

4. SET UP ALERTS
   → Go to Settings tab
   → Enable Desktop/Telegram/Email
   → Test alerts to verify

5. CUSTOMIZE YOUR WATCHLIST
   → Add/remove stocks in sidebar
   → Saves automatically to database

⚠️  IMPORTANT DISCLAIMERS:
• This is for EDUCATIONAL purposes only
• NOT financial advice
• Trading involves RISK - you can lose money
• Always consult a licensed financial advisor
    """)
    
    print("\n" + "="*70)
    print("🎉 You're all set! Happy trading!")
    print("="*70 + "\n")
    
    print("📚 Additional Resources:")
    print("  • README_NEW.md - Complete documentation")
    print("  • REFACTORING_COMPLETE.md - Technical details")
    print("  • config.yaml - System configuration")
    print("  • ENHANCEMENT_PLAN.md - Roadmap & features\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled. Run again when ready: python QUICK_START.py\n")
        sys.exit(0)
