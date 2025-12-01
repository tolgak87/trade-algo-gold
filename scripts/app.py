"""
Main application entry point for Gold Trading Bot

Usage: Run from project root directory
    python scripts/app.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.trading_bot import TradingBot


def main():
    """
    Main application entry point for Gold Trading Bot
    """
    # Initialize trading bot
    bot = TradingBot()
    
    if not bot.initialize():
        print("❌ Bot initialization failed")
        return
    
    # Display bot status
    bot.display_status()
    
    # FULL AUTO-TRADING CYCLE
    # Change 'BUY' to 'SELL' for short positions when market is downtrend
    bot.full_auto_trading_cycle(
        desired_signal='BUY',          # 'BUY' for long | 'SELL' for short
        risk_percentage=1.0,
        signal_check_interval=30,      # Check for signals every 30s
        position_check_interval=5      # Monitor position every 5s
    )
    

if __name__ == "__main__":
    main()
