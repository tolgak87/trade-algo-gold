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
    
    # ⚠️ CAUTION: Uncomment below to place REAL orders
    """
    # Example 1: Execute BUY order with SAR-based Stop Loss
    result = bot.execute_trade(
        position_type='BUY',
        risk_percentage=1.0,
        use_sar_sl=True
    )
    
    # Example 2: Execute SELL order with standard Stop Loss
    # result = bot.execute_trade(
    #     position_type='SELL',
    #     risk_percentage=1.0,
    #     use_sar_sl=False
    # )
    
    # Example 3: Get current SAR signal
    # signal = bot.get_sar_signal()
    # if signal == 'BUY':
    #     bot.execute_trade('BUY', risk_percentage=1.0, use_sar_sl=True)
    # elif signal == 'SELL':
    #     bot.execute_trade('SELL', risk_percentage=1.0, use_sar_sl=True)
    
    # Example 4: Refresh data and check again
    # bot.refresh_data()
    # bot.display_status()
    """


if __name__ == "__main__":
    main()
