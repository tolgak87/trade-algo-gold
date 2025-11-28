"""
Dashboard-Enabled Trading Bot Launcher
Runs trading bot with real-time web dashboard
"""

from src.trading_bot import TradingBot
from src.dashboard_server import initialize_dashboard
import time


def main():
    """
    Main entry point with dashboard
    """
    print("\n" + "="*70)
    print("🌐 GOLD TRADING BOT WITH WEB DASHBOARD")
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
    desired_signal = 'SELL'  # Change to 'SELL' if you want to wait for sell signals
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
        print("\n\n⚠️  Trading bot stopped by user")
        print("👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
