"""
Create demo trades for testing Circuit Breaker
This creates sample closed trades to test loss detection

Usage: Run from project root directory
    python scripts/create_demo_trades.py
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_demo_trades():
    """Create demo trades with various profit/loss scenarios"""
    
    # Base time
    now = datetime.now()
    
    # Scenario 1: 5 consecutive losses (should trigger 3h pause)
    demo_trades_consecutive = []
    
    for i in range(5):
        trade_time = now - timedelta(hours=5-i)
        demo_trades_consecutive.append({
            "trade_id": f"demo_{1000+i}_demo_{2000+i}",
            "order_id": 1000 + i,
            "deal_id": 2000 + i,
            "symbol": "XAUUSD",
            "type": "BUY",
            "status": "CLOSED",
            "entry_time": trade_time.isoformat(),
            "entry_date": trade_time.strftime("%Y-%m-%d"),
            "entry_time_display": trade_time.strftime("%Y-%m-%d %H:%M:%S"),
            "entry_price": 2650.0,
            "volume": 0.1,
            "leverage": 100,
            "stop_loss": 2645.0,
            "take_profit": 2660.0,
            "exit_time": (trade_time + timedelta(minutes=30)).isoformat(),
            "exit_date": (trade_time + timedelta(minutes=30)).strftime("%Y-%m-%d"),
            "exit_time_display": (trade_time + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "exit_price": 2645.0,  # Hit SL
            "close_reason": "Stop Loss Hit",
            "profit_loss": -50.0,  # Loss
            "profit_loss_pips": -5.0,
            "profit_loss_percentage": -0.19,
            "duration_seconds": 1800,
            "duration_display": "30m 0s",
            "account_balance_at_entry": 10000.0,
            "account_equity_at_entry": 10000.0,
            "account_balance_at_exit": 9950.0 - (i * 50),
            "account_equity_at_exit": 9950.0 - (i * 50),
            "account_currency": "USD",
            "risk_info": None,
            "comment": f"Demo Loss #{i+1}",
            "magic_number": 234000,
            "server": "Demo-Server",
            "login": 99999
        })
    
    # Scenario 2: 70% losses in last 10 trades (7 losses, 3 wins)
    demo_trades_percentage = []
    
    for i in range(10):
        trade_time = now - timedelta(hours=10-i)
        is_loss = i < 7  # First 7 are losses
        
        demo_trades_percentage.append({
            "trade_id": f"demo_{3000+i}_demo_{4000+i}",
            "order_id": 3000 + i,
            "deal_id": 4000 + i,
            "symbol": "XAUUSD",
            "type": "BUY",
            "status": "CLOSED",
            "entry_time": trade_time.isoformat(),
            "entry_date": trade_time.strftime("%Y-%m-%d"),
            "entry_time_display": trade_time.strftime("%Y-%m-%d %H:%M:%S"),
            "entry_price": 2650.0,
            "volume": 0.1,
            "leverage": 100,
            "stop_loss": 2645.0,
            "take_profit": 2660.0,
            "exit_time": (trade_time + timedelta(minutes=30)).isoformat(),
            "exit_date": (trade_time + timedelta(minutes=30)).strftime("%Y-%m-%d"),
            "exit_time_display": (trade_time + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "exit_price": 2645.0 if is_loss else 2660.0,
            "close_reason": "Stop Loss Hit" if is_loss else "Take Profit Hit",
            "profit_loss": -50.0 if is_loss else 100.0,
            "profit_loss_pips": -5.0 if is_loss else 10.0,
            "profit_loss_percentage": -0.19 if is_loss else 0.38,
            "duration_seconds": 1800,
            "duration_display": "30m 0s",
            "account_balance_at_entry": 10000.0,
            "account_equity_at_entry": 10000.0,
            "account_balance_at_exit": 9950.0 if is_loss else 10100.0,
            "account_equity_at_exit": 9950.0 if is_loss else 10100.0,
            "account_currency": "USD",
            "risk_info": None,
            "comment": f"Demo {'Loss' if is_loss else 'Win'} #{i+1}",
            "magic_number": 234000,
            "server": "Demo-Server",
            "login": 99999
        })
    
    print("=" * 70)
    print("🎮 DEMO TRADE SCENARIOS")
    print("=" * 70)
    print("\n📋 Choose a scenario to test:\n")
    print("1️⃣  5 Consecutive Losses")
    print("   → Should trigger: 3 hour pause")
    print("   → Reason: 5 consecutive losses\n")
    
    print("2️⃣  70% Losses in 10 Trades (7 losses, 3 wins)")
    print("   → Should trigger: 5 hour pause")
    print("   → Reason: 70% losses in last 10 trades\n")
    
    print("3️⃣  Both scenarios combined")
    print("   → Test multiple triggers\n")
    
    print("4️⃣  Clean slate (remove demo trades)")
    print("   → Start fresh\n")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        save_demo_trades(demo_trades_consecutive, "consecutive")
    elif choice == "2":
        save_demo_trades(demo_trades_percentage, "percentage")
    elif choice == "3":
        save_demo_trades(demo_trades_consecutive + demo_trades_percentage, "combined")
    elif choice == "4":
        clean_demo_trades()
    else:
        print("❌ Invalid choice")


def save_demo_trades(trades, scenario_name):
    """Save demo trades to today's log file"""
    log_file = f"logs/trade_logs/trades_{datetime.now().strftime('%Y_%m_%d')}.json"
    
    # Read existing trades
    try:
        with open(log_file, 'r') as f:
            existing_trades = json.load(f)
    except:
        existing_trades = []
    
    # Remove old demo trades
    existing_trades = [t for t in existing_trades if not t.get("trade_id", "").startswith("demo_")]
    
    # Add new demo trades
    existing_trades.extend(trades)
    
    # Save
    with open(log_file, 'w') as f:
        json.dump(existing_trades, f, indent=4)
    
    print(f"\n✅ Demo trades saved ({scenario_name} scenario)")
    print(f"   File: {log_file}")
    print(f"   Demo trades: {len(trades)}")
    print(f"\n💡 Now run: python test_circuit_breaker.py")


def clean_demo_trades():
    """Remove demo trades from today's log"""
    log_file = f"logs/trade_logs/trades_{datetime.now().strftime('%Y_%m_%d')}.json"
    
    try:
        with open(log_file, 'r') as f:
            existing_trades = json.load(f)
        
        # Remove demo trades
        real_trades = [t for t in existing_trades if not t.get("trade_id", "").startswith("demo_")]
        
        # Save
        with open(log_file, 'w') as f:
            json.dump(real_trades, f, indent=4)
        
        print(f"\n✅ Demo trades removed")
        print(f"   Real trades remaining: {len(real_trades)}")
    except:
        print("❌ No log file found")


if __name__ == "__main__":
    create_demo_trades()
