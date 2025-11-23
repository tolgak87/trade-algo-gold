from src.collect_account_info import collect_account_info
from src.symbol_detector import SymbolDetector
from src.order_executor import OrderExecutor
from src.risk_manager import RiskManager
from src.trade_logger import TradeLogger
import MetaTrader5 as mt5
import json
from datetime import datetime

def main():
    """
    Main application entry point for Gold Trading Bot
    """
    print("=" * 60)
    print("🏆 Gold Trading Bot - Starting...")
    print("=" * 60)
    
    # Step 1: Detect available gold symbols
    print("\n[1/5] Detecting gold symbols...")
    detector = SymbolDetector()
    gold_symbol = detector.detect_gold_symbol()
    
    if not gold_symbol:
        print("❌ Failed to detect gold symbol. Exiting...")
        return
    
    # Step 2: Collect account information
    print("\n[2/5] Collecting account information...")
    account_success = collect_account_info()
    
    if not account_success:
        print("\n❌ Failed to collect account information")
        return
    
    # Get account balance for position sizing
    try:
        with open('account_info.json', 'r') as f:
            account_data = json.load(f)
            account_balance = account_data.get('balance', 10000.0)
    except:
        account_balance = 10000.0  # Default balance
    
    # Step 3: Initialize Trade Logger
    print("\n[3/5] Initializing trade logging system...")
    trade_logger = TradeLogger(log_directory="trade_logs")
    print("✅ Trade logging enabled - Daily JSON files")
    
    # Show today's statistics
    stats = trade_logger.get_trade_statistics()
    print(f"📊 Today's Stats: {stats['total_trades']} trades | Win Rate: {stats['win_rate']}%")
    
    # Step 4: Initialize Risk Management (1:2 ratio)
    print("\n[4/5] Initializing risk management...")
    risk_manager = RiskManager(gold_symbol, risk_reward_ratio=2.0)
    print("✅ Risk-Reward Ratio: 1:2")
    
    # Step 5: Execute BUY order with automatic SL/TP (optional - uncomment to activate)
    print("\n[5/5] Order execution ready...")
    executor = OrderExecutor(gold_symbol, trade_logger=trade_logger)
    
    # ⚠️ CAUTION: Uncomment below to place REAL orders
    """
    # Get current price
    if not mt5.initialize():
        print("❌ Failed to initialize MT5")
        return
    
    tick = mt5.symbol_info_tick(gold_symbol)
    if tick is None:
        print("❌ Failed to get current price")
        mt5.shutdown()
        return
    
    entry_price = tick.ask
    mt5.shutdown()
    
    # Method 1: Calculate SL/TP by points (50 points risk, 100 points reward)
    sl, tp = risk_manager.calculate_sl_tp_by_points(entry_price, 50)
    
    # Method 2: Calculate SL/TP by price (manual SL price)
    # sl, tp = risk_manager.calculate_sl_tp_by_price(entry_price, 2645.00)
    
    # Method 3: Calculate SL/TP by percentage (0.5% risk, 1.0% reward)
    # sl, tp = risk_manager.calculate_sl_tp_by_percentage(entry_price, 0.5)
    
    # Calculate optimal position size (risk 1% of account)
    lot_size = risk_manager.calculate_position_size_by_risk(
        account_balance=account_balance,
        risk_percentage=1.0,
        entry_price=entry_price,
        stop_loss_price=sl
    )
    
    # Display risk info before order
    risk_info = risk_manager.get_risk_info(entry_price, sl, tp, lot_size)
    print("\n📊 Trade Risk Analysis:")
    print(f"   Entry Price: {risk_info['entry_price']}")
    print(f"   Stop Loss: {risk_info['stop_loss']} ({risk_info['risk_points']} points)")
    print(f"   Take Profit: {risk_info['take_profit']} ({risk_info['reward_points']} points)")
    print(f"   Lot Size: {risk_info['lot_size']}")
    print(f"   Risk Amount: ${risk_info['risk_amount']}")
    print(f"   Reward Amount: ${risk_info['reward_amount']}")
    print(f"   Risk:Reward = 1:{risk_info['risk_reward_ratio']}")
    
    # Execute order with risk info
    result = executor.execute_buy_order(
        lot_size=lot_size,
        stop_loss=sl,
        take_profit=tp,
        comment="Gold Bot BUY - RR 1:2"
    )
    
    # Add risk info to result for logging
    result["risk_info"] = risk_info
    
    if result["success"]:
        print(f"\n✅ Order placed and logged successfully!")
        print(f"   Order ID: {result['order_id']}")
        print(f"   Log File: trade_logs/trades_{datetime.now().strftime('%Y_%m_%d')}.json")
        
        # Show updated statistics
        updated_stats = trade_logger.get_trade_statistics()
        print(f"\n📊 Updated Stats: {updated_stats['total_trades']} trades today")
    else:
        print(f"\n❌ Order failed: {result.get('error')}")
    """
    
    print("\n" + "=" * 60)
    print("✅ Bot Ready!")
    print(f"📊 Trading Symbol: {gold_symbol}")
    print(f"💰 Account Balance: ${account_balance}")
    print(f"⚖️  Risk Management: Active (1:2)")
    print(f"📝 Trade Logging: Enabled (trade_logs/)")
    print("💡 Uncomment order execution code to start trading")
    print("=" * 60)

if __name__ == "__main__":
    main()