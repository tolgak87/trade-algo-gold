import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
from typing import Optional, Tuple

class ParabolicSAR:
    """
    Parabolic SAR (Stop and Reverse) Indicator
    Real-time implementation with MT5 data
    """
    
    def __init__(self, symbol: str, timeframe: int = mt5.TIMEFRAME_M15, 
                 acceleration: float = 0.02, maximum: float = 0.2):
        """
        Initialize Parabolic SAR indicator
        
        Args:
            symbol: Trading symbol (e.g., XAUUSD)
            timeframe: MT5 timeframe constant (default: 15-minute)
            acceleration: Acceleration factor (default: 0.02)
            maximum: Maximum acceleration (default: 0.2)
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.af = acceleration  # Acceleration Factor
        self.max_af = maximum   # Maximum Acceleration Factor
        
    def get_historical_data(self, bars: int = 100) -> Optional[pd.DataFrame]:
        """
        Fetch historical price data from MT5
        
        Args:
            bars: Number of bars to fetch
            
        Returns:
            DataFrame with OHLC data or None if failed
        """
        if not mt5.initialize():
            print(f"❌ MT5 initialization failed: {mt5.last_error()}")
            return None
        
        # Get historical data
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, bars)
        
        if rates is None or len(rates) == 0:
            print(f"❌ Failed to get historical data for {self.symbol}")
            mt5.shutdown()
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        mt5.shutdown()
        return df
    
    def calculate_sar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Parabolic SAR values
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            DataFrame with SAR values added
        """
        if df is None or len(df) < 2:
            return df
        
        # Initialize arrays
        df['sar'] = 0.0
        df['trend'] = 0  # 1 = uptrend, -1 = downtrend
        df['ep'] = 0.0   # Extreme Point
        df['af_current'] = self.af
        
        # Start with uptrend assumption
        df.loc[0, 'sar'] = df.loc[0, 'low']
        df.loc[0, 'trend'] = 1
        df.loc[0, 'ep'] = df.loc[0, 'high']
        df.loc[0, 'af_current'] = self.af
        
        # Calculate SAR for each bar
        for i in range(1, len(df)):
            prev_sar = df.loc[i-1, 'sar']
            prev_trend = df.loc[i-1, 'trend']
            prev_ep = df.loc[i-1, 'ep']
            prev_af = df.loc[i-1, 'af_current']
            
            current_high = df.loc[i, 'high']
            current_low = df.loc[i, 'low']
            
            # Calculate new SAR
            new_sar = prev_sar + prev_af * (prev_ep - prev_sar)
            
            # Uptrend
            if prev_trend == 1:
                # Check if trend reverses
                if current_low < new_sar:
                    # Switch to downtrend
                    df.loc[i, 'trend'] = -1
                    df.loc[i, 'sar'] = prev_ep
                    df.loc[i, 'ep'] = current_low
                    df.loc[i, 'af_current'] = self.af
                else:
                    # Continue uptrend
                    df.loc[i, 'trend'] = 1
                    df.loc[i, 'sar'] = new_sar
                    
                    # Update EP and AF
                    if current_high > prev_ep:
                        df.loc[i, 'ep'] = current_high
                        df.loc[i, 'af_current'] = min(prev_af + self.af, self.max_af)
                    else:
                        df.loc[i, 'ep'] = prev_ep
                        df.loc[i, 'af_current'] = prev_af
                    
                    # Make sure SAR is below the last two lows
                    df.loc[i, 'sar'] = min(df.loc[i, 'sar'], 
                                          df.loc[i-1, 'low'],
                                          df.loc[i, 'low'])
            
            # Downtrend
            else:
                # Check if trend reverses
                if current_high > new_sar:
                    # Switch to uptrend
                    df.loc[i, 'trend'] = 1
                    df.loc[i, 'sar'] = prev_ep
                    df.loc[i, 'ep'] = current_high
                    df.loc[i, 'af_current'] = self.af
                else:
                    # Continue downtrend
                    df.loc[i, 'trend'] = -1
                    df.loc[i, 'sar'] = new_sar
                    
                    # Update EP and AF
                    if current_low < prev_ep:
                        df.loc[i, 'ep'] = current_low
                        df.loc[i, 'af_current'] = min(prev_af + self.af, self.max_af)
                    else:
                        df.loc[i, 'ep'] = prev_ep
                        df.loc[i, 'af_current'] = prev_af
                    
                    # Make sure SAR is above the last two highs
                    df.loc[i, 'sar'] = max(df.loc[i, 'sar'],
                                          df.loc[i-1, 'high'],
                                          df.loc[i, 'high'])
        
        return df
    
    def get_current_sar(self) -> Optional[dict]:
        """
        Get current Parabolic SAR value with real-time price
        
        Returns:
            Dictionary with SAR info or None if failed
        """
        # Get historical data
        df = self.get_historical_data(bars=100)
        
        if df is None:
            return None
        
        # Calculate SAR
        df = self.calculate_sar(df)
        
        # Get current values
        current = df.iloc[-1]
        
        # Get real-time price
        if not mt5.initialize():
            return None
        
        tick = mt5.symbol_info_tick(self.symbol)
        mt5.shutdown()
        
        if tick is None:
            return None
        
        return {
            'symbol': self.symbol,
            'timeframe': self._timeframe_to_string(self.timeframe),
            'current_price': tick.bid,
            'sar_value': round(current['sar'], 2),
            'trend': 'UPTREND' if current['trend'] == 1 else 'DOWNTREND',
            'trend_signal': 'BUY' if current['trend'] == 1 else 'SELL',
            'extreme_point': round(current['ep'], 2),
            'acceleration_factor': round(current['af_current'], 4),
            'distance_to_sar': round(abs(tick.bid - current['sar']), 2),
            'distance_percentage': round(abs(tick.bid - current['sar']) / tick.bid * 100, 3),
            'timestamp': current['time']
        }
    
    def get_sar_stop_loss(self, position_type: str = 'BUY') -> Optional[float]:
        """
        Get SAR-based stop loss level
        
        Args:
            position_type: 'BUY' or 'SELL'
            
        Returns:
            Stop loss price based on SAR or None if failed
        """
        sar_info = self.get_current_sar()
        
        if sar_info is None:
            return None
        
        # For BUY position, SAR should be below current price
        # For SELL position, SAR should be above current price
        if position_type.upper() == 'BUY':
            if sar_info['trend'] == 'UPTREND':
                return sar_info['sar_value']
            else:
                print("⚠️ Warning: SAR indicates DOWNTREND for BUY position")
                return sar_info['sar_value']
        else:  # SELL
            if sar_info['trend'] == 'DOWNTREND':
                return sar_info['sar_value']
            else:
                print("⚠️ Warning: SAR indicates UPTREND for SELL position")
                return sar_info['sar_value']
    
    def _timeframe_to_string(self, timeframe: int) -> str:
        """Convert MT5 timeframe constant to string"""
        timeframes = {
            mt5.TIMEFRAME_M1: '1M',
            mt5.TIMEFRAME_M5: '5M',
            mt5.TIMEFRAME_M15: '15M',
            mt5.TIMEFRAME_M30: '30M',
            mt5.TIMEFRAME_H1: '1H',
            mt5.TIMEFRAME_H4: '4H',
            mt5.TIMEFRAME_D1: '1D',
        }
        return timeframes.get(timeframe, 'UNKNOWN')
    
    def display_sar_info(self):
        """Display current SAR information in formatted way"""
        sar_info = self.get_current_sar()
        
        if sar_info is None:
            print("❌ Failed to get SAR information")
            return
        
        print("\n" + "=" * 60)
        print("🔮 Parabolic SAR Indicator Analysis")
        print("=" * 60)
        print(f"📊 Symbol: {sar_info['symbol']}")
        print(f"⏱️  Timeframe: {sar_info['timeframe']}")
        print(f"💰 Current Price: {sar_info['current_price']}")
        print(f"📍 SAR Value: {sar_info['sar_value']}")
        print(f"📈 Trend: {sar_info['trend']}")
        print(f"🎯 Signal: {sar_info['trend_signal']}")
        print(f"🔝 Extreme Point: {sar_info['extreme_point']}")
        print(f"⚡ Acceleration: {sar_info['acceleration_factor']}")
        print(f"📏 Distance to SAR: {sar_info['distance_to_sar']} ({sar_info['distance_percentage']}%)")
        print(f"🕐 Last Update: {sar_info['timestamp']}")
        print("=" * 60)


def main():
    """
    Example usage of Parabolic SAR indicator
    """
    print("🔮 Parabolic SAR Indicator - Real-Time Analysis")
    print("=" * 60)
    
    # Initialize SAR indicator for XAUUSD on 15-minute timeframe
    sar = ParabolicSAR(
        symbol="XAUUSD",
        timeframe=mt5.TIMEFRAME_M15,
        acceleration=0.02,
        maximum=0.2
    )
    
    # Display current SAR information
    sar.display_sar_info()
    
    # Get SAR-based stop loss for a BUY position
    print("\n📊 SAR-Based Stop Loss Levels:")
    buy_sl = sar.get_sar_stop_loss('BUY')
    if buy_sl:
        print(f"   BUY Position SL: {buy_sl}")
    
    sell_sl = sar.get_sar_stop_loss('SELL')
    if sell_sl:
        print(f"   SELL Position SL: {sell_sl}")
    
    print("\n✅ Analysis Complete")


if __name__ == "__main__":
    main()
