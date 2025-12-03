"""
Trading Bot - MQL Bridge Version (Minimal)
Basic trading bot for MQL Bridge implementation.
"""

import logging
from src.parabolic_sar_bridge import ParabolicSAR
from src.order_executor import OrderExecutor
from src.risk_manager import RiskManager
from src.trade_logger import TradeLogger

logger = logging.getLogger(__name__)


class TradingBot:
    """Minimal trading bot for bridge-based trading."""
    
    def __init__(self, bridge):
        """
        Initialize trading bot.
        
        Args:
            bridge: MQLBridge instance
        """
        self.bridge = bridge
        self.symbol = None
        self.sar = None
        self.executor = None
        self.risk_manager = None
        self.trade_logger = TradeLogger()
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize bot components."""
        try:
            # Get symbol from bridge
            market_data = self.bridge.get_market_data()
            if not market_data or 'symbol' not in market_data:
                logger.error("Failed to get symbol from bridge")
                return False
            
            self.symbol = market_data['symbol']
            
            # Initialize components
            self.sar = ParabolicSAR(self.symbol, self.bridge)
            self.executor = OrderExecutor(self.symbol, self.bridge, self.trade_logger)
            self.risk_manager = RiskManager(self.symbol, self.bridge)
            
            self.initialized = True
            logger.info(f"Trading bot initialized for {self.symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Bot initialization error: {e}")
            return False
    
    def display_status(self):
        """Display bot status."""
        if not self.initialized:
            print("❌ Bot not initialized")
            return
        
        print(f"\n✅ Trading Bot Status:")
        print(f"   Symbol: {self.symbol}")
        print(f"   Bridge: Connected")
        print(f"   Components: Initialized")
    
    def get_current_signal(self):
        """Get current SAR signal."""
        if not self.initialized:
            return None
        
        try:
            return self.sar.check_sar_signal()
        except Exception as e:
            logger.error(f"Error getting signal: {e}")
            return None
    
    def execute_trade(self, signal: str, entry_price: float, 
                     stop_loss: float, take_profit: float, lot_size: float):
        """Execute a trade."""
        if not self.initialized:
            logger.error("Bot not initialized")
            return False
        
        try:
            if signal == "BUY":
                return self.executor.execute_buy_order(
                    entry_price, stop_loss, take_profit, lot_size
                )
            elif signal == "SELL":
                return self.executor.execute_sell_order(
                    entry_price, stop_loss, take_profit, lot_size
                )
            else:
                logger.error(f"Invalid signal: {signal}")
                return False
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return False
