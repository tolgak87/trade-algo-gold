"""
Gold Trading Bot - Main Application (MQL Bridge Version)
Broker-agnostic trading system using MT4/MT5 via MQL Bridge
"""

import sys
from src.mql_bridge import MQLBridge
from src.symbol_detector_bridge import SymbolDetector
from src.collect_account_info_bridge import collect_account_info
from src.trading_bot_bridge import TradingBot
import json


def load_trade_config():
    """Load trading configuration"""
    try:
        with open('src/configs/trade_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Failed to load config: {e}")
        return {
            "trading": {
                "desired_signal": "BOTH",
                "risk_percentage": 1.0,
                "signal_check_interval": 5,
                "position_check_interval": 5
            }
        }


def main():
    """Main application entry point"""
    print("\n" + "=" * 70)
    print("🏆 Gold Trading Bot - MQL Bridge Version")
    print("=" * 70)
    print("Broker-Agnostic System: Works with any MT4/MT5 broker")
    print("=" * 70)
    
    # Pre-flight check
    print("\n🚀 Starting in 3 seconds...")
    print("\n⚠️  BEFORE STARTING:")
    print("   1. Open your MT4 or MT5 terminal")
    print("   2. Make sure PythonBridge EA is attached to a chart")
    print("   3. Make sure 'AutoTrading' button is enabled")
    print()
    input("Press ENTER when ready (or Ctrl+C to cancel)...")
    
    # Load configuration
    config = load_trade_config()
    trading_config = config.get('trading', {})
    
    # Step 1: Start MQL Bridge
    print("\n[1/5] Starting MQL Bridge Server...")
    bridge = MQLBridge(host='127.0.0.1', port=9090)
    
    if not bridge.start():
        print("❌ Failed to start MQL Bridge")
        return
    
    # Step 2: Wait for EA connection
    print("\n[2/5] Waiting for MT4/MT5 EA connection...")
    print("\n📋 Checklist:")
    print("   ✓ Bridge server started on 127.0.0.1:9090")
    print("   ? Is MT4/MT5 terminal running?")
    print("   ? Is PythonBridge EA compiled?")
    print("   ? Is PythonBridge EA attached to a chart?")
    print("   ? Check EA Experts tab for connection messages")
    print()
    
    if not bridge.wait_for_connection(timeout=60):
        print("\n❌ No EA connection within timeout")
        print("\n🔧 Troubleshooting:")
        print("   1. Open MT4/MT5 terminal")
        print("   2. Go to File → Open Data Folder")
        print("   3. Copy PythonBridge_MT5.mq5 (or MT4 version) to MQL5/Experts (or MQL4/Experts)")
        print("   4. Compile the EA (F7)")
        print("   5. Drag EA to any chart")
        print("   6. Check 'Experts' tab for messages:")
        print("      - Should see: 'PythonBridge: Connecting to 127.0.0.1:9090'")
        print("      - Should see: 'PythonBridge: Connected to Python'")
        print("   7. Make sure 'AutoTrading' is enabled (button on toolbar)")
        print("   8. Check Windows Firewall - port 9090 must be allowed")
        print("\n📖 For detailed guide, see: README_BRIDGE.md")
        bridge.stop()
        return
    
    # Step 3: Detect symbol
    print("\n[3/5] Detecting trading symbol...")
    detector = SymbolDetector()
    symbol = detector.detect_symbol(bridge)
    
    if not symbol:
        print("❌ No trading symbol detected")
        bridge.stop()
        return
    
    # Step 4: Collect account info
    print("\n[4/5] Collecting account information...")
    if not collect_account_info(bridge):
        print("⚠️  Account info collection failed, using defaults")
    
    # Step 5: Initialize Trading Bot
    print("\n[5/5] Initializing Trading Bot...")
    bot = TradingBot(bridge)
    
    if not bot.initialize():
        print("❌ Bot initialization failed")
        bridge.stop()
        return
    
    # Display bot status
    bot.display_status()
    
    # Trading parameters
    desired_signal = trading_config.get('desired_signal', 'BOTH')
    risk_percentage = trading_config.get('risk_percentage', 1.0)
    signal_check = trading_config.get('signal_check_interval', 5)
    position_check = trading_config.get('position_check_interval', 5)
    
    print("\n" + "=" * 70)
    print("📋 Trading Configuration:")
    print(f"   Signal Mode: {desired_signal}")
    print(f"   Risk per Trade: {risk_percentage}%")
    print(f"   Signal Check Interval: {signal_check}s")
    print(f"   Position Monitor Interval: {position_check}s")
    print("=" * 70)
    
    # Main menu
    while True:
        print("\n" + "=" * 70)
        print("🎛️  TRADING BOT MENU")
        print("=" * 70)
        print("1. 🚀 Start Full Auto-Trading Cycle")
        print("2. 📊 Refresh Market Data")
        print("3. 🔮 Display Current SAR Signal")
        print("4. 💰 Manual Trade (BUY)")
        print("5. 💸 Manual Trade (SELL)")
        print("6. 📈 View Open Positions")
        print("7. ⚙️  Bot Status")
        print("8. 🛑 Exit")
        print("=" * 70)
        
        choice = input("\nSelect option (1-8): ").strip()
        
        if choice == '1':
            # Full auto-trading
            print("\n🚀 Starting full auto-trading cycle...")
            try:
                bot.full_auto_trading_cycle(
                    desired_signal=desired_signal,
                    risk_percentage=risk_percentage,
                    signal_check_interval=signal_check,
                    position_check_interval=position_check
                )
            except KeyboardInterrupt:
                print("\n\n⚠️  Auto-trading stopped by user")
        
        elif choice == '2':
            # Refresh data
            bot.refresh_data()
            bot.display_status()
        
        elif choice == '3':
            # Display SAR signal
            signal = bot.get_sar_signal()
            if signal:
                print(f"\n🔮 Current SAR Signal: {signal}")
                sar_info = bot.sar_info
                if sar_info:
                    print(f"   Price: {sar_info['current_price']}")
                    print(f"   SAR Value: {sar_info['sar_value']}")
                    print(f"   Trend: {sar_info['trend']}")
            else:
                print("\n⚠️  No signal available")
        
        elif choice == '4':
            # Manual BUY
            confirm = input("\n⚠️  Execute BUY order? (yes/no): ").strip().lower()
            if confirm == 'yes':
                result = bot.execute_trade('BUY', risk_percentage, use_sar_sl=True)
                if result and result.get('success'):
                    print(f"\n✅ BUY order placed: Ticket #{result['order_id']}")
        
        elif choice == '5':
            # Manual SELL
            confirm = input("\n⚠️  Execute SELL order? (yes/no): ").strip().lower()
            if confirm == 'yes':
                result = bot.execute_trade('SELL', risk_percentage, use_sar_sl=True)
                if result and result.get('success'):
                    print(f"\n✅ SELL order placed: Ticket #{result['order_id']}")
        
        elif choice == '6':
            # View positions
            positions = bot.get_open_positions()
            if positions:
                print(f"\n📊 Open Positions ({len(positions)}):")
                for pos in positions:
                    print(f"   Ticket: {pos.get('ticket')} | {pos.get('pos_type')} | "
                          f"Vol: {pos.get('volume')} | P/L: ${pos.get('profit', 0):.2f}")
            else:
                print("\n📊 No open positions")
        
        elif choice == '7':
            # Bot status
            bot.display_status()
        
        elif choice == '8':
            # Exit
            confirm = input("\n⚠️  Stop bot and exit? (yes/no): ").strip().lower()
            if confirm == 'yes':
                break
        
        else:
            print("❌ Invalid choice. Please select 1-8.")
    
    # Cleanup
    print("\n🛑 Shutting down...")
    bridge.stop()
    print("✅ Bot stopped successfully")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
