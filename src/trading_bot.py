import MetaTrader5 as mt5
import json
from datetime import datetime
from typing import Optional, Dict

from src.collect_account_info import collect_account_info
from src.symbol_detector import SymbolDetector
from src.order_executor import OrderExecutor
from src.risk_manager import RiskManager
from src.trade_logger import TradeLogger
from src.parabolic_sar import ParabolicSAR


class TradingBot:
    """
    Main Trading Bot Class - Expert Advisor Style
    Manages all trading operations and indicators
    """
    
    def __init__(self):
        """Initialize trading bot components"""
        self.symbol: Optional[str] = None
        self.account_balance: float = 10000.0
        self.account_leverage: int = 0
        
        # Components
        self.detector: Optional[SymbolDetector] = None
        self.trade_logger: Optional[TradeLogger] = None
        self.risk_manager: Optional[RiskManager] = None
        self.executor: Optional[OrderExecutor] = None
        self.sar: Optional[ParabolicSAR] = None
        
        # Data
        self.symbol_info: Optional[object] = None
        self.sar_info: Optional[Dict] = None
        self.stats: Optional[Dict] = None
    
    def initialize(self) -> bool:
        """
        Initialize all bot components
        Returns: True if successful, False otherwise
        """
        print("=" * 60)
        print("🏆 Gold Trading Bot - Starting...")
        print("=" * 60)
        
        # Step 1: Detect gold symbol
        if not self._detect_symbol():
            return False
        
        # Step 2: Collect account info
        if not self._collect_account_info():
            return False
        
        # Step 3: Initialize trade logger
        if not self._initialize_logger():
            return False
        
        # Step 4: Initialize risk manager
        if not self._initialize_risk_manager():
            return False
        
        # Step 5: Initialize order executor
        if not self._initialize_executor():
            return False
        
        # Step 6: Initialize Parabolic SAR
        if not self._initialize_sar():
            return False
        
        # Get symbol info for display
        self._load_symbol_info()
        
        return True
    
    def _detect_symbol(self) -> bool:
        """Detect available gold symbol"""
        print("\n[1/6] Detecting gold symbols...")
        self.detector = SymbolDetector()
        self.symbol = self.detector.detect_gold_symbol()
        
        if not self.symbol:
            print("❌ Failed to detect gold symbol. Exiting...")
            return False
        
        return True
    
    def _collect_account_info(self) -> bool:
        """Collect account information"""
        print("[2/6] Collecting account information...")
        account_success = collect_account_info()
        
        if not account_success:
            print("\n❌ Failed to collect account information")
            return False
        
        # Load account data
        try:
            with open('account_info.json', 'r') as f:
                account_data = json.load(f)
                self.account_balance = account_data.get('balance', 10000.0)
                self.account_leverage = account_data.get('leverage', 0)
        except:
            self.account_balance = 10000.0
            self.account_leverage = 0
        
        return True
    
    def _initialize_logger(self) -> bool:
        """Initialize trade logging system"""
        print("[3/6] Initializing trade logging system...")
        self.trade_logger = TradeLogger(log_directory="trade_logs")
        self.stats = self.trade_logger.get_trade_statistics()
        print("✅ Trade logging enabled")
        return True
    
    def _initialize_risk_manager(self) -> bool:
        """Initialize risk management system"""
        print("[4/6] Initializing risk management...")
        self.risk_manager = RiskManager(self.symbol, risk_reward_ratio=2.0)
        print("✅ Risk-Reward Ratio: 1:2")
        return True
    
    def _initialize_executor(self) -> bool:
        """Initialize order executor"""
        print("[5/6] Order execution ready...")
        self.executor = OrderExecutor(self.symbol, trade_logger=self.trade_logger)
        print("✅ Order executor initialized")
        return True
    
    def _initialize_sar(self) -> bool:
        """Initialize Parabolic SAR indicator"""
        print("[6/6] Analyzing Parabolic SAR indicator...")
        self.sar = ParabolicSAR(self.symbol, timeframe=mt5.TIMEFRAME_M15)
        self.sar_info = self.sar.get_current_sar()
        
        if self.sar_info:
            print(f"✅ SAR Analysis Complete")
            print(f"   Current Price: {self.sar_info['current_price']}")
            print(f"   SAR Value: {self.sar_info['sar_value']}")
            print(f"   Trend: {self.sar_info['trend']} → Signal: {self.sar_info['trend_signal']}")
            print(f"   Distance to SAR: {self.sar_info['distance_to_sar']} ({self.sar_info['distance_percentage']}%)")
        else:
            print("⚠️  SAR analysis failed")
        
        return True
    
    def _load_symbol_info(self):
        """Load symbol information for display"""
        if not mt5.initialize():
            self.symbol_info = None
        else:
            self.symbol_info = mt5.symbol_info(self.symbol)
            mt5.shutdown()
    
    def display_status(self):
        """Display bot status and information"""
        print("\n" + "=" * 60)
        print("✅ Bot Ready!")
        print(f"📊 Trading Symbol: {self.symbol}")
        print(f"💰 Account Balance: ${self.account_balance}")
        print(f"🔢 Leverage: 1:{self.account_leverage}")
        print(f"⚖️  Risk Management: Active (1:2)")
        print(f"📝 Trade Logging: Enabled (trade_logs/)")
        
        if self.stats:
            print(f"📊 Today's Stats: {self.stats['total_trades']} trades | Win Rate: {self.stats['win_rate']}%")
        
        # Display symbol information
        if self.symbol_info is not None:
            print(f"\n📈 Symbol Information:")
            print(f"   Bid: {self.symbol_info.bid}")
            print(f"   Ask: {self.symbol_info.ask}")
            print(f"   Spread: {self.symbol_info.spread}")
            print(f"   Digits: {self.symbol_info.digits}")
            print(f"   Point: {self.symbol_info.point}")
            print(f"   Min Lot: {self.symbol_info.volume_min}")
            print(f"   Max Lot: {self.symbol_info.volume_max}")
            print(f"   Lot Step: {self.symbol_info.volume_step}")
        
        # Display SAR information
        if self.sar_info:
            print(f"\n🔮 Parabolic SAR (15M Timeframe):")
            print(f"   SAR Value: {self.sar_info['sar_value']}")
            print(f"   Trend: {self.sar_info['trend']}")
            print(f"   Signal: {self.sar_info['trend_signal']}")
            print(f"   Distance: {self.sar_info['distance_to_sar']} ({self.sar_info['distance_percentage']}%)")
        
        print("\n💡 Use bot.execute_trade() to place orders")
        print("=" * 60)
    
    def execute_trade(self, position_type: str = 'BUY', 
                     risk_percentage: float = 1.0,
                     use_sar_sl: bool = True) -> Dict:
        """
        Execute a trade with automatic risk management
        
        Args:
            position_type: 'BUY' or 'SELL'
            risk_percentage: Percentage of account to risk (default: 1%)
            use_sar_sl: Use SAR-based stop loss (default: True)
            
        Returns:
            Dictionary with trade result
        """
        # Get current price
        if not mt5.initialize():
            return {"success": False, "error": "Failed to initialize MT5"}
        
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            mt5.shutdown()
            return {"success": False, "error": "Failed to get current price"}
        
        entry_price = tick.ask if position_type == 'BUY' else tick.bid
        mt5.shutdown()
        
        # Calculate Stop Loss
        if use_sar_sl:
            # Use SAR-based Stop Loss
            sar_sl = self.sar.get_sar_stop_loss(position_type)
            if sar_sl is None:
                return {"success": False, "error": "Failed to get SAR-based Stop Loss"}
            
            sl, tp = self.risk_manager.calculate_sl_tp_by_price(entry_price, sar_sl)
        else:
            # Use default points-based Stop Loss
            sl, tp = self.risk_manager.calculate_sl_tp_by_points(entry_price, 50)
        
        # Calculate optimal position size
        lot_size = self.risk_manager.calculate_position_size_by_risk(
            account_balance=self.account_balance,
            risk_percentage=risk_percentage,
            entry_price=entry_price,
            stop_loss_price=sl
        )
        
        # Display risk info
        risk_info = self.risk_manager.get_risk_info(entry_price, sl, tp, lot_size)
        print(f"\n📊 Trade Risk Analysis ({position_type}):")
        print(f"   Entry Price: {risk_info['entry_price']}")
        print(f"   Stop Loss: {risk_info['stop_loss']} ({risk_info['risk_points']} points)")
        print(f"   Take Profit: {risk_info['take_profit']} ({risk_info['reward_points']} points)")
        print(f"   Lot Size: {risk_info['lot_size']}")
        print(f"   Risk Amount: ${risk_info['risk_amount']}")
        print(f"   Reward Amount: ${risk_info['reward_amount']}")
        print(f"   Risk:Reward = 1:{risk_info['risk_reward_ratio']}")
        
        # Execute order
        if position_type == 'BUY':
            result = self.executor.execute_buy_order(
                lot_size=lot_size,
                stop_loss=sl,
                take_profit=tp,
                comment=f"Gold Bot BUY - {'SAR SL' if use_sar_sl else 'Standard SL'}"
            )
        else:
            result = self.executor.execute_sell_order(
                lot_size=lot_size,
                stop_loss=sl,
                take_profit=tp,
                comment=f"Gold Bot SELL - {'SAR SL' if use_sar_sl else 'Standard SL'}"
            )
        
        # Add metadata to result
        result["risk_info"] = risk_info
        result["sar_info"] = self.sar_info
        
        if result["success"]:
            print(f"\n✅ Order placed and logged successfully!")
            print(f"   Order ID: {result['order_id']}")
            print(f"   Log File: trade_logs/trades_{datetime.now().strftime('%Y_%m_%d')}.json")
            
            # Show updated statistics
            updated_stats = self.trade_logger.get_trade_statistics()
            print(f"\n📊 Updated Stats: {updated_stats['total_trades']} trades today")
        else:
            print(f"\n❌ Order failed: {result.get('error')}")
        
        return result
    
    def get_sar_signal(self) -> Optional[str]:
        """
        Get current SAR trading signal
        Returns: 'BUY', 'SELL', or None
        """
        if not self.sar_info:
            return None
        return self.sar_info['trend_signal']
    
    def refresh_data(self):
        """Refresh all real-time data"""
        self.sar_info = self.sar.get_current_sar()
        self._load_symbol_info()
        self.stats = self.trade_logger.get_trade_statistics()
        print("✅ Data refreshed")
