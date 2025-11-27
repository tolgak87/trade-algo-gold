import MetaTrader5 as mt5
from typing import Tuple, Optional, Dict

class RiskManager:
    """
    Automatic Stop Loss and Take Profit calculation with configurable risk-reward ratio.
    Default risk-reward ratio: 1:2 (Risk 1 to gain 2)
    """
    
    def __init__(self, symbol: str, risk_reward_ratio: float = 2.0):
        """
        Initialize RiskManager.
        
        Args:
            symbol: Trading symbol (e.g., XAUUSD)
            risk_reward_ratio: Reward to risk ratio (default: 2.0 for 1:2)
        """
        self.symbol = symbol
        self.risk_reward_ratio = risk_reward_ratio
    
    def calculate_sl_tp_by_points(
        self,
        entry_price: float,
        stop_loss_points: float,
        order_type: str = "BUY"
    ) -> Tuple[float, float]:
        """
        Calculate Stop Loss and Take Profit based on points/pips.
        
        Args:
            entry_price: Entry price for the trade
            stop_loss_points: Stop loss distance in points/pips
            order_type: "BUY" or "SELL" (currently only BUY supported)
            
        Returns:
            Tuple[float, float]: (stop_loss_price, take_profit_price)
        """
        if order_type.upper() != "BUY":
            raise ValueError("Only BUY orders are supported")
        
        # Get symbol info for point value
        if not mt5.initialize():
            raise Exception("MT5 initialization failed")
        
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            mt5.shutdown()
            raise Exception(f"Symbol {self.symbol} not found")
        
        point = symbol_info.point
        digits = symbol_info.digits
        
        mt5.shutdown()
        
        # Calculate SL and TP for BUY order
        stop_loss = round(entry_price - (stop_loss_points * point), digits)
        take_profit_points = stop_loss_points * self.risk_reward_ratio
        take_profit = round(entry_price + (take_profit_points * point), digits)
        
        return stop_loss, take_profit
    
    def calculate_sl_tp_by_price(
        self,
        entry_price: float,
        stop_loss_price: float,
        order_type: str = "BUY"
    ) -> Tuple[float, float]:
        """
        Calculate Take Profit based on Stop Loss price using risk-reward ratio.
        
        Args:
            entry_price: Entry price for the trade
            stop_loss_price: Desired stop loss price
            order_type: "BUY" or "SELL"
            
        Returns:
            Tuple[float, float]: (stop_loss_price, take_profit_price)
        """
        # Get symbol info for proper rounding
        if not mt5.initialize():
            raise Exception("MT5 initialization failed")
        
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            mt5.shutdown()
            raise Exception(f"Symbol {self.symbol} not found")
        
        digits = symbol_info.digits
        mt5.shutdown()
        
        if order_type.upper() == "BUY":
            # For BUY: SL below entry, TP above entry
            risk_distance = entry_price - stop_loss_price
            
            if risk_distance <= 0:
                raise ValueError("Stop Loss must be below entry price for BUY orders")
            
            # Calculate TP based on risk-reward ratio
            reward_distance = risk_distance * self.risk_reward_ratio
            take_profit = round(entry_price + reward_distance, digits)
            
        else:  # SELL
            # For SELL: SL above entry, TP below entry
            risk_distance = stop_loss_price - entry_price
            
            if risk_distance <= 0:
                raise ValueError("Stop Loss must be above entry price for SELL orders")
            
            # Calculate TP based on risk-reward ratio
            reward_distance = risk_distance * self.risk_reward_ratio
            take_profit = round(entry_price - reward_distance, digits)
        
        return stop_loss_price, take_profit
    
    def calculate_sl_tp_by_percentage(
        self,
        entry_price: float,
        risk_percentage: float,
        order_type: str = "BUY"
    ) -> Tuple[float, float]:
        """
        Calculate SL and TP based on percentage of entry price.
        
        Args:
            entry_price: Entry price for the trade
            risk_percentage: Risk percentage (e.g., 0.5 for 0.5%)
            order_type: "BUY" or "SELL" (currently only BUY supported)
            
        Returns:
            Tuple[float, float]: (stop_loss_price, take_profit_price)
        """
        if order_type.upper() != "BUY":
            raise ValueError("Only BUY orders are supported")
        
        # Get symbol info for proper rounding
        if not mt5.initialize():
            raise Exception("MT5 initialization failed")
        
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            mt5.shutdown()
            raise Exception(f"Symbol {self.symbol} not found")
        
        digits = symbol_info.digits
        mt5.shutdown()
        
        # Calculate SL and TP for BUY order
        risk_amount = entry_price * (risk_percentage / 100)
        stop_loss = round(entry_price - risk_amount, digits)
        
        reward_amount = risk_amount * self.risk_reward_ratio
        take_profit = round(entry_price + reward_amount, digits)
        
        return stop_loss, take_profit
    
    def calculate_position_size_by_risk(
        self,
        account_balance: float,
        risk_percentage: float,
        entry_price: float,
        stop_loss_price: float,
        order_type: str = "BUY"
    ) -> float:
        """
        Calculate optimal position size based on account risk percentage.
        
        Args:
            account_balance: Account balance
            risk_percentage: Percentage of balance to risk (e.g., 1.0 for 1%)
            entry_price: Entry price
            stop_loss_price: Stop loss price
            order_type: "BUY" or "SELL" (currently only BUY supported)
            
        Returns:
            float: Recommended lot size
        """
        if order_type.upper() != "BUY":
            raise ValueError("Only BUY orders are supported")
        
        if not mt5.initialize():
            raise Exception("MT5 initialization failed")
        
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            mt5.shutdown()
            raise Exception(f"Symbol {self.symbol} not found")
        
        # Get contract size (typically 100 for gold = 100oz)
        contract_size = symbol_info.trade_contract_size
        volume_min = symbol_info.volume_min
        volume_max = symbol_info.volume_max
        volume_step = symbol_info.volume_step
        
        mt5.shutdown()
        
        # Calculate risk amount in account currency
        risk_amount = account_balance * (risk_percentage / 100)
        
        # Calculate price difference (risk per unit)
        price_difference = abs(entry_price - stop_loss_price)
        
        # Calculate position size
        # lot_size = risk_amount / (price_difference * contract_size)
        lot_size = risk_amount / (price_difference * contract_size)
        
        # Round to volume step
        lot_size = round(lot_size / volume_step) * volume_step
        
        # Ensure within bounds
        lot_size = max(volume_min, min(lot_size, volume_max))
        
        return lot_size
    
    def get_risk_info(
        self,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        lot_size: float
    ) -> Dict:
        """
        Get detailed risk information for a trade.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            lot_size: Lot size
            
        Returns:
            dict: Risk information
        """
        if not mt5.initialize():
            raise Exception("MT5 initialization failed")
        
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            mt5.shutdown()
            raise Exception(f"Symbol {self.symbol} not found")
        
        contract_size = symbol_info.trade_contract_size
        mt5.shutdown()
        
        # Calculate risk and reward
        risk_points = entry_price - stop_loss
        reward_points = take_profit - entry_price
        
        risk_amount = risk_points * contract_size * lot_size
        reward_amount = reward_points * contract_size * lot_size
        
        actual_rr_ratio = reward_points / risk_points if risk_points > 0 else 0
        
        return {
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "lot_size": lot_size,
            "risk_points": round(risk_points, 2),
            "reward_points": round(reward_points, 2),
            "risk_amount": round(risk_amount, 2),
            "reward_amount": round(reward_amount, 2),
            "risk_reward_ratio": round(actual_rr_ratio, 2),
            "contract_size": contract_size
        }


