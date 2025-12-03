"""
Order Executor - MQL Bridge Version
Executes BUY/SELL orders through MQL Bridge ONLY.
NO MetaTrader5 Python module required.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class OrderExecutor:
    """Executes trading orders via MQL Bridge."""
    
    def __init__(self, symbol: str, bridge, trade_logger=None):
        """
        Initialize OrderExecutor (Bridge-Only Mode).
        
        Args:
            symbol: Trading symbol (e.g., 'XAUUSD', 'BTCUSD')
            bridge: MQLBridge instance (REQUIRED)
            trade_logger: Optional TradeLogger instance
        """
        if not bridge:
            raise ValueError("MQL Bridge is required for OrderExecutor")
            
        self.symbol = symbol
        self.bridge = bridge
        self.trade_logger = trade_logger
        
        logger.info(f"OrderExecutor initialized for {symbol} (MQL Bridge Mode)")
    
    def execute_buy_order(self, entry_price: float, stop_loss: float, 
                         take_profit: float, lot_size: float,
                         comment: str = "Buy") -> bool:
        """
        Execute BUY order through MQL Bridge.
        
        Args:
            entry_price: Entry price for the order
            stop_loss: Stop loss price
            take_profit: Take profit price
            lot_size: Position size in lots
            comment: Order comment
            
        Returns:
            bool: True if order executed successfully
        """
        logger.info(f"Executing BUY order for {self.symbol}")
        logger.info(f"Entry: {entry_price}, SL: {stop_loss}, TP: {take_profit}, Lots: {lot_size}")
        
        try:
            # Execute via MQL Bridge
            result = self.bridge.execute_trade({
                "action": "BUY",
                "symbol": self.symbol,
                "volume": lot_size,
                "price": entry_price,
                "sl": stop_loss,
                "tp": take_profit,
                "comment": comment
            })
            
            if result and result.get('success'):
                ticket = result.get('ticket', 'N/A')
                self._print_order_success("BUY", entry_price, stop_loss, take_profit, lot_size, ticket)
                self._log_trade("BUY", entry_price, stop_loss, take_profit, lot_size, ticket)
                return True
            else:
                error_msg = result.get('error', 'Unknown error') if result else 'No response from bridge'
                logger.error(f"BUY order failed: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Exception in execute_buy_order: {e}")
            return False
    
    def execute_sell_order(self, entry_price: float, stop_loss: float,
                          take_profit: float, lot_size: float,
                          comment: str = "Sell") -> bool:
        """
        Execute SELL order through MQL Bridge.
        
        Args:
            entry_price: Entry price for the order
            stop_loss: Stop loss price
            take_profit: Take profit price
            lot_size: Position size in lots
            comment: Order comment
            
        Returns:
            bool: True if order executed successfully
        """
        logger.info(f"Executing SELL order for {self.symbol}")
        logger.info(f"Entry: {entry_price}, SL: {stop_loss}, TP: {take_profit}, Lots: {lot_size}")
        
        try:
            # Execute via MQL Bridge
            result = self.bridge.execute_trade({
                "action": "SELL",
                "symbol": self.symbol,
                "volume": lot_size,
                "price": entry_price,
                "sl": stop_loss,
                "tp": take_profit,
                "comment": comment
            })
            
            if result and result.get('success'):
                ticket = result.get('ticket', 'N/A')
                self._print_order_success("SELL", entry_price, stop_loss, take_profit, lot_size, ticket)
                self._log_trade("SELL", entry_price, stop_loss, take_profit, lot_size, ticket)
                return True
            else:
                error_msg = result.get('error', 'Unknown error') if result else 'No response from bridge'
                logger.error(f"SELL order failed: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Exception in execute_sell_order: {e}")
            return False
    
    def _print_order_success(self, order_type: str, entry: float, sl: float, 
                            tp: float, lots: float, ticket):
        """Print order success message."""
        print(f"\n{'='*60}")
        print(f"✅ {order_type} ORDER EXECUTED SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"Symbol: {self.symbol}")
        print(f"Ticket: {ticket}")
        print(f"Entry Price: {entry}")
        print(f"Stop Loss: {sl}")
        print(f"Take Profit: {tp}")
        print(f"Lot Size: {lots}")
        print(f"{'='*60}\n")
    
    def _log_trade(self, order_type: str, entry: float, sl: float, 
                   tp: float, lots: float, ticket):
        """Log trade to trade logger if available."""
        if self.trade_logger:
            try:
                self.trade_logger.log_trade(
                    symbol=self.symbol,
                    action=order_type,
                    entry_price=entry,
                    stop_loss=sl,
                    take_profit=tp,
                    lot_size=lots,
                    ticket=str(ticket),
                    timestamp=datetime.now()
                )
            except Exception as e:
                logger.warning(f"Failed to log trade: {e}")
