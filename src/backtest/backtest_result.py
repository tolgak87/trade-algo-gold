"""
Backtest Result Analysis
Performance metrics and reporting for backtests
"""

from typing import Dict, List
import os
import json
from datetime import datetime


class BacktestResult:
    """
    Analyzes and presents backtest results
    Calculates performance metrics and generates reports
    """
    
    def __init__(self, engine: 'BacktestEngine'):
        """
        Initialize with completed backtest engine
        
        Args:
            engine: BacktestEngine instance with completed backtest
        """
        self.engine = engine
        self.calculate_metrics()
    
    def calculate_metrics(self):
        """Calculate all performance metrics"""
        # Basic metrics
        self.initial_balance = self.engine.initial_balance
        self.final_balance = self.engine.current_balance
        self.net_profit = self.final_balance - self.initial_balance
        self.return_percentage = (self.net_profit / self.initial_balance) * 100
        
        # Trade statistics
        self.total_trades = self.engine.total_trades
        self.winning_trades = self.engine.winning_trades
        self.losing_trades = self.engine.losing_trades
        self.win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        # Profit metrics
        self.total_profit = self.engine.total_profit
        self.total_loss = self.engine.total_loss
        self.profit_factor = (self.total_profit / self.total_loss) if self.total_loss > 0 else 0
        
        # Average trades
        self.avg_win = (self.total_profit / self.winning_trades) if self.winning_trades > 0 else 0
        self.avg_loss = (self.total_loss / self.losing_trades) if self.losing_trades > 0 else 0
        
        # Drawdown
        self.max_drawdown = self.calculate_max_drawdown()
        self.max_drawdown_pct = (self.max_drawdown / self.initial_balance) * 100
        
        # Best/Worst trades
        if self.engine.trades:
            profits = [t['profit'] for t in self.engine.trades]
            self.best_trade = max(profits)
            self.worst_trade = min(profits)
            self.avg_trade = sum(profits) / len(profits)
        else:
            self.best_trade = 0
            self.worst_trade = 0
            self.avg_trade = 0
        
        # Duration
        if self.engine.trades:
            durations = [t['duration'] for t in self.engine.trades]
            self.avg_trade_duration = sum(durations) / len(durations)
        else:
            self.avg_trade_duration = 0
    
    def calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown from equity curve"""
        if not self.engine.equity_curve:
            return 0
        
        peak = self.initial_balance
        max_dd = 0
        
        for point in self.engine.equity_curve:
            balance = point['balance']
            if balance > peak:
                peak = balance
            
            drawdown = peak - balance
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
    
    def print_summary(self):
        """Print backtest results summary"""
        print("\n" + "="*70)
        print("📊 BACKTEST RESULTS")
        print("="*70)
        
        # Account Performance
        print("\n💰 Account Performance:")
        print(f"   Initial Balance:    ${self.initial_balance:>12,.2f}")
        print(f"   Final Balance:      ${self.final_balance:>12,.2f}")
        print(f"   Net Profit:         ${self.net_profit:>12,.2f}")
        print(f"   Return:             {self.return_percentage:>12.2f}%")
        print(f"   Max Drawdown:       ${self.max_drawdown:>12,.2f} ({self.max_drawdown_pct:.2f}%)")
        
        # Trade Statistics
        print("\n📈 Trade Statistics:")
        print(f"   Total Trades:       {self.total_trades:>12}")
        print(f"   Winning Trades:     {self.winning_trades:>12}")
        print(f"   Losing Trades:      {self.losing_trades:>12}")
        print(f"   Win Rate:           {self.win_rate:>12.2f}%")
        
        # Profit Analysis
        print("\n💵 Profit Analysis:")
        print(f"   Total Profit:       ${self.total_profit:>12,.2f}")
        print(f"   Total Loss:         ${self.total_loss:>12,.2f}")
        print(f"   Profit Factor:      {self.profit_factor:>12.2f}")
        print(f"   Average Win:        ${self.avg_win:>12,.2f}")
        print(f"   Average Loss:       ${self.avg_loss:>12,.2f}")
        
        # Trade Details
        print("\n🎯 Trade Details:")
        print(f"   Best Trade:         ${self.best_trade:>12,.2f}")
        print(f"   Worst Trade:        ${self.worst_trade:>12,.2f}")
        print(f"   Average Trade:      ${self.avg_trade:>12,.2f}")
        print(f"   Avg Duration:       {self.avg_trade_duration:>12.1f} minutes")
        
        # Performance Rating
        print("\n⭐ Performance Rating:")
        rating = self.get_performance_rating()
        print(f"   {rating}")
        
        print("\n" + "="*70)
    
    def get_performance_rating(self) -> str:
        """Get performance rating based on metrics"""
        if self.return_percentage > 20 and self.win_rate > 60 and self.profit_factor > 2:
            return "⭐⭐⭐⭐⭐ EXCELLENT - Strategy looks very promising!"
        elif self.return_percentage > 10 and self.win_rate > 50 and self.profit_factor > 1.5:
            return "⭐⭐⭐⭐ GOOD - Strategy shows potential"
        elif self.return_percentage > 0 and self.profit_factor > 1:
            return "⭐⭐⭐ ACCEPTABLE - Strategy is profitable but needs improvement"
        elif self.return_percentage > 0:
            return "⭐⭐ POOR - Barely profitable, high risk"
        else:
            return "⭐ FAILING - Strategy loses money, needs major revision"
    
    def get_trade_list(self) -> List[Dict]:
        """Get list of all trades"""
        return self.engine.trades
    
    def save_to_file(self, filename: str = None):
        """
        Save backtest results to JSON file
        
        Args:
            filename: Output filename (default: backtest_results_TIMESTAMP.json)
        """
        if filename is None:
            filename = f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        results = {
            'summary': {
                'initial_balance': self.initial_balance,
                'final_balance': self.final_balance,
                'net_profit': self.net_profit,
                'return_percentage': self.return_percentage,
                'max_drawdown': self.max_drawdown,
                'max_drawdown_pct': self.max_drawdown_pct
            },
            'statistics': {
                'total_trades': self.total_trades,
                'winning_trades': self.winning_trades,
                'losing_trades': self.losing_trades,
                'win_rate': self.win_rate,
                'profit_factor': self.profit_factor,
                'avg_win': self.avg_win,
                'avg_loss': self.avg_loss,
                'best_trade': self.best_trade,
                'worst_trade': self.worst_trade,
                'avg_trade': self.avg_trade,
                'avg_duration_minutes': self.avg_trade_duration
            },
            'trades': [
                {
                    **trade,
                    'entry_time': trade['entry_time'].isoformat(),
                    'exit_time': trade['exit_time'].isoformat()
                }
                for trade in self.engine.trades
            ],
            'rating': self.get_performance_rating()
        }
        
        # Ensure directory exists
        os.makedirs("logs/backtest_results", exist_ok=True)
        
        filepath = f"logs/backtest_results/{filename}"
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=4)
        
        print(f"\n💾 Results saved to: {filepath}")
        
        return filepath
    
    def get_monthly_breakdown(self) -> Dict:
        """Get profit breakdown by month"""
        monthly = {}
        
        for trade in self.engine.trades:
            month_key = trade['exit_time'].strftime('%Y-%m')
            if month_key not in monthly:
                monthly[month_key] = {
                    'trades': 0,
                    'profit': 0,
                    'wins': 0,
                    'losses': 0
                }
            
            monthly[month_key]['trades'] += 1
            monthly[month_key]['profit'] += trade['profit']
            if trade['profit'] > 0:
                monthly[month_key]['wins'] += 1
            else:
                monthly[month_key]['losses'] += 1
        
        return monthly
    
    def print_monthly_breakdown(self):
        """Print monthly profit breakdown"""
        monthly = self.get_monthly_breakdown()
        
        if not monthly:
            return
        
        print("\n📅 Monthly Breakdown:")
        print("   " + "-" * 66)
        print(f"   {'Month':<10} {'Trades':<8} {'Wins':<6} {'Losses':<8} {'Profit':>12}")
        print("   " + "-" * 66)
        
        total_trades = 0
        total_wins = 0
        total_losses = 0
        total_profit = 0.0
        
        for month, data in sorted(monthly.items()):
            win_rate = (data['wins'] / data['trades'] * 100) if data['trades'] > 0 else 0
            print(f"   {month:<10} {data['trades']:<8} {data['wins']:<6} {data['losses']:<8} "
                  f"${data['profit']:>10,.2f} ({win_rate:.1f}%)")
            total_trades += data['trades']
            total_wins += data['wins']
            total_losses += data['losses']
            total_profit += data['profit']
        
        print("   " + "=" * 66)
        total_win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
        print(f"   {'TOTAL':<10} {total_trades:<8} {total_wins:<6} {total_losses:<8} "
              f"${total_profit:>10,.2f} ({total_win_rate:.1f}%)")
        print("   " + "=" * 66)
