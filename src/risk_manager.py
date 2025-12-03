"""
Risk Manager - MQL Bridge Version
SL/TP calculation and position sizing through MQL Bridge.
NO MetaTrader5 Python module required.
"""

from typing import Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class RiskManager:
    """
    Automatic Stop Loss and Take Profit calculation with configurable risk-reward ratio.
    Uses MQL Bridge for symbol information.
    Default risk-reward ratio: 1:2 (Risk 1 to gain 2)
    """
    
    def __init__(self, symbol: str, bridge, risk_reward_ratio: float = 2.0):
        """
        Initialize RiskManager.
        
        Args:
            symbol: Trading symbol (e.g., XAUUSD)
            bridge: MQLBridge instance (REQUIRED)
            risk_reward_ratio: Reward to risk ratio (default: 2.0 for 1:2)
        """
        if not bridge:
            raise ValueError("MQL Bridge is required for RiskManager")
            
        self.symbol = symbol
        self.bridge = bridge
        self.risk_reward_ratio = risk_reward_ratio
        
        # Cache symbol info
        self._symbol_info = None
        self._update_symbol_info()
    
    def _update_symbol_info(self):
        """Get and cache symbol information from bridge."""
        try:
            info = self.bridge.get_symbol_info(self.symbol)
            if info and info.get('success'):
                self._symbol_info = info
                logger.debug(f"Symbol info cached for {self.symbol}")
            else:
                logger.warning(f"Failed to get symbol info for {self.symbol}")
        except Exception as e:
            logger.error(f"Error getting symbol info: {e}")
    
    @property
    def point(self) -> float:
        """Get symbol point value."""
        if self._symbol_info:
            return self._symbol_info.get('point', 0.01)
        return 0.01  # Default for gold
    
    @property
    def digits(self) -> int:
        """Get symbol digits."""
        if self._symbol_info:
            return self._symbol_info.get('digits', 2)
        return 2  # Default for gold
    
    @property
    def contract_size(self) -> float:
        """Get contract size."""
        if self._symbol_info:
            return self._symbol_info.get('trade_contract_size', 100.0)
        return 100.0  # Default for gold (100 oz)
    
    @property
    def volume_min(self) -> float:
        """Get minimum volume."""
        if self._symbol_info:
            return self._symbol_info.get('volume_min', 0.01)
        return 0.01
    
    @property
    def volume_max(self) -> float:
        """Get maximum volume."""
        if self._symbol_info:
            return self._symbol_info.get('volume_max', 100.0)
        return 100.0
    
    @property
    def volume_step(self) -> float:
        """Get volume step."""
        if self._symbol_info:
            return self._symbol_info.get('volume_step', 0.01)
        return 0.01
    
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
            order_type: "BUY" or "SELL"
            
        Returns:
            Tuple[float, float]: (stop_loss_price, take_profit_price)
        """
        point = self.point
        digits = self.digits
        
        if order_type.upper() == "BUY":
            # For BUY: SL below entry, TP above entry
            stop_loss = round(entry_price - (stop_loss_points * point), digits)
            take_profit_points = stop_loss_points * self.risk_reward_ratio
            take_profit = round(entry_price + (take_profit_points * point), digits)
        else:  # SELL
            # For SELL: SL above entry, TP below entry
            stop_loss = round(entry_price + (stop_loss_points * point), digits)
            take_profit_points = stop_loss_points * self.risk_reward_ratio
            take_profit = round(entry_price - (take_profit_points * point), digits)
        
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
        digits = self.digits
        
        if order_type.upper() == "BUY":
            # For BUY: SL below entry, TP above entry
            risk_distance = entry_price - stop_loss_price
            
            if risk_distance <= 0:
                raise ValueError("Stop Loss must be below entry price for BUY orders")
            
            reward_distance = risk_distance * self.risk_reward_ratio
            take_profit = round(entry_price + reward_distance, digits)
            
        else:  # SELL
            # For SELL: SL above entry, TP below entry
            risk_distance = stop_loss_price - entry_price
            
            if risk_distance <= 0:
                raise ValueError("Stop Loss must be above entry price for SELL orders")
            
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
            order_type: "BUY" or "SELL"
            
        Returns:
            Tuple[float, float]: (stop_loss_price, take_profit_price)
        """
        digits = self.digits
        
        # Calculate risk and reward amounts
        risk_amount = entry_price * (risk_percentage / 100)
        reward_amount = risk_amount * self.risk_reward_ratio
        
        if order_type.upper() == "BUY":
            stop_loss = round(entry_price - risk_amount, digits)
            take_profit = round(entry_price + reward_amount, digits)
        else:  # SELL
            stop_loss = round(entry_price + risk_amount, digits)
            take_profit = round(entry_price - reward_amount, digits)
        
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
            order_type: "BUY" or "SELL"
            
        Returns:
            float: Recommended lot size
        """
        # Calculate risk amount in account currency
        risk_amount = account_balance * (risk_percentage / 100)
        
        # Calculate price difference (risk per unit)
        price_difference = abs(entry_price - stop_loss_price)
        
        # Calculate position size
        contract_sz = self.contract_size
        lot_size = risk_amount / (price_difference * contract_sz)
        
        # Round to volume step
        volume_st = self.volume_step
        lot_size = round(lot_size / volume_st) * volume_st
        
        # Ensure within bounds
        lot_size = max(self.volume_min, min(lot_size, self.volume_max))
        
        return lot_size
    
    def get_risk_info(
        self,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        lot_size: float,
        order_type: str = "BUY"
    ) -> Dict:
        """
        Get detailed risk information for a trade.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            lot_size: Lot size
            order_type: "BUY" or "SELL"
            
        Returns:
            dict: Risk information
        """
        contract_sz = self.contract_size
        
        # Calculate risk and reward based on order type
        if order_type.upper() == "BUY":
            risk_points = entry_price - stop_loss
            reward_points = take_profit - entry_price
        else:  # SELL
            risk_points = stop_loss - entry_price
            reward_points = entry_price - take_profit
        
        risk_amount = risk_points * contract_sz * lot_size
        reward_amount = reward_points * contract_sz * lot_size
        
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
            "contract_size": contract_sz
        }