def main():
    """
    Example usage of RiskManager
    """
    from symbol_detector import SymbolDetector
    
    # Detect gold symbol
    detector = SymbolDetector()
    symbol = detector.detect_gold_symbol()
    
    if not symbol:
        print("❌ Failed to detect gold symbol")
        return
    
    # Initialize RiskManager with 1:2 risk-reward ratio
    risk_manager = RiskManager(symbol, risk_reward_ratio=2.0)
    
    # Example 1: Calculate SL/TP by points
    entry_price = 2650.00
    sl_points = 50  # 50 points = $5 for gold
    
    sl, tp = risk_manager.calculate_sl_tp_by_points(entry_price, sl_points)
    print("\n📊 Method 1: By Points")
    print(f"   Entry: {entry_price}")
    print(f"   SL: {sl} (Risk: {sl_points} points)")
    print(f"   TP: {tp} (Reward: {sl_points * 2.0} points)")
    print(f"   Risk:Reward = 1:2")
    
    # Example 2: Calculate SL/TP by price
    sl_price = 2645.00
    sl2, tp2 = risk_manager.calculate_sl_tp_by_price(entry_price, sl_price)
    print("\n📊 Method 2: By Price")
    print(f"   Entry: {entry_price}")
    print(f"   SL: {sl2}")
    print(f"   TP: {tp2}")
    print(f"   Risk:Reward = 1:2")
    
    # Example 3: Calculate SL/TP by percentage
    risk_pct = 0.5  # 0.5% risk
    sl3, tp3 = risk_manager.calculate_sl_tp_by_percentage(entry_price, risk_pct)
    print("\n📊 Method 3: By Percentage")
    print(f"   Entry: {entry_price}")
    print(f"   SL: {sl3} (Risk: {risk_pct}%)")
    print(f"   TP: {tp3} (Reward: {risk_pct * 2.0}%)")
    print(f"   Risk:Reward = 1:2")
    
    # Example 4: Calculate position size
    account_balance = 10000.0
    risk_pct = 1.0  # Risk 1% of account
    lot_size = risk_manager.calculate_position_size_by_risk(
        account_balance, risk_pct, entry_price, sl_price
    )
    print("\n💰 Position Sizing")
    print(f"   Account Balance: ${account_balance}")
    print(f"   Risk: {risk_pct}%")
    print(f"   Recommended Lot Size: {lot_size}")
    
    # Example 5: Get risk info
    risk_info = risk_manager.get_risk_info(entry_price, sl2, tp2, lot_size)
    print("\n📋 Risk Information")
    print(f"   Risk Amount: ${risk_info['risk_amount']}")
    print(f"   Reward Amount: ${risk_info['reward_amount']}")
    print(f"   Risk:Reward Ratio: 1:{risk_info['risk_reward_ratio']}")


if __name__ == "__main__":
    main()
