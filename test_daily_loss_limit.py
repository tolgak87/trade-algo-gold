"""
Test Daily Loss Limit System
Demonstrates daily loss tracking and automatic pause
"""

import MetaTrader5 as mt5
from datetime import datetime
from src.trade_logger import TradeLogger
from src.circuit_breaker import CircuitBreaker


def test_daily_loss_limit():
    """Test daily loss limit functionality"""
    
    print("\n" + "=" * 70)
    print("🧪 DAILY LOSS LIMIT TEST")
    print("=" * 70)
    
    # Initialize MT5
    if not mt5.initialize():
        print("❌ Failed to initialize MT5")
        return
    
    # Get account info
    account_info = mt5.account_info()
    if account_info is None:
        print("❌ Failed to get account info")
        mt5.shutdown()
        return
    
    current_balance = account_info.balance
    print(f"\n📊 Current Account Balance: ${current_balance:.2f}")
    
    mt5.shutdown()
    
    # Initialize circuit breaker
    logger = TradeLogger()
    breaker = CircuitBreaker(logger)
    
    # Check if there are trades today and show starting balance
    first_trade_balance = logger.get_first_trade_balance()
    if first_trade_balance:
        print(f"📅 Starting Balance (from first trade today): ${first_trade_balance:.2f}")
        diff = current_balance - first_trade_balance
        if diff < 0:
            print(f"📉 Daily Change: -${abs(diff):.2f} ({(diff/first_trade_balance)*100:.2f}%)")
        elif diff > 0:
            print(f"📈 Daily Change: +${diff:.2f} (+{(diff/first_trade_balance)*100:.2f}%)")
        else:
            print(f"📊 Daily Change: $0.00 (0%)")
    else:
        print(f"ℹ️  No trades yet today - will use ${current_balance:.2f} as starting balance")
    
    # Display current status
    breaker.display_status()
    
    # Check daily loss limit
    print("\n" + "-" * 70)
    print("🔍 Checking Daily Loss Limit...")
    print("-" * 70)
    
    allowed, reason = breaker.check_daily_loss_limit(current_balance)
    
    # Get trade statistics
    stats = logger.get_trade_statistics()
    total_daily_profit = stats.get('total_profit', 0)
    
    if allowed:
        print("✅ Daily loss limit OK - Trading allowed")
        
        # Show how much loss is remaining before limit
        cfg = breaker.config["daily_loss_limit"]
        starting_balance = breaker.state.get("daily_starting_balance", current_balance)
        
        if cfg["use_percentage"]:
            max_loss_pct = cfg["max_daily_loss_percentage"]
            max_loss_amount = starting_balance * max_loss_pct / 100
            current_loss = abs(total_daily_profit) if total_daily_profit < 0 else 0
            remaining = max_loss_amount - current_loss
            
            print(f"\n💡 Daily Loss Limit Details:")
            print(f"   Starting Balance: ${starting_balance:.2f}")
            print(f"   Max Loss Allowed: {max_loss_pct}% (${max_loss_amount:.2f})")
            print(f"   Current Loss (from trades): ${current_loss:.2f}")
            
            if total_daily_profit > 0:
                print(f"   ✅ Daily Profit: ${total_daily_profit:.2f}")
            
            print(f"   Remaining: ${remaining:.2f} ({(remaining/starting_balance)*100:.1f}%)")
        else:
            max_loss = cfg["max_daily_loss_dollars"]
            current_loss = abs(total_daily_profit) if total_daily_profit < 0 else 0
            remaining = max_loss - current_loss
            
            print(f"\n💡 Daily Loss Limit Details:")
            print(f"   Starting Balance: ${starting_balance:.2f}")
            print(f"   Max Loss Allowed: ${max_loss}")
            print(f"   Current Loss (from trades): ${current_loss:.2f}")
            
            if total_daily_profit > 0:
                print(f"   ✅ Daily Profit: ${total_daily_profit:.2f}")
            
            print(f"   Remaining: ${remaining:.2f}")
    else:
        print(f"🔴 Daily loss limit REACHED!")
        print(f"   {reason}")
        print(f"\n⏸️  Trading paused until next day (midnight)")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
    
    # Show configuration
    print(f"\n⚙️  Current Configuration:")
    print(f"   Enabled: {breaker.config['daily_loss_limit']['enabled']}")
    print(f"   Use Percentage: {breaker.config['daily_loss_limit']['use_percentage']}")
    print(f"   Max Loss %: {breaker.config['daily_loss_limit']['max_daily_loss_percentage']}%")
    print(f"   Max Loss $: ${breaker.config['daily_loss_limit']['max_daily_loss_dollars']}")
    
    print(f"\n💡 To change settings, edit: protection_config.json")


if __name__ == "__main__":
    test_daily_loss_limit()
