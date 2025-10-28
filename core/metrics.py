"""
Performance metrics calculations: Sharpe, Sortino, drawdown, etc.
"""
import numpy as np
import pandas as pd
from typing import Tuple


class PerformanceMetrics:
    """
    Calculate key performance metrics for backtesting results.
    """
    
    @staticmethod
    def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0, 
                     periods_per_year: int = 252) -> float:
        """
        Calculate annualized Sharpe ratio.
        """
        if len(returns) < 2:
            return 0.0
            
        excess_returns = returns - risk_free_rate / periods_per_year
        
        if excess_returns.std() == 0:
            return 0.0
            
        sharpe = np.sqrt(periods_per_year) * excess_returns.mean() / excess_returns.std()
        return sharpe
    
    @staticmethod
    def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0,
                     periods_per_year: int = 252) -> float:
        """
        Calculate annualized Sortino ratio (uses downside deviation).
        """
        if len(returns) < 2:
            return 0.0
            
        excess_returns = returns - risk_free_rate / periods_per_year
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
            
        sortino = np.sqrt(periods_per_year) * excess_returns.mean() / downside_returns.std()
        return sortino
    
    @staticmethod
    def max_drawdown(equity_curve: pd.Series) -> Tuple[float, pd.Timestamp, pd.Timestamp]:
        """
        Calculate maximum drawdown and its duration.
        Returns: (max_drawdown_pct, start_date, end_date)
        """
        if len(equity_curve) < 2:
            return 0.0, None, None
            
        # Calculate running maximum
        running_max = equity_curve.expanding().max()
        
        # Calculate drawdown
        drawdown = (equity_curve - running_max) / running_max
        
        # Find maximum drawdown
        max_dd = drawdown.min()
        max_dd_end = drawdown.idxmin()
        
        # Find start of maximum drawdown
        max_dd_start = equity_curve[:max_dd_end].idxmax()
        
        return abs(max_dd), max_dd_start, max_dd_end
    
    @staticmethod
    def hit_rate(trades: pd.DataFrame) -> float:
        """
        Calculate hit rate (percentage of profitable trades).
        """
        if len(trades) == 0:
            return 0.0
            
        # Assume trades DataFrame has 'pnl' column
        if 'pnl' not in trades.columns:
            return 0.0
            
        profitable = (trades['pnl'] > 0).sum()
        return profitable / len(trades)
    
    @staticmethod
    def calculate_all_metrics(equity_curve: pd.Series, trades: pd.DataFrame,
                             periods_per_year: int = 252) -> dict:
        """
        Calculate all performance metrics.
        """
        returns = equity_curve.pct_change().dropna()
        
        max_dd, dd_start, dd_end = PerformanceMetrics.max_drawdown(equity_curve)
        
        metrics = {
            'total_return': (equity_curve.iloc[-1] / equity_curve.iloc[0] - 1) * 100,
            'sharpe_ratio': PerformanceMetrics.sharpe_ratio(returns, periods_per_year=periods_per_year),
            'sortino_ratio': PerformanceMetrics.sortino_ratio(returns, periods_per_year=periods_per_year),
            'max_drawdown': max_dd * 100,
            'max_drawdown_start': dd_start,
            'max_drawdown_end': dd_end,
            'total_trades': len(trades),
            'avg_return_per_trade': returns.mean() * 100 if len(returns) > 0 else 0,
            'volatility': returns.std() * np.sqrt(periods_per_year) * 100,
        }
        
        return metrics
