"""
Reset Circuit Breaker - Clean Start
Clears circuit breaker state and optionally clears today's trade logs
"""

import os
import json
from datetime import datetime


def reset_circuit_breaker():
    """Reset circuit breaker state and optionally clear logs"""
    
    print("=" * 70)
    print("🔄 CIRCUIT BREAKER RESET")
    print("=" * 70)
    
    # 1. Reset circuit breaker state
    state_file = "circuit_breaker_state.json"
    
    if os.path.exists(state_file):
        os.remove(state_file)
        print("\n✅ Circuit breaker state cleared")
    else:
        print("\n⚠️  No circuit breaker state file found")
    
    # 2. Ask about trade logs
    print("\n📋 What do you want to do with trade logs?")
    print("1️⃣  Keep all trade logs (recommended)")
    print("2️⃣  Clear today's trade logs only")
    print("3️⃣  Clear ALL trade logs (careful!)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "2":
        # Clear today's log
        today_file = f"trade_logs/trades_{datetime.now().strftime('%Y_%m_%d')}.json"
        if os.path.exists(today_file):
            os.remove(today_file)
            print(f"✅ Today's trade log cleared: {today_file}")
        else:
            print(f"⚠️  No trade log found for today")
    
    elif choice == "3":
        # Clear all logs
        confirm = input("⚠️  Are you sure? This will delete ALL trade history! (yes/no): ").strip().lower()
        if confirm == "yes":
            log_dir = "trade_logs"
            if os.path.exists(log_dir):
                for file in os.listdir(log_dir):
                    if file.endswith(".json"):
                        os.remove(os.path.join(log_dir, file))
                print(f"✅ All trade logs cleared from {log_dir}/")
            else:
                print("⚠️  No trade_logs directory found")
        else:
            print("❌ Cancelled - trade logs kept")
    
    else:
        print("✅ Trade logs kept intact")
    
    print("\n" + "=" * 70)
    print("✅ RESET COMPLETE - Ready for fresh start!")
    print("=" * 70)
    print("\n💡 Now you can run: python dashboard_app.py")


if __name__ == "__main__":
    reset_circuit_breaker()
