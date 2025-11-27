import MetaTrader5 as mt5
from typing import Optional, Dict
from datetime import datetime
import json

class OrderExecutor:
    """
    Executes BUY (LONG) and SELL (SHORT) orders on MT5 with configurable parameters.
    Supports both long and short positions for gold trading.
    """
    
    def __init__(self, symbol: str, trade_logger=None):
        """
        Initialize OrderExecutor with a trading symbol.
        
        Args:
            symbol: The trading symbol (e.g., XAUUSD)
            trade_logger: TradeLogger instance for logging trades
        """
        self.symbol = symbol
        self.last_order_result = None
        self.trade_logger = trade_logger
    
    def execute_buy_order(
        self,
        lot_size: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        deviation: int = 20,
        comment: str = "Gold Trading Bot",
        magic_number: int = 234000
    ) -> Dict:
        """
        Execute a BUY (LONG) order on the specified symbol.
        
        Args:
            lot_size: Volume/lot size for the order
            stop_loss: Stop Loss price (optional)
            take_profit: Take Profit price (optional)
            deviation: Maximum price deviation in points
            comment: Order comment
            magic_number: Magic number to identify bot orders
            
        Returns:
            dict: Order execution result with status and details
        """
        if not mt5.initialize():
            return {
                "success": False,
                "error": "MT5 initialization failed",
                "error_code": mt5.last_error()
            }
        
        # Get symbol info
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            mt5.shutdown()
            return {
                "success": False,
                "error": f"Symbol {self.symbol} not found"
            }
        
        # Check if symbol is available for trading
        if not symbol_info.visible:
            if not mt5.symbol_select(self.symbol, True):
                mt5.shutdown()
                return {
                    "success": False,
                    "error": f"Failed to select symbol {self.symbol}"
                }
        
        # Validate lot size
        if lot_size < symbol_info.volume_min:
            mt5.shutdown()
            return {
                "success": False,
                "error": f"Lot size {lot_size} is below minimum {symbol_info.volume_min}"
            }
        
        if lot_size > symbol_info.volume_max:
            mt5.shutdown()
            return {
                "success": False,
                "error": f"Lot size {lot_size} exceeds maximum {symbol_info.volume_max}"
            }
        
        # Get current price
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            mt5.shutdown()
            return {
                "success": False,
                "error": f"Failed to get tick data for {self.symbol}"
            }
        
        price = tick.ask
        
        # Prepare order request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "deviation": deviation,
            "magic": magic_number,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Add SL/TP if provided
        if stop_loss is not None:
            request["sl"] = stop_loss
        
        if take_profit is not None:
            request["tp"] = take_profit
        
        # Send order
        result = mt5.order_send(request)
        
        # Process result
        if result is None:
            mt5.shutdown()
            return {
                "success": False,
                "error": "Order send failed - no result returned"
            }
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            mt5.shutdown()
            return {
                "success": False,
                "error": f"Order failed: {result.comment}",
                "retcode": result.retcode,
                "request": request
            }
        
        # Order successful
        # Get account info for logging
        account_info = mt5.account_info()
        leverage = account_info.leverage if account_info else None
        
        order_info = {
            "success": True,
            "order_id": result.order,
            "deal_id": result.deal,
            "symbol": self.symbol,
            "type": "BUY",
            "volume": lot_size,
            "price": result.price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "comment": comment,
            "magic_number": magic_number,
            "leverage": leverage,
            "timestamp": datetime.now().isoformat(),
            "retcode": result.retcode,
            "request_id": result.request_id
        }
        
        self.last_order_result = order_info
        
        # Log to TradeLogger if available
        if self.trade_logger:
            risk_info = order_info.get("risk_info")
            self.trade_logger.log_trade_open(
                order_id=result.order,
                deal_id=result.deal,
                symbol=self.symbol,
                order_type="BUY",
                volume=lot_size,
                entry_price=result.price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                leverage=leverage,
                comment=comment,
                magic_number=magic_number,
                risk_info=risk_info
            )
        
        print(f"\n✅ BUY Order Executed Successfully!")
        print(f"   Order ID: {result.order}")
        print(f"   Deal ID: {result.deal}")
        print(f"   Symbol: {self.symbol}")
        print(f"   Volume: {lot_size}")
        print(f"   Entry Price: {result.price}")
        if stop_loss:
            print(f"   Stop Loss: {stop_loss}")
        if take_profit:
            print(f"   Take Profit: {take_profit}")
        
        mt5.shutdown()
        return order_info
    
    def execute_sell_order(
        self,
        lot_size: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        deviation: int = 20,
        comment: str = "Gold Trading Bot",
        magic_number: int = 234000
    ) -> Dict:
        """
        Execute a SELL (SHORT) order on the specified symbol.
        
        Args:
            lot_size: Volume/lot size for the order
            stop_loss: Stop Loss price (optional)
            take_profit: Take Profit price (optional)
            deviation: Maximum price deviation in points
            comment: Order comment
            magic_number: Magic number to identify bot orders
            
        Returns:
            dict: Order execution result with status and details
        """
        if not mt5.initialize():
            return {
                "success": False,
                "error": "MT5 initialization failed",
                "error_code": mt5.last_error()
            }
        
        # Get symbol info
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            mt5.shutdown()
            return {
                "success": False,
                "error": f"Symbol {self.symbol} not found"
            }
        
        # Check if symbol is available for trading
        if not symbol_info.visible:
            if not mt5.symbol_select(self.symbol, True):
                mt5.shutdown()
                return {
                    "success": False,
                    "error": f"Failed to select symbol {self.symbol}"
                }
        
        # Validate lot size
        if lot_size < symbol_info.volume_min:
            mt5.shutdown()
            return {
                "success": False,
                "error": f"Lot size {lot_size} is below minimum {symbol_info.volume_min}"
            }
        
        if lot_size > symbol_info.volume_max:
            mt5.shutdown()
            return {
                "success": False,
                "error": f"Lot size {lot_size} exceeds maximum {symbol_info.volume_max}"
            }
        
        # Get current price (use BID for SELL)
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            mt5.shutdown()
            return {
                "success": False,
                "error": f"Failed to get tick data for {self.symbol}"
            }
        
        price = tick.bid
        
        # Prepare order request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "deviation": deviation,
            "magic": magic_number,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Add SL/TP if provided
        if stop_loss is not None:
            request["sl"] = stop_loss
        
        if take_profit is not None:
            request["tp"] = take_profit
        
        # Send order
        result = mt5.order_send(request)
        
        # Process result
        if result is None:
            mt5.shutdown()
            return {
                "success": False,
                "error": "Order send failed - no result returned"
            }
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            mt5.shutdown()
            return {
                "success": False,
                "error": f"Order failed: {result.comment}",
                "retcode": result.retcode,
                "request": request
            }
        
        # Order successful
        # Get account info for logging
        account_info = mt5.account_info()
        leverage = account_info.leverage if account_info else None
        
        order_info = {
            "success": True,
            "order_id": result.order,
            "deal_id": result.deal,
            "symbol": self.symbol,
            "type": "SELL",
            "volume": lot_size,
            "price": result.price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "comment": comment,
            "magic_number": magic_number,
            "leverage": leverage,
            "timestamp": datetime.now().isoformat(),
            "retcode": result.retcode,
            "request_id": result.request_id
        }
        
        self.last_order_result = order_info
        
        # Log to TradeLogger if available
        if self.trade_logger:
            risk_info = order_info.get("risk_info")
            self.trade_logger.log_trade_open(
                order_id=result.order,
                deal_id=result.deal,
                symbol=self.symbol,
                order_type="SELL",
                volume=lot_size,
                entry_price=result.price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                leverage=leverage,
                comment=comment,
                magic_number=magic_number,
                risk_info=risk_info
            )
        
        print(f"\n✅ SELL Order Executed Successfully!")
        print(f"   Order ID: {result.order}")
        print(f"   Deal ID: {result.deal}")
        print(f"   Symbol: {self.symbol}")
        print(f"   Volume: {lot_size}")
        print(f"   Entry Price: {result.price}")
        if stop_loss:
            print(f"   Stop Loss: {stop_loss}")
        if take_profit:
            print(f"   Take Profit: {take_profit}")
        
        mt5.shutdown()
        return order_info
    
    def get_last_order_info(self) -> Optional[Dict]:
        """
        Get information about the last executed order.
        
        Returns:
            dict: Last order information or None
        """
        return self.last_order_result
    
    def save_order_to_log(self, order_info: Dict, log_file: str = "trades_log.json") -> bool:
        """
        Save order information to a JSON log file.
        
        Args:
            order_info: Order information dictionary
            log_file: Path to log file
            
        Returns:
            bool: True if saved successfully
        """
        try:
            # Try to read existing log
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    trades = json.load(f)
            except FileNotFoundError:
                trades = []
            
            # Append new order
            trades.append(order_info)
            
            # Save updated log
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(trades, f, indent=4, ensure_ascii=False)
            
            print(f"📝 Order logged to {log_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save order log: {e}")
            return False


def main():
    """
    Example usage of OrderExecutor
    """
    from symbol_detector import SymbolDetector
    
    # Detect gold symbol
    detector = SymbolDetector()
    symbol = detector.detect_gold_symbol()
    
    if not symbol:
        print("❌ Failed to detect gold symbol")
        return
    
    # Create order executor
    executor = OrderExecutor(symbol)
    
    # Example: Execute a BUY order
    # CAUTION: This will place a real order!
    # Uncomment and modify parameters for actual trading
    
    """
    result = executor.execute_buy_order(
        lot_size=0.01,  # Minimum lot size
        stop_loss=2500.00,  # Example SL price
        take_profit=2600.00,  # Example TP price
        comment="Test BUY order"
    )
    
    if result["success"]:
        # Save to log
        executor.save_order_to_log(result)
    else:
        print(f"Order failed: {result.get('error')}")
    """
    
    print("\n⚠️  OrderExecutor initialized and ready")
    print("💡 Uncomment the code in main() to execute actual orders")


if __name__ == "__main__":
    main()
