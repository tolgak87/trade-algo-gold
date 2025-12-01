import MetaTrader5 as mt5
import json
import time
from datetime import datetime
from typing import Optional, Dict

from src.collect_account_info import collect_account_info
from src.symbol_detector import SymbolDetector
from src.order_executor import OrderExecutor
from src.risk_manager import RiskManager
from src.trade_logger import TradeLogger
from src.parabolic_sar import ParabolicSAR
from src.email_notifier import EmailNotifier, load_email_config
from src.web_ui.dashboard_server import DashboardServer
from src.circuit_breaker import CircuitBreaker


class TradingBot:
    """
    Main Trading Bot Class - Expert Advisor Style
    Manages all trading operations and indicators
    """
    
    def __init__(self, dashboard: Optional[DashboardServer] = None):
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
        self.email_notifier: Optional[EmailNotifier] = None
        self.dashboard: Optional[DashboardServer] = dashboard
        self.circuit_breaker: Optional[CircuitBreaker] = None
        
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
        
        # Step 7: Initialize Email Notifications (optional)
        self._initialize_email()
        
        # Step 8: Initialize Circuit Breaker
        if not self._initialize_circuit_breaker():
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
            with open('logs/account_info.json', 'r') as f:
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
    
    def _initialize_email(self):
        """Initialize email notification system (optional)"""
        try:
            self.email_notifier = load_email_config()
        except:
            self.email_notifier = EmailNotifier()  # Disabled notifier
            print("⚠️  Email notifications disabled")
    
    def _initialize_circuit_breaker(self) -> bool:
        """Initialize Circuit Breaker protection system"""
        print("[7/7] Initializing Circuit Breaker protection...")
        self.circuit_breaker = CircuitBreaker(self.trade_logger)
        
        # Display current status
        status = self.circuit_breaker.get_status()
        print(f"✅ Circuit Breaker initialized")
        print(f"   Enabled: {'Yes' if status['enabled'] else 'No'}")
        print(f"   Consecutive Losses: {status['consecutive_losses']}")
        
        if status['is_paused']:
            print(f"   ⚠️  Currently PAUSED: {status['pause_reason']}")
            print(f"   Remaining: {status['remaining_display']}")
        
        # Show daily balance tracking
        first_trade_balance = self.trade_logger.get_first_trade_balance()
        if first_trade_balance:
            print(f"\n💰 Daily Balance Tracking:")
            print(f"   Starting Balance (from first trade): ${first_trade_balance:.2f}")
            print(f"   Current Balance: ${self.account_balance:.2f}")
            
            diff = self.account_balance - first_trade_balance
            if diff < 0:
                print(f"   Daily Change: -${abs(diff):.2f} ({(diff/first_trade_balance)*100:.2f}%)")
            elif diff > 0:
                print(f"   Daily Change: +${diff:.2f} (+{(diff/first_trade_balance)*100:.2f}%)")
            else:
                print(f"   Daily Change: $0.00 (0%)")
        else:
            print(f"\n💰 Starting Balance: ${self.account_balance:.2f}")
            print(f"   (No trades yet today)")
        
        return True
    
    def _load_symbol_info(self):
        """Load symbol information for display"""
        if not mt5.initialize():
            self.symbol_info = None
        else:
            self.symbol_info = mt5.symbol_info(self.symbol)
            mt5.shutdown()
    
    def _update_dashboard_account(self):
        """Update dashboard with current account information"""
        if not self.dashboard:
            return
        
        if not mt5.initialize():
            return
        
        account_info = mt5.account_info()
        if account_info:
            self.dashboard.update_account_info({
                'balance': account_info.balance,
                'equity': account_info.equity,
                'margin': account_info.margin,
                'free_margin': account_info.margin_free,
                'margin_level': account_info.margin_level,
                'profit': account_info.profit
            })
        
        mt5.shutdown()
    
    def _update_dashboard_sar(self):
        """Update dashboard with SAR data"""
        if not self.dashboard or not self.sar_info:
            return
        
        self.dashboard.update_sar_data({
            'sar_value': self.sar_info.get('sar_value', 0),
            'trend': self.sar_info.get('trend', 'Unknown'),
            'signal': self.sar_info.get('trend_signal', 'HOLD'),
            'distance': self.sar_info.get('distance_to_sar', 0),
            'acceleration': 0.02
        })
    
    def _update_dashboard_price(self, price: float):
        """Update dashboard with current price"""
        if not self.dashboard or not self.sar_info:
            return
        
        self.dashboard.add_price_point(price, self.sar_info.get('sar_value', 0))
    
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
        
        # Display Circuit Breaker status
        if self.circuit_breaker:
            status = self.circuit_breaker.get_status()
            print(f"\n🛡️  Circuit Breaker:")
            print(f"   Status: {'🔴 PAUSED' if status['is_paused'] else '✅ ACTIVE'}")
            if status['is_paused']:
                print(f"   Reason: {status['pause_reason']}")
                print(f"   Remaining: {status['remaining_display']}")
            print(f"   Consecutive Losses: {status['consecutive_losses']}/5")
            if status['percentage_losses'] is not None:
                print(f"   Loss Rate (10 trades): {status['percentage_losses']}%/70%")
        
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
        # CHECK CIRCUIT BREAKER BEFORE TRADING
        if self.circuit_breaker:
            allowed, reason = self.circuit_breaker.is_trading_allowed(self.email_notifier)
            if not allowed:
                print(f"\n🔴 TRADE BLOCKED: {reason}")
                if self.dashboard:
                    self.dashboard.send_notification(f"Trade blocked: {reason}", "warning")
                return {"success": False, "error": reason}
            
            # Check daily loss limit
            allowed, reason = self.circuit_breaker.check_daily_loss_limit(self.account_balance, self.email_notifier)
            if not allowed:
                print(f"\n🔴 TRADE BLOCKED: {reason}")
                if self.dashboard:
                    self.dashboard.send_notification(f"Trade blocked: {reason}", "danger")
                return {"success": False, "error": reason}
        
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
            
            sl, tp = self.risk_manager.calculate_sl_tp_by_price(entry_price, sar_sl, position_type)
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
        
        # Update dashboard on trade execution
        if self.dashboard and result["success"]:
            self.dashboard.update_bot_status(f"{position_type} position opened - Ticket #{result['order_id']}")
            self.dashboard.send_notification(f"{position_type} order placed successfully!", "success")
        
        if result["success"]:
            print(f"\n✅ Order placed and logged successfully!")
            print(f"   Order ID: {result['order_id']}")
            print(f"   Log File: trade_logs/trades_{datetime.now().strftime('%Y_%m_%d')}.json")
            
            # Show updated statistics
            updated_stats = self.trade_logger.get_trade_statistics()
            print(f"\n📊 Updated Stats: {updated_stats['total_trades']} trades today")
        else:
            print(f"\n❌ Order failed: {result.get('error')}")
            if self.dashboard:
                self.dashboard.send_notification(f"Order failed: {result.get('error')}", "danger")
        
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
    
    def wait_for_signal(self, desired_signal: str = 'BUY', 
                       check_interval: int = 30,
                       max_wait_minutes: int = 0) -> bool:
        """
        Wait for a specific trading signal
        
        Args:
            desired_signal: 'BUY' or 'SELL' signal to wait for
            check_interval: Seconds between checks (default: 30)
            max_wait_minutes: Maximum minutes to wait (0 = infinite)
            
        Returns:
            True if signal received, False if timeout
        """
        print(f"\n⏳ Waiting for {desired_signal} signal...")
        print(f"   Check interval: {check_interval} seconds")
        if max_wait_minutes > 0:
            print(f"   Max wait time: {max_wait_minutes} minutes")
        else:
            print(f"   Max wait time: Unlimited (Ctrl+C to stop)")
        
        start_time = time.time()
        check_count = 0
        
        try:
            while True:
                check_count += 1
                
                # CHECK CIRCUIT BREAKER STATUS
                if self.circuit_breaker:
                    allowed, reason = self.circuit_breaker.is_trading_allowed(self.email_notifier)
                    if not allowed:
                        print(f"\n🔴 {reason}")
                        if self.dashboard:
                            self.dashboard.update_bot_status(reason)
                            self.dashboard.send_notification(reason, "warning")
                        # Wait and check again
                        time.sleep(check_interval)
                        continue
                
                # Refresh SAR data
                self.sar_info = self.sar.get_current_sar()
                current_signal = self.get_sar_signal()
                
                # Update dashboard
                if self.dashboard:
                    self._update_dashboard_account()
                    self._update_dashboard_sar()
                    self.dashboard.update_bot_status(f"Waiting for {desired_signal} signal - Check #{check_count}")
                    self.dashboard.update_signal({
                        'type': current_signal if current_signal else 'HOLD',
                        'reason': f"Current: {current_signal}, Waiting for: {desired_signal}",
                        'timestamp': datetime.now().isoformat()
                    })
                    if self.sar_info:
                        self._update_dashboard_price(self.sar_info['current_price'])
                
                if current_signal:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    if current_signal == desired_signal:
                        print(f"\n✅ [{timestamp}] {desired_signal} signal received!")
                        print(f"   Symbol: {self.symbol}")
                        print(f"   Current Price: {self.sar_info['current_price']}")
                        print(f"   SAR Value (Stop Loss): {self.sar_info['sar_value']}")
                        print(f"   Trend: {self.sar_info['trend']}")
                        print(f"   Total checks: {check_count}")
                        return True
                    else:
                        # Display detailed info while waiting
                        print(f"\n⏳ [{timestamp}] Check #{check_count}: Current signal is {current_signal} (waiting for {desired_signal})")
                        print(f"   📊 Symbol: {self.symbol}")
                        print(f"   💰 Current Price: {self.sar_info['current_price']}")
                        print(f"   🔮 SAR Value: {self.sar_info['sar_value']}")
                        print(f"   📈 Trend: {self.sar_info['trend']}")
                        print(f"   📍 Distance: {self.sar_info['distance_to_sar']} ({self.sar_info['distance_percentage']}%)")
                else:
                    print(f"⚠️  Check #{check_count}: Unable to get SAR signal")
                
                # Check timeout
                if max_wait_minutes > 0:
                    elapsed_minutes = (time.time() - start_time) / 60
                    if elapsed_minutes >= max_wait_minutes:
                        print(f"\n⏰ Timeout: {max_wait_minutes} minutes elapsed without {desired_signal} signal")
                        return False
                
                # Wait before next check
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Monitoring stopped by user")
            print(f"   Total checks performed: {check_count}")
            return False
    
    def auto_trade_on_signal(self, desired_signal: str = 'BUY',
                            risk_percentage: float = 1.0,
                            use_sar_sl: bool = True,
                            check_interval: int = 30,
                            max_wait_minutes: int = 0) -> Optional[Dict]:
        """
        Wait for signal and automatically execute trade
        
        Args:
            desired_signal: 'BUY' or 'SELL' signal to wait for
            risk_percentage: Percentage of account to risk
            use_sar_sl: Use SAR-based stop loss
            check_interval: Seconds between checks (default: 30)
            max_wait_minutes: Maximum minutes to wait (0 = infinite)
            
        Returns:
            Trade result dictionary or None if timeout
        """
        # Wait for signal
        if self.wait_for_signal(desired_signal, check_interval, max_wait_minutes):
            print(f"\n🚀 Executing {desired_signal} trade...")
            return self.execute_trade(desired_signal, risk_percentage, use_sar_sl)
        else:
            print(f"❌ No trade executed - signal not received")
            return None
    
    def get_open_positions(self) -> list:
        """
        Get all open positions for the current symbol
        
        Returns:
            List of open position objects
        """
        if not mt5.initialize():
            return []
        
        positions = mt5.positions_get(symbol=self.symbol)
        mt5.shutdown()
        
        return list(positions) if positions else []
    
    def close_position(self, position_ticket: int) -> bool:
        """
        Close a specific position by ticket
        
        Args:
            position_ticket: Position ticket number
            
        Returns:
            True if successfully closed, False otherwise
        """
        if not mt5.initialize():
            print("❌ Failed to initialize MT5")
            return False
        
        position = mt5.positions_get(ticket=position_ticket)
        if not position:
            print(f"❌ Position {position_ticket} not found")
            mt5.shutdown()
            return False
        
        position = position[0]
        
        # Determine order type (opposite of position)
        if position.type == mt5.POSITION_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(self.symbol).bid
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(self.symbol).ask
        
        # Create close request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": position.volume,
            "type": order_type,
            "position": position_ticket,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": "Emergency close by bot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        mt5.shutdown()
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"✅ Position {position_ticket} closed successfully")
            return True
        else:
            print(f"❌ Failed to close position {position_ticket}: {result.comment}")
            return False
    
    def modify_position_sl(self, position_ticket: int, new_stop_loss: float) -> bool:
        """
        Modify stop loss of an open position
        
        Args:
            position_ticket: Position ticket number
            new_stop_loss: New stop loss price
            
        Returns:
            True if successfully modified, False otherwise
        """
        if not mt5.initialize():
            print("❌ Failed to initialize MT5")
            return False
        
        position = mt5.positions_get(ticket=position_ticket)
        if not position:
            print(f"❌ Position {position_ticket} not found")
            mt5.shutdown()
            return False
        
        position = position[0]
        
        # Create modification request
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": self.symbol,
            "position": position_ticket,
            "sl": new_stop_loss,
            "tp": position.tp,  # Keep original TP
        }
        
        result = mt5.order_send(request)
        mt5.shutdown()
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return True
        else:
            print(f"⚠️  Failed to modify SL: {result.comment}")
            return False
    
    def monitor_position(self, position_ticket: int, 
                        stop_loss: float,
                        take_profit: float,
                        entry_price: float,
                        position_type: str = 'BUY',
                        check_interval: int = 5) -> Dict:
        """
        Monitor an open position with emergency stop loss protection
        
        Args:
            position_ticket: Position ticket number to monitor
            stop_loss: Original stop loss price
            take_profit: Original take profit price
            entry_price: Entry price of position
            position_type: 'BUY' or 'SELL'
            check_interval: Seconds between checks (default: 5)
            
        Returns:
            Dictionary with close reason and details
        """
        print(f"\n🔍 Monitoring position {position_ticket}...")
        print(f"   Position Type: {position_type}")
        print(f"   Entry Price: {entry_price}")
        print(f"   Stop Loss: {stop_loss}")
        print(f"   Take Profit: {take_profit}")
        print(f"   Check interval: {check_interval} seconds")
        print(f"   Monitoring: SAR reversal + Emergency SL + Trailing SL")
        
        check_count = 0
        current_sl = stop_loss  # Track current SL
        start_time = datetime.now()
        
        try:
            while True:
                check_count += 1
                
                # Check if position still exists
                positions = self.get_open_positions()
                position_exists = any(p.ticket == position_ticket for p in positions)
                
                if not position_exists:
                    # Position closed - send email notification
                    end_time = datetime.now()
                    duration = str(end_time - start_time).split('.')[0]
                    
                    # Get final position details from history
                    final_price = 0
                    profit_loss = 0
                    volume = 0
                    close_reason = "Position closed"
                    
                    if not mt5.initialize():
                        close_reason = "Position closed by MT5 (SL/TP hit or manual)"
                    else:
                        # Get position history
                        from datetime import timedelta
                        history_from = start_time - timedelta(minutes=5)
                        history_to = datetime.now() + timedelta(minutes=1)
                        
                        # Get deals for this position
                        deals = mt5.history_deals_get(position=position_ticket, from_date=history_from, to_date=history_to)
                        
                        if deals and len(deals) > 0:
                            # Find the exit deal (OUT)
                            for deal in deals:
                                if deal.entry == 1:  # 1 = OUT (exit deal)
                                    final_price = deal.price
                                    profit_loss = deal.profit
                                    volume = deal.volume
                                    
                                    # Determine close reason from deal comment
                                    deal_comment = deal.comment.lower()
                                    if 'tp' in deal_comment:
                                        close_reason = "Take Profit Hit"
                                    elif 'sl' in deal_comment:
                                        close_reason = "Stop Loss Hit"
                                    else:
                                        close_reason = "Manual Close"
                                    break
                            
                            # If we didn't find exit deal, use last deal
                            if final_price == 0 and len(deals) > 0:
                                last_deal = deals[-1]
                                final_price = last_deal.price
                                profit_loss = last_deal.profit
                                volume = last_deal.volume
                                close_reason = "Take Profit Hit" if profit_loss > 0 else "Stop Loss Hit or Manual Close"
                        
                        # Get account balance after close
                        account_balance = 0
                        account_info = mt5.account_info()
                        if account_info:
                            account_balance = account_info.balance
                        
                        mt5.shutdown()
                    
                    # LOG THE CLOSED POSITION (even if manual close)
                    if self.trade_logger and final_price > 0:
                        # Log the closure directly with the ticket number
                        self.trade_logger.log_trade_close(
                            order_id=position_ticket,
                            exit_price=final_price,
                            close_reason=close_reason
                        )
                        print(f"   📝 Trade closure logged: {close_reason} | P/L: ${profit_loss:.2f}")
                    
                    # Send email notification
                    if self.email_notifier and self.email_notifier.enabled:
                        self.email_notifier.notify_position_closed({
                            'symbol': self.symbol,
                            'type': position_type,
                            'ticket': position_ticket,
                            'entry_price': entry_price,
                            'close_price': final_price if final_price else entry_price,
                            'volume': volume,
                            'profit_loss': profit_loss,
                            'close_reason': close_reason,
                            'duration': duration,
                            'account_balance': account_balance
                        })
                    
                    # Update dashboard - position closed
                    if self.dashboard:
                        self.dashboard.update_position(None)
                        self.dashboard.update_bot_status(f"Position closed: {close_reason}")
                        self.dashboard.add_trade({
                            'ticket': position_ticket,
                            'type': position_type,
                            'entry_price': entry_price,
                            'close_price': final_price,
                            'volume': volume,
                            'profit': profit_loss,
                            'duration': duration,
                            'close_reason': close_reason,
                            'timestamp': datetime.now().isoformat()
                        })
                        self._update_dashboard_account()
                    
                    return {
                        "closed": True,
                        "reason": close_reason,
                        "checks": check_count,
                        "duration": duration
                    }
                
                # Get current position details
                current_position = next((p for p in positions if p.ticket == position_ticket), None)
                
                # Refresh SAR data
                self.sar_info = self.sar.get_current_sar()
                current_signal = self.get_sar_signal()
                new_sar = self.sar_info['sar_value']
                
                # Get current price
                if not mt5.initialize():
                    continue
                tick = mt5.symbol_info_tick(self.symbol)
                mt5.shutdown()
                
                if not tick:
                    continue
                
                current_price = tick.bid if position_type == 'BUY' else tick.ask
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Update dashboard with current position data
                if self.dashboard and current_position:
                    position_duration = str(datetime.now() - start_time).split('.')[0]
                    self.dashboard.update_position({
                        'ticket': position_ticket,
                        'type': position_type,
                        'symbol': self.symbol,
                        'volume': current_position.volume,
                        'entry_price': entry_price,
                        'current_price': current_price,
                        'stop_loss': current_sl,
                        'take_profit': take_profit,
                        'profit': current_position.profit,
                        'duration': position_duration
                    })
                    self._update_dashboard_sar()
                    self._update_dashboard_price(current_price)
                    self._update_dashboard_account()
                    self.dashboard.update_bot_status(f"Monitoring {position_type} position #{position_ticket}")
                
                # Check 0: Update Trailing Stop Loss based on SAR
                sl_updated = False
                if position_type == 'BUY':
                    # For BUY: SAR should be below price, move SL up if SAR moved up
                    if new_sar > current_sl and new_sar < current_price:
                        print(f"\n🔒 [{timestamp}] TRAILING STOP UPDATE!")
                        print(f"   Old SL: {current_sl} → New SL: {new_sar}")
                        print(f"   Profit locked: {(new_sar - current_sl):.2f} points")
                        
                        if self.modify_position_sl(position_ticket, new_sar):
                            current_sl = new_sar
                            sl_updated = True
                            print(f"   ✅ Stop Loss updated in MT5")
                        
                elif position_type == 'SELL':
                    # For SELL: SAR should be above price, move SL down if SAR moved down
                    if new_sar < current_sl and new_sar > current_price:
                        print(f"\n🔒 [{timestamp}] TRAILING STOP UPDATE!")
                        print(f"   Old SL: {current_sl} → New SL: {new_sar}")
                        print(f"   Profit locked: {(current_sl - new_sar):.2f} points")
                        
                        if self.modify_position_sl(position_ticket, new_sar):
                            current_sl = new_sar
                            sl_updated = True
                            print(f"   ✅ Stop Loss updated in MT5")
                
                # Check 1: SAR Reversal
                sar_reversed = False
                if position_type == 'BUY' and current_signal == 'SELL':
                    sar_reversed = True
                    print(f"\n⚠️  [{timestamp}] SAR REVERSAL DETECTED!")
                    print(f"   Position: {position_type} | New Signal: {current_signal}")
                    print(f"   Closing position for safety...")
                    
                    if self.close_position(position_ticket):
                        return {
                            "closed": True,
                            "reason": "SAR reversal (UPTREND → DOWNTREND)",
                            "price": current_price,
                            "sar_value": self.sar_info['sar_value'],
                            "checks": check_count
                        }
                
                elif position_type == 'SELL' and current_signal == 'BUY':
                    sar_reversed = True
                    print(f"\n⚠️  [{timestamp}] SAR REVERSAL DETECTED!")
                    print(f"   Position: {position_type} | New Signal: {current_signal}")
                    print(f"   Closing position for safety...")
                    
                    if self.close_position(position_ticket):
                        return {
                            "closed": True,
                            "reason": "SAR reversal (DOWNTREND → UPTREND)",
                            "price": current_price,
                            "sar_value": self.sar_info['sar_value'],
                            "checks": check_count
                        }
                
                # Check 2: Emergency Stop Loss (price broke SL but order didn't trigger)
                emergency_sl_hit = False
                if position_type == 'BUY' and current_price < current_sl:
                    emergency_sl_hit = True
                    print(f"\n🚨 [{timestamp}] EMERGENCY STOP LOSS!")
                    print(f"   Current Price: {current_price} < Stop Loss: {current_sl}")
                    print(f"   MT5 SL didn't trigger - Force closing position!")
                    
                    if self.close_position(position_ticket):
                        return {
                            "closed": True,
                            "reason": "Emergency Stop Loss (price below SL)",
                            "price": current_price,
                            "stop_loss": current_sl,
                            "slippage": abs(current_price - current_sl),
                            "checks": check_count
                        }
                
                elif position_type == 'SELL' and current_price > current_sl:
                    emergency_sl_hit = True
                    print(f"\n🚨 [{timestamp}] EMERGENCY STOP LOSS!")
                    print(f"   Current Price: {current_price} > Stop Loss: {current_sl}")
                    print(f"   MT5 SL didn't trigger - Force closing position!")
                    
                    if self.close_position(position_ticket):
                        return {
                            "closed": True,
                            "reason": "Emergency Stop Loss (price above SL)",
                            "price": current_price,
                            "stop_loss": current_sl,
                            "slippage": abs(current_price - current_sl),
                            "checks": check_count
                        }
                
                # Display monitoring status
                if check_count % 6 == 1 or sl_updated:  # Every ~30 seconds or when SL updated
                    profit_loss = current_position.profit if current_position else 0
                    print(f"\n📊 [{timestamp}] Monitor Check #{check_count}")
                    print(f"   Price: {current_price} | SAR: {self.sar_info['sar_value']} | Signal: {current_signal}")
                    print(f"   P&L: ${profit_loss:.2f} | SL: {current_sl} | TP: {take_profit}")
                
                # Wait before next check
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Position monitoring stopped by user")
            print(f"   Position {position_ticket} is still OPEN!")
            print(f"   Total checks: {check_count}")
            return {
                "closed": False,
                "reason": "Monitoring stopped by user",
                "checks": check_count
            }
    
    def full_auto_trading_cycle(self, desired_signal: str = 'BUY',
                                risk_percentage: float = 1.0,
                                signal_check_interval: int = 30,
                                position_check_interval: int = 5) -> Dict:
        """
        Complete automated trading cycle:
        1. Wait for signal
        2. Execute trade
        3. Monitor position (SAR reversal + emergency SL)
        4. Repeat
        
        Args:
            desired_signal: 'BUY' or 'SELL' signal to wait for
            risk_percentage: Percentage of account to risk
            signal_check_interval: Seconds between signal checks (default: 30)
            position_check_interval: Seconds between position checks (default: 5)
            
        Returns:
            Final cycle result dictionary
        """
        print("\n" + "=" * 60)
        print("🤖 FULL AUTO-TRADING CYCLE STARTED")
        print("=" * 60)
        print(f"   Signal: {desired_signal}")
        print(f"   Risk: {risk_percentage}% of account")
        print(f"   SAR-based Stop Loss: Enabled")
        print(f"   Emergency SL Protection: Enabled")
        print(f"   Signal Check: Every {signal_check_interval}s")
        print(f"   Position Check: Every {position_check_interval}s")
        print("=" * 60)
        
        try:
            while True:
                # Phase 1: Wait for signal
                print(f"\n🔍 PHASE 1: Waiting for {desired_signal} signal...")
                if not self.wait_for_signal(desired_signal, signal_check_interval):
                    break
                
                # Phase 2: Execute trade
                print(f"\n💰 PHASE 2: Executing {desired_signal} trade...")
                result = self.execute_trade(desired_signal, risk_percentage, use_sar_sl=True)
                
                if not result["success"]:
                    print(f"❌ Trade execution failed: {result.get('error')}")
                    continue
                
                # Get position details
                position_ticket = result.get("order_id")
                entry_price = result["risk_info"]["entry_price"]
                stop_loss = result["risk_info"]["stop_loss"]
                take_profit = result["risk_info"]["take_profit"]
                
                print(f"\n✅ Trade opened successfully!")
                print(f"   Ticket: {position_ticket}")
                print(f"   Entry Price: {entry_price}")
                print(f"   Stop Loss: {stop_loss}")
                print(f"   Take Profit: {take_profit}")
                
                # Phase 3: Monitor position
                print(f"\n🛡️ PHASE 3: Monitoring position {position_ticket}...")
                monitor_result = self.monitor_position(
                    position_ticket=position_ticket,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    entry_price=entry_price,
                    position_type=desired_signal,
                    check_interval=position_check_interval
                )
                
                print(f"\n📊 Position closed: {monitor_result['reason']}")
                print(f"   Total monitoring checks: {monitor_result['checks']}")
                
                # Phase 4: Prepare for next cycle
                print(f"\n🔄 Cycle complete. Restarting signal detection...\n")
                time.sleep(5)  # Brief pause before next cycle
                
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Full auto-trading cycle stopped by user")
            return {"stopped": True, "reason": "User interrupted"}
        
        return {"stopped": True, "reason": "Cycle ended"}
