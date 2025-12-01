"""
Dashboard-Enabled Trading Bot Launcher
Runs trading bot with real-time web dashboard

🔧 BACKTEST MODE: Set BACKTEST_MODE = True to test on historical data
"""

from src.trading_bot import TradingBot
from src.web_ui.dashboard_server import initialize_dashboard
from datetime import datetime, timedelta
import time

# ============================================================
# 🎚️ TOGGLE BACKTEST MODE HERE
# ============================================================
BACKTEST_MODE = False  # Set to True to run backtest instead of live trading
# ============================================================


def main():
    """
    Main entry point with dashboard
    """
    if BACKTEST_MODE:
        run_backtest_mode()
    else:
        run_live_trading_mode()


def run_backtest_mode():
    """
    Run backtesting mode on historical data
    """
    print("\n" + "="*70)
    print("🔬 GOLD TRADING BOT - BACKTEST MODE")
    print("="*70)
    
    from src.backtest.backtest_engine import BacktestEngine
    
    # Backtest configuration
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # Last 3 months
    
    print(f"\n⚙️  Backtest Configuration:")
    print(f"   Symbol: XAUUSD")
    print(f"   Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"   Strategy: Parabolic SAR (15M timeframe)")
    print(f"   Initial Balance: $10,000")
    print(f"   Risk per Trade: 1%")
    print(f"   Signals: BOTH (BUY and SELL)")
    
    # Create and run backtest
    engine = BacktestEngine(
        symbol="XAUUSD",
        initial_balance=10000.0,
        risk_percentage=1.0
    )
    
    try:
        result = engine.run_backtest(
            start_date=start_date,
            end_date=end_date,
            desired_signal='BOTH'
        )
        
        # Display results
        result.print_summary()
        result.print_monthly_breakdown()
        result.save_to_file()
        
        # Recommendations
        print("\n💡 Next Steps:")
        if result.return_percentage > 0:
            print("   ✅ Strategy is profitable on historical data")
            print("   ✅ Set BACKTEST_MODE = False in dashboard_app.py to trade live")
        else:
            print("   ❌ Strategy needs improvement")
            print("   💡 Try running backtest_app.py to test different parameters")
        
    except Exception as e:
        print(f"\n❌ Backtest failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)


def run_live_trading_mode():
    """
    Run live trading mode with dashboard
    """
    print("\n" + "="*70)
    print("🌐 GOLD TRADING BOT - LIVE TRADING MODE")
    print("="*70)
    
    # Step 1: Initialize and start dashboard server
    print("\n[Step 1/3] Starting web dashboard server...")
    dashboard = initialize_dashboard(host='127.0.0.1', port=5000)
    time.sleep(2)  # Give server time to start
    
    print(f"\n✅ Dashboard ready at: {dashboard.get_url()}")
    print("   Open this URL in your browser to monitor trading")
    
    # Step 2: Initialize trading bot with dashboard
    print("\n[Step 2/3] Initializing trading bot...")
    bot = TradingBot(dashboard=dashboard)
    
    if not bot.initialize():
        print("\n❌ Bot initialization failed. Exiting...")
        return
    
    dashboard.update_bot_status("Bot initialized successfully")
    dashboard.send_notification("Trading bot started", "success")
    
    # Step 3: Display status and start trading
    print("\n[Step 3/3] Starting automated trading cycle...")
    bot.display_status()
    
    # Configuration
    desired_signal = 'BUY'  # Change to 'SELL' if you want to wait for sell signals
    risk_percentage = 1.0   # Risk 1% per trade
    signal_check_interval = 30  # Check for signals every 30 seconds
    position_check_interval = 5  # Monitor position every 5 seconds
    
    print(f"\n📋 Trading Configuration:")
    print(f"   Target Signal: {desired_signal}")
    print(f"   Risk per trade: {risk_percentage}%")
    print(f"   Signal check: Every {signal_check_interval} seconds")
    print(f"   Position monitoring: Every {position_check_interval} seconds")
    print(f"\n🌐 Dashboard: {dashboard.get_url()}")
    print(f"=" * 70)
    
    # Start full automated trading cycle
    bot.full_auto_trading_cycle(
        desired_signal=desired_signal,
        risk_percentage=risk_percentage,
        signal_check_interval=signal_check_interval,
        position_check_interval=position_check_interval
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Bot stopped by user")
        print("👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
