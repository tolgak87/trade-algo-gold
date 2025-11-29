"""
Backtesting Application Launcher
Simple entry point to run strategy backtests
"""

from backtest.backtest_engine import BacktestEngine
from datetime import datetime, timedelta


def run_backtest_demo():
    """
    Run a demonstration backtest
    Tests last 2 months of data with 1-minute bars
    """
    print("\n" + "="*70)
    print("🔬 GOLD TRADING BOT - BACKTEST MODE")
    print("="*70)
    
    # Configuration
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)  # Last 2 month
    
    print(f"\n⚙️  Backtest Configuration:")
    print(f"   Symbol: XAUUSD")
    print(f"   Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"   Strategy: Parabolic SAR (1M timeframe - like live bot!)")
    print(f"   Initial Balance: $10,000")
    print(f"   Risk per Trade: 1%")
    print(f"   Signals: BUY ONLY (Long positions in uptrend)")
    
    # Create backtest engine
    engine = BacktestEngine(
        symbol="XAUUSD",
        initial_balance=10000.0,
        risk_percentage=1.0
    )
    
    # Run backtest
    try:
        result = engine.run_backtest(
            start_date=start_date,
            end_date=end_date,
            desired_signal='BUY'  # Only BUY signals (long in uptrend)
        )
        
        # Display results
        result.print_summary()
        result.print_monthly_breakdown()
        
        # Save results
        result.save_to_file()
        
        # Show recommendations
        print("\n💡 Recommendations:")
        if result.return_percentage > 0:
            print("   ✅ Strategy is profitable on historical data")
            print("   ✅ Consider testing on demo account next")
            if result.win_rate < 50:
                print("   ⚠️  Win rate is low - consider tighter stop loss")
            if result.max_drawdown_pct > 20:
                print("   ⚠️  High drawdown - consider reducing risk percentage")
        else:
            print("   ❌ Strategy loses money on this period")
            print("   ❌ DO NOT use on live account")
            print("   💡 Try different parameters or timeframes")
        
    except Exception as e:
        print(f"\n❌ Backtest failed: {e}")
        print("\n💡 Make sure:")
        print("   1. MetaTrader5 is installed")
        print("   2. MT5 has historical data for XAUUSD")
        print("   3. MT5 can be accessed (demo account is fine)")
        return
    
    print("\n" + "="*70)
    print("✅ Backtest Complete!")
    print("="*70)


def run_custom_backtest(start_date: datetime, 
                       end_date: datetime,
                       initial_balance: float = 10000.0,
                       risk_percentage: float = 1.0,
                       desired_signal: str = 'BOTH'):
    """
    Run custom backtest with specific parameters
    
    Args:
        start_date: Backtest start date
        end_date: Backtest end date
        initial_balance: Starting balance
        risk_percentage: Risk per trade
        desired_signal: 'BUY', 'SELL', or 'BOTH'
    """
    print(f"\n🔬 Running custom backtest...")
    
    engine = BacktestEngine(
        symbol="XAUUSD",
        initial_balance=initial_balance,
        risk_percentage=risk_percentage
    )
    
    result = engine.run_backtest(start_date, end_date, desired_signal)
    result.print_summary()
    result.print_monthly_breakdown()
    result.save_to_file()
    
    return result


def quick_test_last_week():
    """Quick test on last week of data"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print("\n🚀 Quick Test - Last Week")
    
    engine = BacktestEngine(symbol="XAUUSD", initial_balance=10000.0, risk_percentage=1.0)
    result = engine.run_backtest(start_date, end_date, 'BOTH')
    result.print_summary()
    
    return result


def test_different_risks():
    """Test different risk percentages"""
    print("\n📊 Testing Different Risk Levels...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    
    risk_levels = [0.5, 1.0, 2.0, 3.0]
    results = []
    
    for risk in risk_levels:
        print(f"\n{'='*70}")
        print(f"Testing Risk: {risk}%")
        print(f"{'='*70}")
        
        engine = BacktestEngine(
            symbol="XAUUSD",
            initial_balance=10000.0,
            risk_percentage=risk
        )
        
        result = engine.run_backtest(start_date, end_date, 'BOTH')
        results.append({
            'risk': risk,
            'return': result.return_percentage,
            'max_dd': result.max_drawdown_pct,
            'win_rate': result.win_rate,
            'trades': result.total_trades
        })
    
    # Summary
    print("\n" + "="*70)
    print("📊 RISK COMPARISON SUMMARY")
    print("="*70)
    print(f"{'Risk %':<10} {'Return %':<12} {'Max DD %':<12} {'Win Rate %':<12} {'Trades':<10}")
    print("-"*70)
    
    for r in results:
        print(f"{r['risk']:<10.1f} {r['return']:<12.2f} {r['max_dd']:<12.2f} {r['win_rate']:<12.2f} {r['trades']:<10}")
    
    print("="*70)


if __name__ == "__main__":
    # Default: Run demo backtest
    run_backtest_demo()
    
    # Uncomment to test other scenarios:
    # quick_test_last_week()
    # test_different_risks()
    
    # Custom date range example:
    # start = datetime(2024, 10, 1)
    # end = datetime(2024, 11, 28)
    # run_custom_backtest(start, end, initial_balance=10000, risk_percentage=1.0)
