"""
Backtesting Engine for Gold Trading Bot
Simulates trading strategy on historical data
"""

"""
DEPRECATED: Backtest engine uses MetaTrader5 for historical data.
This is acceptable for backtesting as it requires historical data access.
For live trading, use app_bridge.py with MQL Bridge.
"""
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json


class BacktestEngine:
    """
    Backtesting engine that simulates trading on historical data
    Tests Parabolic SAR strategy with configurable parameters
    """
    
    def __init__(self, 
                 symbol: str = "XAUUSD",
                 initial_balance: float = 10000.0,
                 risk_percentage: float = 1.0,
                 timeframe = None,
                 sar_acceleration: float = 0.02,
                 sar_maximum: float = 0.2):
        """
        Initialize backtesting engine
        
        Args:
            symbol: Trading symbol
            initial_balance: Starting account balance
            risk_percentage: Risk per trade (%)
            timeframe: MT5 timeframe (default: M15)
            sar_acceleration: SAR acceleration factor
            sar_maximum: SAR maximum value
        """
        self.symbol = symbol
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.risk_percentage = risk_percentage
        self.timeframe = timeframe if timeframe else mt5.TIMEFRAME_M1  # Changed to 1-minute
        self.sar_acceleration = sar_acceleration
        self.sar_maximum = sar_maximum
        
        # Trade tracking
        self.trades: List[Dict] = []
        self.open_positions: List[Dict] = []  # Multiple positions support
        self.max_positions: int = 10  # Maximum concurrent positions
        self.equity_curve: List[Dict] = []
        
        # Statistics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0
        self.total_loss = 0
        
    def load_historical_data(self, 
                            start_date: datetime, 
                            end_date: datetime) -> pd.DataFrame:
        """
        Load historical price data from MT5
        
        Args:
            start_date: Start date for backtest
            end_date: End date for backtest
            
        Returns:
            DataFrame with OHLC data
        """
        print(f"\n📊 Loading historical data for {self.symbol}...")
        print(f"   Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"   Timeframe: 1 minute (more realistic simulation)")
        
        if not mt5.initialize():
            raise Exception("Failed to initialize MT5")
        
        # Get historical rates
        rates = mt5.copy_rates_range(self.symbol, self.timeframe, start_date, end_date)
        mt5.shutdown()
        
        if rates is None or len(rates) == 0:
            raise Exception(f"No historical data available for {self.symbol}")
        
        # Convert to DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        print(f"✅ Loaded {len(df)} bars")
        print(f"   First: {df['time'].iloc[0]}")
        print(f"   Last: {df['time'].iloc[-1]}")
        
        return df
    
    def calculate_parabolic_sar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Parabolic SAR indicator on historical data
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            DataFrame with SAR values and trend
        """
        print("\n🔮 Calculating Parabolic SAR...")
        
        df = df.copy()
        
        # Initialize
        df['sar'] = 0.0
        df['trend'] = 0  # 1 = uptrend, -1 = downtrend
        df['ep'] = 0.0  # Extreme Point
        df['af'] = self.sar_acceleration  # Acceleration Factor
        
        # Start with downtrend
        df.loc[0, 'sar'] = df['high'].iloc[0]
        df.loc[0, 'trend'] = -1
        df.loc[0, 'ep'] = df['low'].iloc[0]
        
        for i in range(1, len(df)):
            prev_sar = df.loc[i-1, 'sar']
            prev_trend = df.loc[i-1, 'trend']
            prev_ep = df.loc[i-1, 'ep']
            prev_af = df.loc[i-1, 'af']
            
            current_high = df.loc[i, 'high']
            current_low = df.loc[i, 'low']
            
            # Calculate new SAR
            new_sar = prev_sar + prev_af * (prev_ep - prev_sar)
            
            # Check for trend reversal
            if prev_trend == 1:  # Uptrend
                if current_low < new_sar:
                    # Reversal to downtrend
                    df.loc[i, 'trend'] = -1
                    df.loc[i, 'sar'] = prev_ep
                    df.loc[i, 'ep'] = current_low
                    df.loc[i, 'af'] = self.sar_acceleration
                else:
                    # Continue uptrend
                    df.loc[i, 'trend'] = 1
                    df.loc[i, 'sar'] = new_sar
                    
                    # Update EP and AF
                    if current_high > prev_ep:
                        df.loc[i, 'ep'] = current_high
                        df.loc[i, 'af'] = min(prev_af + self.sar_acceleration, self.sar_maximum)
                    else:
                        df.loc[i, 'ep'] = prev_ep
                        df.loc[i, 'af'] = prev_af
            else:  # Downtrend
                if current_high > new_sar:
                    # Reversal to uptrend
                    df.loc[i, 'trend'] = 1
                    df.loc[i, 'sar'] = prev_ep
                    df.loc[i, 'ep'] = current_high
                    df.loc[i, 'af'] = self.sar_acceleration
                else:
                    # Continue downtrend
                    df.loc[i, 'trend'] = -1
                    df.loc[i, 'sar'] = new_sar
                    
                    # Update EP and AF
                    if current_low < prev_ep:
                        df.loc[i, 'ep'] = current_low
                        df.loc[i, 'af'] = min(prev_af + self.sar_acceleration, self.sar_maximum)
                    else:
                        df.loc[i, 'ep'] = prev_ep
                        df.loc[i, 'af'] = prev_af
        
        print(f"✅ SAR calculated for {len(df)} bars")
        
        return df
    
    def execute_backtest_trade(self, 
                               bar: pd.Series, 
                               signal: str) -> bool:
        """
        Execute a trade in backtest mode
        
        Args:
            bar: Current price bar
            signal: 'BUY' or 'SELL'
            
        Returns:
            True if trade executed
        """
        # This check is now in execute_backtest_trade - max_positions limit
        
        entry_price = bar['close']
        stop_loss = bar['sar']
        
        # Calculate position size based on risk
        risk_amount = self.current_balance * (self.risk_percentage / 100)
        pip_value = 10  # For gold
        stop_loss_pips = abs(entry_price - stop_loss)
        
        if stop_loss_pips == 0:
            return False
        
        volume = round(risk_amount / (stop_loss_pips * pip_value), 2)
        volume = max(0.01, min(volume, 10.0))  # Limit volume
        
        # Calculate TP (1:2 risk-reward)
        if signal == 'BUY':
            take_profit = entry_price + (stop_loss_pips * 2)
        else:
            take_profit = entry_price - (stop_loss_pips * 2)
        
        # Open position
        position = {
            'type': signal,
            'entry_time': bar['time'],
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'volume': volume,
            'entry_balance': self.current_balance,
            'position_id': len(self.trades) + len(self.open_positions) + 1  # Unique ID
        }
        
        self.open_positions.append(position)
        
        return True
    
    def check_positions_close(self, bar: pd.Series) -> List[Dict]:
        """
        Check if any open positions should be closed
        
        Args:
            bar: Current price bar
            
        Returns:
            List of closed trades
        """
        if not self.open_positions:
            return []
        
        closed_trades = []
        positions_to_keep = []
        
        for pos in self.open_positions:
            current_price = bar['close']
            current_sar = bar['sar']
            current_trend = bar['trend']
            
            close_reason = None
            close_price = None
            
            # Check TP/SL
            if pos['type'] == 'BUY':
                if current_price >= pos['take_profit']:
                    close_reason = 'Take Profit'
                    close_price = pos['take_profit']
                elif current_price <= pos['stop_loss']:
                    close_reason = 'Stop Loss'
                    close_price = pos['stop_loss']
                elif current_trend == -1:  # SAR reversal
                    close_reason = 'SAR Reversal'
                    close_price = current_price
            else:  # SELL
                if current_price <= pos['take_profit']:
                    close_reason = 'Take Profit'
                    close_price = pos['take_profit']
                elif current_price >= pos['stop_loss']:
                    close_reason = 'Stop Loss'
                    close_price = pos['stop_loss']
                elif current_trend == 1:  # SAR reversal
                    close_reason = 'SAR Reversal'
                    close_price = current_price
            
            if close_reason:
                # Calculate profit/loss
                if pos['type'] == 'BUY':
                    pips = close_price - pos['entry_price']
                else:
                    pips = pos['entry_price'] - close_price
                
                profit = pips * pos['volume'] * 10  # Gold pip value
                
                # Update balance
                self.current_balance += profit
                
                # Create trade record
                trade = {
                    'entry_time': pos['entry_time'],
                    'exit_time': bar['time'],
                    'type': pos['type'],
                    'entry_price': pos['entry_price'],
                    'exit_price': close_price,
                    'volume': pos['volume'],
                    'profit': profit,
                    'balance': self.current_balance,
                    'close_reason': close_reason,
                    'duration': (bar['time'] - pos['entry_time']).total_seconds() / 60  # minutes
                }
                
                # Update statistics
                self.total_trades += 1
                if profit > 0:
                    self.winning_trades += 1
                    self.total_profit += profit
                else:
                    self.losing_trades += 1
                    self.total_loss += abs(profit)
                
                self.trades.append(trade)
                closed_trades.append(trade)
                # Position removed from list (not added to positions_to_keep)
            else:
                # Position still open
                positions_to_keep.append(pos)
        
        # Update open positions list
        self.open_positions = positions_to_keep
        
        return closed_trades
    
    def run_backtest(self, 
                     start_date: datetime, 
                     end_date: datetime,
                     desired_signal: str = 'BUY') -> 'BacktestResult':
        """
        Run complete backtest
        
        Args:
            start_date: Start date
            end_date: End date
            desired_signal: 'BUY', 'SELL', or 'BOTH'
            
        Returns:
            BacktestResult object with performance metrics
        """
        print("\n" + "="*70)
        print("🔬 STARTING BACKTEST")
        print("="*70)
        
        # Reset state
        self.current_balance = self.initial_balance
        self.trades = []
        self.open_positions = []  # Reset to empty list
        self.equity_curve = []
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0
        self.total_loss = 0
        
        # Load and prepare data
        df = self.load_historical_data(start_date, end_date)
        df = self.calculate_parabolic_sar(df)
        
        print(f"\n📈 Running backtest simulation...")
        print(f"   Strategy: Parabolic SAR ({desired_signal} signals)")
        print(f"   Risk per trade: {self.risk_percentage}%")
        print(f"   Initial balance: ${self.initial_balance:,.2f}")
        
        # Simulate trading
        for i in range(1, len(df)):
            bar = df.iloc[i]
            prev_bar = df.iloc[i-1]
            
            # Record equity curve
            self.equity_curve.append({
                'time': bar['time'],
                'balance': self.current_balance,
                'equity': self.current_balance,
                'open_positions': len(self.open_positions)
            })
            
            # Check if any positions should close
            closed_trades = self.check_positions_close(bar)
            for closed_trade in closed_trades:
                print(f"   [{closed_trade['exit_time'].strftime('%Y-%m-%d %H:%M')}] "
                      f"Trade #{self.total_trades}: {closed_trade['type']} "
                      f"→ {closed_trade['close_reason']} "
                      f"| P/L: ${closed_trade['profit']:+.2f} "
                      f"| Balance: ${self.current_balance:,.2f} "
                      f"| Open: {len(self.open_positions)}")
            
            # Check for new signals (can open if under max positions)
            if len(self.open_positions) < self.max_positions:
                current_trend = bar['trend']
                prev_trend = prev_bar['trend']
                
                # Signal on trend change
                signal = None
                if prev_trend == -1 and current_trend == 1:
                    signal = 'BUY'
                elif prev_trend == 1 and current_trend == -1:
                    signal = 'SELL'
                
                # Execute trade if signal matches desired
                if signal:
                    if desired_signal == 'BOTH' or desired_signal == signal:
                        if self.execute_backtest_trade(bar, signal):
                            print(f"   [{bar['time'].strftime('%Y-%m-%d %H:%M')}] "
                                  f"Opened {signal} | Entry: {bar['close']:.2f} "
                                  f"| SL: {bar['sar']:.2f} "
                                  f"| Open: {len(self.open_positions)}")
        
        # Close any remaining positions at end
        if self.open_positions:
            last_bar = df.iloc[-1]
            final_closes = self.check_positions_close(last_bar)
            print(f"\n🔚 Closing {len(self.open_positions)} remaining positions at end...")
        
        print(f"\n✅ Backtest complete!")
        
        # Import here to avoid circular dependency
        from src.backtest.backtest_result import BacktestResult
        return BacktestResult(self)
