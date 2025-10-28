"""
Plotting utilities for backtest visualization.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional


# Set style
sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (12, 8)


def plot_equity_curve(equity_df: pd.DataFrame, save_path: Optional[str] = None):
    """
    Plot cumulative PnL curve.
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    
    ax.plot(equity_df.index, equity_df['equity'], linewidth=2, color='#2E86AB', label='Portfolio Equity')
    ax.fill_between(equity_df.index, equity_df['equity'], alpha=0.3, color='#2E86AB')
    
    ax.set_title('Portfolio Equity Curve', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Equity ($)', fontsize=12)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"[v0] Equity curve saved to {save_path}")
    
    plt.close()


def plot_drawdown(equity_df: pd.DataFrame, save_path: Optional[str] = None):
    """
    Plot drawdown chart.
    """
    # Calculate drawdown
    running_max = equity_df['equity'].expanding().max()
    drawdown = (equity_df['equity'] - running_max) / running_max * 100
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    ax.fill_between(drawdown.index, drawdown, 0, alpha=0.5, color='#A23B72', label='Drawdown')
    ax.plot(drawdown.index, drawdown, linewidth=2, color='#A23B72')
    
    ax.set_title('Portfolio Drawdown', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Drawdown (%)', fontsize=12)
    ax.legend(loc='lower left', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Add horizontal line at 0
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"[v0] Drawdown chart saved to {save_path}")
    
    plt.close()


def plot_rolling_sharpe(equity_df: pd.DataFrame, window: int = 50, 
                        save_path: Optional[str] = None):
    """
    Plot rolling Sharpe ratio.
    """
    returns = equity_df['equity'].pct_change().dropna()
    
    # Calculate rolling Sharpe
    rolling_sharpe = returns.rolling(window=window).mean() / returns.rolling(window=window).std() * np.sqrt(252 * 6)
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    ax.plot(rolling_sharpe.index, rolling_sharpe, linewidth=2, color='#F18F01', label=f'{window}-Period Rolling Sharpe')
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax.axhline(y=1.5, color='green', linestyle='--', linewidth=1, alpha=0.5, label='Target Sharpe (1.5)')
    
    ax.set_title('Rolling Sharpe Ratio', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Sharpe Ratio', fontsize=12)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"[v0] Rolling Sharpe chart saved to {save_path}")
    
    plt.close()


def plot_returns_distribution(equity_df: pd.DataFrame, save_path: Optional[str] = None):
    """
    Plot returns distribution histogram.
    """
    returns = equity_df['equity'].pct_change().dropna() * 100  # Convert to percentage
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    ax.hist(returns, bins=50, alpha=0.7, color='#6A4C93', edgecolor='black')
    
    # Add vertical lines for mean and median
    ax.axvline(returns.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {returns.mean():.3f}%')
    ax.axvline(returns.median(), color='green', linestyle='--', linewidth=2, label=f'Median: {returns.median():.3f}%')
    
    ax.set_title('Returns Distribution', fontsize=16, fontweight='bold')
    ax.set_xlabel('Return (%)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"[v0] Returns distribution saved to {save_path}")
    
    plt.close()
