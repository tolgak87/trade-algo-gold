import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import MetaTrader5 as mt5

class TradeLogger:
    """
    Comprehensive JSON-based trade history logging system.
    Creates daily log files with detailed trade information.
    """
    
    def __init__(self, log_directory: str = "trade_logs"):
        """
        Initialize TradeLogger.
        
        Args:
            log_directory: Directory to store log files
        """
        # Get the project root directory (parent of src/)
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.log_directory = os.path.join(self.project_root, log_directory)
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Create log directory if it doesn't exist."""
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)
            print(f"📁 Created log directory: {self.log_directory}")
    
    def _get_daily_log_filename(self, date: Optional[datetime] = None) -> str:
        """
        Generate daily log filename with date.
        Format: trades_YYYY_MM_DD.json
        
        Args:
            date: Date for the log file (uses current date if None)
            
        Returns:
            str: Log filename
        """
        if date is None:
            date = datetime.now()
        
        filename = f"trades_{date.strftime('%Y_%m_%d')}.json"
        return os.path.join(self.log_directory, filename)
    
    def _read_daily_log(self, filename: str) -> List[Dict]:
        """
        Read existing daily log file.
        
        Args:
            filename: Log filename
            
        Returns:
            List[Dict]: List of trade records
        """
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"⚠️ Warning: Could not parse {filename}, creating new log")
                return []
        return []
    
    def _write_daily_log(self, filename: str, trades: List[Dict]):
        """
        Write trades to daily log file.
        
        Args:
            filename: Log filename
            trades: List of trade records
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(trades, f, indent=4, ensure_ascii=False)
    
    def log_trade_open(
        self,
        order_id: int,
        deal_id: int,
        symbol: str,
        order_type: str,
        volume: float,
        entry_price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        leverage: Optional[int] = None,
        comment: str = "",
        magic_number: int = 0,
        risk_info: Optional[Dict] = None
    ) -> Dict:
        """
        Log a new trade opening.
        
        Args:
            order_id: MT5 order ID
            deal_id: MT5 deal ID
            symbol: Trading symbol
            order_type: Order type (BUY/SELL)
            volume: Lot size
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            leverage: Account leverage
            comment: Order comment
            magic_number: Magic number
            risk_info: Risk management information
            
        Returns:
            Dict: Trade record
        """
        now = datetime.now()
        
        # Get account info
        account_info = self._get_account_info()
        
        trade_record = {
            "trade_id": f"{order_id}_{deal_id}",
            "order_id": order_id,
            "deal_id": deal_id,
            "symbol": symbol,
            "type": order_type,
            "status": "OPEN",
            
            # Entry information
            "entry_time": now.isoformat(),
            "entry_date": now.strftime("%Y-%m-%d"),
            "entry_time_display": now.strftime("%Y-%m-%d %H:%M:%S"),
            "entry_price": entry_price,
            
            # Position details
            "volume": volume,
            "leverage": leverage,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            
            # Exit information (to be filled on close)
            "exit_time": None,
            "exit_date": None,
            "exit_time_display": None,
            "exit_price": None,
            "close_reason": None,
            
            # Profit/Loss (to be calculated on close)
            "profit_loss": None,
            "profit_loss_pips": None,
            "profit_loss_percentage": None,
            "duration_seconds": None,
            "duration_display": None,
            
            # Account information at entry
            "account_balance_at_entry": account_info.get("balance"),
            "account_equity_at_entry": account_info.get("equity"),
            "account_currency": account_info.get("currency"),
            
            # Risk management
            "risk_info": risk_info,
            
            # Additional metadata
            "comment": comment,
            "magic_number": magic_number,
            "server": account_info.get("server"),
            "login": account_info.get("login")
        }
        
        # Save to daily log
        filename = self._get_daily_log_filename()
        trades = self._read_daily_log(filename)
        trades.append(trade_record)
        self._write_daily_log(filename, trades)
        
        print(f"📝 Trade logged: {trade_record['trade_id']} in {os.path.basename(filename)}")
        return trade_record
    
    def log_trade_close(
        self,
        order_id: int,
        exit_price: float,
        close_reason: str = "MANUAL"
    ) -> Optional[Dict]:
        """
        Update trade log when position is closed.
        
        Args:
            order_id: Original order ID
            exit_price: Exit/close price
            close_reason: Reason for closure (TP/SL/MANUAL/etc)
            
        Returns:
            Dict: Updated trade record or None if not found
        """
        now = datetime.now()
        
        # Search for trade in recent log files (last 7 days)
        for days_back in range(7):
            date = datetime.now()
            if days_back > 0:
                from datetime import timedelta
                date = date - timedelta(days=days_back)
            
            filename = self._get_daily_log_filename(date)
            if not os.path.exists(filename):
                continue
            
            trades = self._read_daily_log(filename)
            
            # Find trade by order_id
            for trade in trades:
                if trade["order_id"] == order_id and trade["status"] == "OPEN":
                    # Update trade record
                    entry_time = datetime.fromisoformat(trade["entry_time"])
                    duration = (now - entry_time).total_seconds()
                    
                    trade["status"] = "CLOSED"
                    trade["exit_time"] = now.isoformat()
                    trade["exit_date"] = now.strftime("%Y-%m-%d")
                    trade["exit_time_display"] = now.strftime("%Y-%m-%d %H:%M:%S")
                    trade["exit_price"] = exit_price
                    trade["close_reason"] = close_reason
                    trade["duration_seconds"] = duration
                    trade["duration_display"] = self._format_duration(duration)
                    
                    # Calculate profit/loss
                    if trade["type"] == "BUY":
                        profit_loss_pips = exit_price - trade["entry_price"]
                    else:  # SELL
                        profit_loss_pips = trade["entry_price"] - exit_price
                    
                    # Calculate monetary profit/loss
                    # For gold: 1 lot = 100 oz, 1 point = $1
                    profit_loss = profit_loss_pips * trade["volume"] * 100
                    
                    trade["profit_loss"] = round(profit_loss, 2)
                    trade["profit_loss_pips"] = round(profit_loss_pips, 5)
                    trade["profit_loss_percentage"] = round(
                        (profit_loss_pips / trade["entry_price"]) * 100, 4
                    )
                    
                    # Get account info at close
                    account_info = self._get_account_info()
                    trade["account_balance_at_exit"] = account_info.get("balance")
                    trade["account_equity_at_exit"] = account_info.get("equity")
                    
                    # Save updated log
                    self._write_daily_log(filename, trades)
                    
                    print(f"📝 Trade closed: {trade['trade_id']} | P/L: ${profit_loss:.2f}")
                    return trade
        
        print(f"⚠️ Trade with order_id {order_id} not found in recent logs")
        return None
    
    def _get_account_info(self) -> Dict:
        """
        Get current account information from MT5.
        
        Returns:
            Dict: Account information
        """
        if not mt5.initialize():
            return {}
        
        info = mt5.account_info()
        if info is None:
            mt5.shutdown()
            return {}
        
        account_data = {
            "login": info.login,
            "balance": info.balance,
            "equity": info.equity,
            "currency": info.currency,
            "server": info.server,
            "leverage": info.leverage
        }
        
        mt5.shutdown()
        return account_data
    
    def _format_duration(self, seconds: float) -> str:
        """
        Format duration in human-readable format.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            str: Formatted duration
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def get_today_trades(self) -> List[Dict]:
        """
        Get all trades for today.
        
        Returns:
            List[Dict]: List of today's trades
        """
        filename = self._get_daily_log_filename()
        return self._read_daily_log(filename)
    
    def get_trades_by_date(self, date: datetime) -> List[Dict]:
        """
        Get trades for a specific date.
        
        Args:
            date: Date to retrieve trades for
            
        Returns:
            List[Dict]: List of trades
        """
        filename = self._get_daily_log_filename(date)
        return self._read_daily_log(filename)
    
    def get_trade_statistics(self, date: Optional[datetime] = None) -> Dict:
        """
        Calculate statistics for trades on a specific date.
        
        Args:
            date: Date to calculate statistics for (today if None)
            
        Returns:
            Dict: Trade statistics
        """
        trades = self.get_trades_by_date(date) if date else self.get_today_trades()
        
        if not trades:
            return {
                "total_trades": 0,
                "open_trades": 0,
                "closed_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "total_profit": 0,
                "win_rate": 0
            }
        
        closed_trades = [t for t in trades if t["status"] == "CLOSED"]
        winning_trades = [t for t in closed_trades if t.get("profit_loss", 0) > 0]
        losing_trades = [t for t in closed_trades if t.get("profit_loss", 0) < 0]
        
        total_profit = sum(t.get("profit_loss", 0) for t in closed_trades)
        win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0
        
        return {
            "date": date.strftime("%Y-%m-%d") if date else datetime.now().strftime("%Y-%m-%d"),
            "total_trades": len(trades),
            "open_trades": len([t for t in trades if t["status"] == "OPEN"]),
            "closed_trades": len(closed_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "total_profit": round(total_profit, 2),
            "win_rate": round(win_rate, 2),
            "average_profit": round(total_profit / len(closed_trades), 2) if closed_trades else 0
        }
    
    def print_trade_summary(self, trade: Dict):
        """
        Print a formatted summary of a trade.
        
        Args:
            trade: Trade record
        """
        print("\n" + "=" * 60)
        print(f"📊 TRADE SUMMARY - {trade['trade_id']}")
        print("=" * 60)
        print(f"Symbol: {trade['symbol']}")
        print(f"Type: {trade['type']}")
        print(f"Status: {trade['status']}")
        print(f"\n📥 ENTRY:")
        print(f"   Time: {trade['entry_time_display']}")
        print(f"   Price: {trade['entry_price']}")
        print(f"   Volume: {trade['volume']} lots")
        print(f"   Stop Loss: {trade['stop_loss']}")
        print(f"   Take Profit: {trade['take_profit']}")
        
        if trade['status'] == 'CLOSED':
            print(f"\n📤 EXIT:")
            print(f"   Time: {trade['exit_time_display']}")
            print(f"   Price: {trade['exit_price']}")
            print(f"   Reason: {trade['close_reason']}")
            print(f"   Duration: {trade['duration_display']}")
            print(f"\n💰 RESULT:")
            print(f"   P/L: ${trade['profit_loss']}")
            print(f"   P/L Pips: {trade['profit_loss_pips']}")
            print(f"   P/L %: {trade['profit_loss_percentage']}%")
        
        print("=" * 60)


def main():
    """
    Example usage of TradeLogger
    """
    logger = TradeLogger()
    
    # Example 1: Log a trade opening
    print("\n📝 Example: Logging trade opening...")
    trade = logger.log_trade_open(
        order_id=12345,
        deal_id=67890,
        symbol="XAUUSD",
        order_type="BUY",
        volume=0.01,
        entry_price=2650.50,
        stop_loss=2645.00,
        take_profit=2661.00,
        leverage=100,
        comment="Test trade",
        risk_info={
            "risk_amount": 55.0,
            "reward_amount": 110.0,
            "risk_reward_ratio": 2.0
        }
    )
    
    logger.print_trade_summary(trade)
    
    # Example 2: Get today's statistics
    print("\n📊 Today's Statistics:")
    stats = logger.get_trade_statistics()
    print(f"Total Trades: {stats['total_trades']}")
    print(f"Open Trades: {stats['open_trades']}")
    print(f"Closed Trades: {stats['closed_trades']}")
    print(f"Win Rate: {stats['win_rate']}%")
    print(f"Total Profit: ${stats['total_profit']}")
    
    # Example 3: Close a trade (uncomment to test)
    """
    closed_trade = logger.log_trade_close(
        order_id=12345,
        exit_price=2655.50,
        close_reason="TP"
    )
    if closed_trade:
        logger.print_trade_summary(closed_trade)
    """


if __name__ == "__main__":
    main()
