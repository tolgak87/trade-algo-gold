"""
Test script for Circuit Breaker functionality
Tests loss detection and pause mechanisms

Usage: Run from project root directory
    python scripts/test_circuit_breaker.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.circuit_breaker import CircuitBreaker
from src.trade_logger import TradeLogger
from src.email_notifier import load_email_config


def main():
    print("=" * 70)
    print("🧪 CIRCUIT BREAKER TEST")
    print("=" * 70)
    
    # Initialize
    logger = TradeLogger()
    breaker = CircuitBreaker(logger)
    
    # Initialize email notifier
    try:
        email_notifier = load_email_config()
        print(f"📧 Email notifications: {'✅ Enabled' if email_notifier.enabled else '❌ Disabled'}")
    except:
        email_notifier = None
        print("📧 Email notifications: ❌ Disabled (no config)")
    
    # Display current configuration
    print("\n📋 Configuration:")
    config = breaker.config["circuit_breaker"]
    print(f"   Rule 1: {config['consecutive_loss_threshold_1']} consecutive losses → {config['consecutive_loss_pause_hours_1']}h pause")
    print(f"   Rule 2: {config['consecutive_loss_threshold_2']} consecutive losses → {config['consecutive_loss_pause_hours_2']}h pause")
    print(f"   Rule 3: {config['percentage_loss_threshold']}% losses in {config['percentage_loss_window']} trades → {config['percentage_loss_pause_hours']}h pause")
    
    # Display current status
    print("\n" + "=" * 70)
    breaker.display_status()
    
    # Check if trading is allowed
    print("\n📊 Trading Status Check:")
    allowed, reason = breaker.is_trading_allowed(email_notifier)
    
    if allowed:
        print("   ✅ Trading is ALLOWED")
    else:
        print(f"   🔴 Trading is BLOCKED")
        print(f"   Reason: {reason}")
        if email_notifier and email_notifier.enabled:
            print("   📧 Circuit breaker email sent!")
    
    # Check daily loss limit
    print("\n💰 Daily Loss Limit Check:")
    current_balance = 10000.0
    allowed, reason = breaker.check_daily_loss_limit(current_balance)
    
    if allowed:
        print("   ✅ Daily loss limit OK")
    else:
        print(f"   🔴 Daily loss limit reached")
        print(f"   Reason: {reason}")
    
    # Display today's trade statistics
    print("\n📈 Today's Trade Statistics:")
    stats = logger.get_trade_statistics()
    print(f"   Total Trades: {stats['total_trades']}")
    print(f"   Closed Trades: {stats['closed_trades']}")
    print(f"   Winning Trades: {stats['winning_trades']}")
    print(f"   Losing Trades: {stats['losing_trades']}")
    print(f"   Win Rate: {stats['win_rate']}%")
    print(f"   Total Profit: ${stats['total_profit']}")
    
    print("\n" + "=" * 70)
    print("✅ Circuit Breaker test completed")
    print("=" * 70)
    
    # Auto-send test email
    if email_notifier and email_notifier.enabled:
        print("\n📧 Sending test email notification...")
        
        # Get real statistics for test email
        stats = logger.get_trade_statistics()
        
        test_data = {
            "reason": "TEST: 5 consecutive losses (threshold: 5)",
            "pause_hours": 3,
            "consecutive_losses": 5,
            "percentage_losses": "60.0",
            "total_pauses": 1,
            "total_daily_loss": stats.get('total_profit', -250.0),  # Use real or default
            "current_balance": 11609.29  # Current balance from account
        }
        
        if email_notifier.notify_circuit_breaker(test_data):
            print("   ✅ Test email sent successfully!")
            print(f"   📬 Check: {email_notifier.recipient_email}")
        else:
            print("   ❌ Failed to send test email")
    
    # Force reset option (for testing)
    print("\n⚠️  To force reset circuit breaker (use with caution):")
    print("   breaker.force_reset()")


if __name__ == "__main__":
    main()
