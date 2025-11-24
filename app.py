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
    
    # Wait for BUY signal and auto-trade (30 second checks, unlimited wait)
    result = bot.auto_trade_on_signal(
        desired_signal='BUY',
        risk_percentage=1.0,
        use_sar_sl=True,
        check_interval=30,
        max_wait_minutes=0  # 0 = unlimited (Ctrl+C to stop)
    )
    

if __name__ == "__main__":
    main()
