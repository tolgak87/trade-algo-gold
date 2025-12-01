import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from src.trade_logger import TradeLogger


class CircuitBreaker:
    """
    Circuit Breaker System - Automatic trading pause on loss patterns
    
    Rules:
    1. 5 consecutive losses → pause 3 hours
    2. 3 more consecutive losses (8 total) → pause 5 more hours
    3. 70% losses in last 10 trades → pause 5 hours
    """
    
    def __init__(self, trade_logger: TradeLogger, config_file: str = "protection_config.json"):
        """
        Initialize Circuit Breaker
        
        Args:
            trade_logger: TradeLogger instance for accessing trade history
            config_file: Path to configuration file
        """
        self.trade_logger = trade_logger
        self.config_file = config_file
        self.state_file = "circuit_breaker_state.json"
        
        # Load configuration
        self.config = self._load_config()
        
        # Load state (pause info)
        self.state = self._load_state()
    
    def _load_config(self) -> Dict:
        """Load circuit breaker configuration from JSON file"""
        default_config = {
            "circuit_breaker": {
                "enabled": True,
                "consecutive_loss_threshold_1": 5,
                "consecutive_loss_pause_hours_1": 3,
                "consecutive_loss_threshold_2": 8,  # 5 + 3 more
                "consecutive_loss_pause_hours_2": 5,  # Additional 5 hours
                "percentage_loss_window": 10,  # Last 10 trades
                "percentage_loss_threshold": 70,  # 70% losses
                "percentage_loss_pause_hours": 5
            },
            "daily_loss_limit": {
                "enabled": True,
                "max_daily_loss_dollars": 500,  # $500 daily loss limit
                "max_daily_loss_percentage": 5,  # 5% of account balance
                "use_percentage": True  # Use percentage instead of fixed amount
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    default_config.update(loaded_config)
            except:
                pass
        else:
            # Create default config file
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            print(f"📝 Created default config: {self.config_file}")
        
        return default_config
    
    def _load_state(self) -> Dict:
        """Load circuit breaker state (pause info)"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "is_paused": False,
            "pause_reason": None,
            "pause_start_time": None,
            "pause_end_time": None,
            "consecutive_losses": 0,
            "total_pause_count": 0,
            "daily_starting_balance": None,
            "last_reset_date": None
        }
    
    def _save_state(self):
        """Save circuit breaker state to file"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=4)
    
    def is_trading_allowed(self, email_notifier=None) -> tuple[bool, Optional[str]]:
        """
        Check if trading is allowed
        
        Args:
            email_notifier: Optional EmailNotifier instance for sending alerts
        
        Returns:
            tuple: (is_allowed: bool, reason: Optional[str])
        """
        if not self.config["circuit_breaker"]["enabled"]:
            return True, None
        
        # Check if currently paused
        if self.state["is_paused"]:
            pause_end = datetime.fromisoformat(self.state["pause_end_time"])
            now = datetime.now()
            
            if now < pause_end:
                # Still paused
                remaining = pause_end - now
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                
                return False, f"🔴 CIRCUIT BREAKER ACTIVE: {self.state['pause_reason']} | Remaining: {hours}h {minutes}m"
            else:
                # Pause period ended
                self._reset_pause()
                print(f"✅ Circuit breaker pause ended - Trading resumed")
                return True, None
        
        # Check loss patterns
        consecutive_losses = self._count_consecutive_losses()
        percentage_losses = self._calculate_percentage_losses()
        
        cfg = self.config["circuit_breaker"]
        
        # Rule 1 & 2: Consecutive losses (5 losses → 3h | 8 losses → 5h more)
        if consecutive_losses >= cfg["consecutive_loss_threshold_2"]:
            # 8 consecutive losses - pause 5 more hours
            breaker_data = self._activate_pause(
                hours=cfg["consecutive_loss_pause_hours_2"],
                reason=f"{consecutive_losses} consecutive losses (threshold: {cfg['consecutive_loss_threshold_2']})"
            )
            
            # Send email notification
            if email_notifier and email_notifier.enabled:
                email_notifier.notify_circuit_breaker(breaker_data)
            
            return False, self.state["pause_reason"]
        
        elif consecutive_losses >= cfg["consecutive_loss_threshold_1"]:
            # 5 consecutive losses - pause 3 hours
            breaker_data = self._activate_pause(
                hours=cfg["consecutive_loss_pause_hours_1"],
                reason=f"{consecutive_losses} consecutive losses (threshold: {cfg['consecutive_loss_threshold_1']})"
            )
            
            # Send email notification
            if email_notifier and email_notifier.enabled:
                email_notifier.notify_circuit_breaker(breaker_data)
            
            return False, self.state["pause_reason"]
        
        # Rule 3: Percentage losses (70% of last 10 trades)
        if percentage_losses is not None and percentage_losses >= cfg["percentage_loss_threshold"]:
            breaker_data = self._activate_pause(
                hours=cfg["percentage_loss_pause_hours"],
                reason=f"{percentage_losses}% losses in last {cfg['percentage_loss_window']} trades"
            )
            
            # Send email notification
            if email_notifier and email_notifier.enabled:
                email_notifier.notify_circuit_breaker(breaker_data)
            
            return False, self.state["pause_reason"]
        
        return True, None
    
    def _count_consecutive_losses(self) -> int:
        """
        Count consecutive losses from most recent closed trades
        
        Returns:
            int: Number of consecutive losses
        """
        trades = self.trade_logger.get_today_trades()
        
        # Get closed trades only, sorted by exit time (most recent first)
        closed_trades = [t for t in trades if t["status"] == "CLOSED" and t["exit_time"] is not None]
        
        if not closed_trades:
            return 0
        
        # Sort by exit time (most recent first)
        closed_trades.sort(key=lambda x: x["exit_time"], reverse=True)
        
        consecutive_losses = 0
        for trade in closed_trades:
            profit_loss = trade.get("profit_loss", 0)
            if profit_loss < 0:
                consecutive_losses += 1
            else:
                # Break on first win
                break
        
        return consecutive_losses
    
    def _calculate_percentage_losses(self) -> Optional[float]:
        """
        Calculate percentage of losses in last N trades
        
        Returns:
            float: Percentage of losses (0-100) or None if not enough trades
        """
        cfg = self.config["circuit_breaker"]
        window = cfg["percentage_loss_window"]
        
        trades = self.trade_logger.get_today_trades()
        
        # Get closed trades only, sorted by exit time (most recent first)
        closed_trades = [t for t in trades if t["status"] == "CLOSED" and t["exit_time"] is not None]
        
        if len(closed_trades) < window:
            return None  # Not enough trades
        
        # Sort by exit time (most recent first)
        closed_trades.sort(key=lambda x: x["exit_time"], reverse=True)
        
        # Get last N trades
        recent_trades = closed_trades[:window]
        
        # Count losses
        losses = sum(1 for t in recent_trades if t.get("profit_loss", 0) < 0)
        
        percentage = (losses / window) * 100
        return round(percentage, 1)
    
    def _activate_pause(self, hours: int, reason: str):
        """
        Activate circuit breaker pause
        
        Args:
            hours: Number of hours to pause
            reason: Reason for pause
        """
        now = datetime.now()
        pause_end = now + timedelta(hours=hours)
        
        self.state["is_paused"] = True
        self.state["pause_reason"] = reason
        self.state["pause_start_time"] = now.isoformat()
        self.state["pause_end_time"] = pause_end.isoformat()
        self.state["total_pause_count"] += 1
        
        self._save_state()
        
        # Get today's statistics for email
        stats = self.trade_logger.get_trade_statistics()
        total_daily_loss = stats.get('total_profit', 0)  # Negative value if loss
        
        # Get current balance
        current_balance = self._get_current_balance()
        
        print("\n" + "=" * 70)
        print("🔴 CIRCUIT BREAKER ACTIVATED!")
        print("=" * 70)
        print(f"   Reason: {reason}")
        print(f"   Pause Duration: {hours} hours")
        print(f"   Start Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   End Time: {pause_end.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Total Pauses Today: {self.state['total_pause_count']}")
        print(f"   💰 Current Balance: ${current_balance:.2f}")
        print(f"   📉 Total Loss Today: ${abs(total_daily_loss):.2f}")
        print("=" * 70)
        
        # Return data for email notification
        return {
            "reason": reason,
            "pause_hours": hours,
            "consecutive_losses": self._count_consecutive_losses(),
            "percentage_losses": self._calculate_percentage_losses(),
            "total_pauses": self.state['total_pause_count'],
            "total_daily_loss": total_daily_loss,
            "current_balance": current_balance
        }
    
    def _get_current_balance(self) -> float:
        """Get current account balance from MT5 or return 0 if unavailable"""
        try:
            import MetaTrader5 as mt5
            if mt5.initialize():
                account_info = mt5.account_info()
                mt5.shutdown()
                if account_info:
                    return account_info.balance
        except:
            pass
        
        # Fallback: calculate from trade history
        stats = self.trade_logger.get_trade_statistics()
        return 10000.0 + stats.get('total_profit', 0)  # Assuming 10k starting balance
    
    def _reset_pause(self):
        """Reset pause state"""
        self.state["is_paused"] = False
        self.state["pause_reason"] = None
        self.state["pause_start_time"] = None
        self.state["pause_end_time"] = None
        self._save_state()
    
    def get_status(self) -> Dict:
        """
        Get current circuit breaker status
        
        Returns:
            dict: Status information
        """
        consecutive_losses = self._count_consecutive_losses()
        percentage_losses = self._calculate_percentage_losses()
        
        status = {
            "enabled": self.config["circuit_breaker"]["enabled"],
            "is_paused": self.state["is_paused"],
            "pause_reason": self.state["pause_reason"],
            "consecutive_losses": consecutive_losses,
            "percentage_losses": percentage_losses,
            "total_pause_count": self.state["total_pause_count"]
        }
        
        if self.state["is_paused"]:
            pause_end = datetime.fromisoformat(self.state["pause_end_time"])
            now = datetime.now()
            remaining = pause_end - now
            
            status["pause_end_time"] = self.state["pause_end_time"]
            status["remaining_seconds"] = int(remaining.total_seconds())
            status["remaining_display"] = self._format_remaining_time(remaining)
        
        return status
    
    def _format_remaining_time(self, delta: timedelta) -> str:
        """Format remaining time in human-readable format"""
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        seconds = int(delta.total_seconds() % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def force_reset(self):
        """Force reset circuit breaker (use with caution!)"""
        self._reset_pause()
        self.state["consecutive_losses"] = 0
        self._save_state()
        print("⚠️  Circuit breaker force reset!")
    
    def check_daily_loss_limit(self, current_balance: float, email_notifier=None) -> tuple[bool, Optional[str]]:
        """
        Check if daily loss limit is reached
        
        Uses TRADE LOGS to calculate actual daily loss (includes bot trades AND manual MT5 trades)
        
        IMPORTANT: Starting balance is loaded from FIRST TRADE of the day in trade logs.
        This ensures consistency even if bot is restarted multiple times.
        
        How it works:
        1. Check if there are any trades today
        2. If yes: Use balance from first trade as starting balance
        3. If no: Use current balance as starting balance
        4. Calculate total loss from all trades
        5. Compare against limit
        
        Example:
        - 07:00 → First trade opened → Balance: $10,000 (from trade log)
        - 09:00 → Bot closed
        - 10:00 → Bot starts → Reads first trade → Starting balance: $10,000 ✅
        - All day trades calculated against $10,000 starting point
        
        Args:
            current_balance: Current account balance
            email_notifier: Optional EmailNotifier instance for sending alerts
            
        Returns:
            tuple: (is_allowed: bool, reason: Optional[str])
        """
        if not self.config["daily_loss_limit"]["enabled"]:
            return True, None
        
        # Get starting balance from first trade of the day
        first_trade_balance = self.trade_logger.get_first_trade_balance()
        
        # Initialize or reset for new day
        today = datetime.now().strftime("%Y-%m-%d")
        
        if self.state["last_reset_date"] != today:
            # NEW DAY
            if first_trade_balance is not None:
                # Use balance from first trade
                starting_balance = first_trade_balance
                print(f"📅 New trading day - Starting balance from first trade: ${starting_balance:.2f}")
            else:
                # No trades yet today, use current balance
                starting_balance = current_balance
                print(f"📅 New trading day - Starting balance: ${current_balance:.2f} (no trades yet)")
            
            self.state["daily_starting_balance"] = starting_balance
            self.state["last_reset_date"] = today
            self.state["total_pause_count"] = 0
            self._save_state()
            return True, None
        
        # SAME DAY - Use starting balance from state (will be updated if first trade appears)
        if first_trade_balance is not None:
            # Always use first trade balance as the source of truth
            starting_balance = first_trade_balance
            
            # Update state if it's different (bot restarted before any checks)
            if self.state.get("daily_starting_balance") != first_trade_balance:
                self.state["daily_starting_balance"] = first_trade_balance
                self._save_state()
                print(f"💡 Updated starting balance from first trade: ${starting_balance:.2f}")
        else:
            # No trades yet, use state or current balance
            starting_balance = self.state.get("daily_starting_balance", current_balance)
        
        # Inform user about starting balance vs current balance
        if starting_balance != current_balance and not hasattr(self, '_informed_about_balance'):
            self._informed_about_balance = True
            balance_diff = current_balance - starting_balance
            if balance_diff < 0:
                print(f"💡 Daily tracking: Started ${starting_balance:.2f} → Now ${current_balance:.2f} (${abs(balance_diff):.2f} loss)")
            else:
                print(f"💡 Daily tracking: Started ${starting_balance:.2f} → Now ${current_balance:.2f} (+${balance_diff:.2f} profit)")
        
        # Get today's trade statistics (includes ALL trades - bot and manual)
        stats = self.trade_logger.get_trade_statistics()
        total_daily_profit = stats.get("total_profit", 0)
        
        # Check if there's a loss
        if total_daily_profit >= 0:
            # No loss or in profit
            return True, None
        
        # Calculate daily loss (positive number)
        daily_loss = abs(total_daily_profit)
        cfg = self.config["daily_loss_limit"]
        
        if cfg["use_percentage"]:
            # Check percentage-based limit
            loss_percentage = (daily_loss / starting_balance) * 100
            max_percentage = cfg["max_daily_loss_percentage"]
            
            if loss_percentage >= max_percentage:
                # Activate pause for rest of the day
                reason = f"Daily loss limit reached: ${daily_loss:.2f} ({loss_percentage:.1f}% of ${starting_balance:.2f}) | Max: {max_percentage}%"
                
                if not self.state["is_paused"]:
                    # Calculate hours until midnight
                    now = datetime.now()
                    midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
                    hours_until_midnight = (midnight - now).total_seconds() / 3600
                    
                    breaker_data = self._activate_pause(
                        hours=max(1, int(hours_until_midnight) + 1),  # At least 1 hour
                        reason=reason
                    )
                    
                    # Add daily loss specific info
                    breaker_data["daily_loss"] = daily_loss
                    breaker_data["loss_percentage"] = loss_percentage
                    breaker_data["starting_balance"] = starting_balance
                    
                    # Send email notification
                    if email_notifier and email_notifier.enabled:
                        email_notifier.notify_circuit_breaker(breaker_data)
                
                return False, f"🔴 DAILY LOSS LIMIT: ${daily_loss:.2f} ({loss_percentage:.1f}%) | Max: {max_percentage}%"
        else:
            # Check dollar-based limit
            max_loss = cfg["max_daily_loss_dollars"]
            
            if daily_loss >= max_loss:
                reason = f"Daily loss limit reached: ${daily_loss:.2f} | Max: ${max_loss}"
                
                if not self.state["is_paused"]:
                    # Calculate hours until midnight
                    now = datetime.now()
                    midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
                    hours_until_midnight = (midnight - now).total_seconds() / 3600
                    
                    breaker_data = self._activate_pause(
                        hours=max(1, int(hours_until_midnight) + 1),
                        reason=reason
                    )
                    
                    # Add daily loss specific info
                    breaker_data["daily_loss"] = daily_loss
                    breaker_data["loss_percentage"] = (daily_loss / starting_balance) * 100
                    breaker_data["starting_balance"] = starting_balance
                    
                    # Send email notification
                    if email_notifier and email_notifier.enabled:
                        email_notifier.notify_circuit_breaker(breaker_data)
                
                return False, f"🔴 DAILY LOSS LIMIT: ${daily_loss:.2f} | Max: ${max_loss}"
        
        return True, None
    
    def display_status(self):
        """Display circuit breaker status in formatted way"""
        status = self.get_status()
        current_balance = self._get_current_balance()
        
        print("\n" + "=" * 70)
        print("🛡️  CIRCUIT BREAKER STATUS")
        print("=" * 70)
        print(f"   Enabled: {'✅ Yes' if status['enabled'] else '❌ No'}")
        print(f"   Status: {'🔴 PAUSED' if status['is_paused'] else '✅ ACTIVE'}")
        
        if status['is_paused']:
            print(f"   Reason: {status['pause_reason']}")
            print(f"   Remaining Time: {status['remaining_display']}")
        
        print(f"\n📊 Current Metrics:")
        print(f"   Consecutive Losses: {status['consecutive_losses']}")
        
        if status['percentage_losses'] is not None:
            print(f"   Loss % (Last 10): {status['percentage_losses']}%")
        
        print(f"   Total Pauses Today: {status['total_pause_count']}")
        
        # Daily loss limit info
        if self.config["daily_loss_limit"]["enabled"]:
            starting_balance = self.state.get("daily_starting_balance")
            if starting_balance:
                # Get actual loss from trade logs
                stats = self.trade_logger.get_trade_statistics()
                total_daily_profit = stats.get("total_profit", 0)
                daily_loss = abs(total_daily_profit) if total_daily_profit < 0 else 0
                loss_pct = (daily_loss / starting_balance) * 100 if starting_balance > 0 else 0
                
                cfg = self.config["daily_loss_limit"]
                max_pct = cfg["max_daily_loss_percentage"]
                max_dollars = cfg["max_daily_loss_dollars"]
                
                print(f"\n💰 Daily Loss Tracking:")
                print(f"   Starting Balance: ${starting_balance:.2f}")
                print(f"   Current Balance: ${current_balance:.2f}")
                print(f"   Daily Loss (from trades): ${daily_loss:.2f} ({loss_pct:.1f}%)")
                
                if total_daily_profit > 0:
                    print(f"   ✅ Daily Profit: ${total_daily_profit:.2f}")
                
                if cfg["use_percentage"]:
                    print(f"   Limit: {max_pct}% (${starting_balance * max_pct / 100:.2f})")
                    remaining_loss = (starting_balance * max_pct / 100) - daily_loss
                    if remaining_loss > 0:
                        print(f"   ✅ Remaining: ${remaining_loss:.2f} ({max_pct - loss_pct:.1f}%)")
                    else:
                        print(f"   🔴 LIMIT REACHED!")
                else:
                    print(f"   Limit: ${max_dollars}")
                    remaining_loss = max_dollars - daily_loss
                    if remaining_loss > 0:
                        print(f"   ✅ Remaining: ${remaining_loss:.2f}")
                    else:
                        print(f"   🔴 LIMIT REACHED!")
        
        print("=" * 70)


def main():
    """Example usage of CircuitBreaker"""
    from trade_logger import TradeLogger
    
    # Initialize
    logger = TradeLogger()
    breaker = CircuitBreaker(logger)
    
    # Display status
    breaker.display_status()
    
    # Check if trading is allowed
    allowed, reason = breaker.is_trading_allowed()
    
    if allowed:
        print("\n✅ Trading is ALLOWED")
    else:
        print(f"\n🔴 Trading is BLOCKED: {reason}")
    
    # Check daily loss limit
    current_balance = 10000.0
    allowed, reason = breaker.check_daily_loss_limit(current_balance)
    
    if allowed:
        print("✅ Daily loss limit OK")
    else:
        print(f"🔴 Daily loss limit reached: {reason}")


if __name__ == "__main__":
    main()
