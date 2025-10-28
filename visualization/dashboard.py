"""
Comprehensive dashboard for backtest visualization.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from visualization.plots import plot_equity_curve, plot_drawdown, plot_rolling_sharpe, plot_returns_distribution


def create_dashboard(equity_df: pd.DataFrame, metrics: dict, trades_df: pd.DataFrame):
    """
    Create a comprehensive dashboard with all key visualizations.
    """
    print("\n[v0] Generating visualization dashboard...")
    
    # Create individual plots
    plot_equity_curve(equity_df, save_path='results/pnl_curve.png')
    plot_drawdown(equity_df, save_path='results/drawdown_chart.png')
    plot_rolling_sharpe(equity_df, window=50, save_path='results/rolling_sharpe.png')
    plot_returns_distribution(equity_df, save_path='results/returns_distribution.png')
    
    # Create combined dashboard
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # 1. Equity Curve
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(equity_df.index, equity_df['equity'], linewidth=2, color='#2E86AB')
    ax1.fill_between(equity_df.index, equity_df['equity'], alpha=0.3, color='#2E86AB')
    ax1.set_title('Portfolio Equity Curve', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Equity ($)', fontsize=10)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    ax1.grid(True, alpha=0.3)
    
    # 2. Drawdown
    ax2 = fig.add_subplot(gs[1, 0])
    running_max = equity_df['equity'].expanding().max()
    drawdown = (equity_df['equity'] - running_max) / running_max * 100
    ax2.fill_between(drawdown.index, drawdown, 0, alpha=0.5, color='#A23B72')
    ax2.plot(drawdown.index, drawdown, linewidth=1.5, color='#A23B72')
    ax2.set_title('Drawdown', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Drawdown (%)', fontsize=10)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.grid(True, alpha=0.3)
    
    # 3. Returns Distribution
    ax3 = fig.add_subplot(gs[1, 1])
    returns = equity_df['equity'].pct_change().dropna() * 100
    ax3.hist(returns, bins=40, alpha=0.7, color='#6A4C93', edgecolor='black')
    ax3.axvline(returns.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {returns.mean():.3f}%')
    ax3.set_title('Returns Distribution', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Return (%)', fontsize=10)
    ax3.set_ylabel('Frequency', fontsize=10)
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. Performance Metrics Table
    ax4 = fig.add_subplot(gs[2, :])
    ax4.axis('off')
    
    metrics_data = [
        ['Total Return', f"{metrics['total_return']:.2f}%"],
        ['Sharpe Ratio', f"{metrics['sharpe_ratio']:.2f}"],
        ['Sortino Ratio', f"{metrics['sortino_ratio']:.2f}"],
        ['Max Drawdown', f"{metrics['max_drawdown']:.2f}%"],
        ['Volatility', f"{metrics['volatility']:.2f}%"],
        ['Total Trades', f"{metrics['total_trades']}"],
    ]
    
    table = ax4.table(cellText=metrics_data, colLabels=['Metric', 'Value'],
                     cellLoc='left', loc='center',
                     colWidths=[0.3, 0.2])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)
    
    # Style the table
    for i in range(len(metrics_data) + 1):
        if i == 0:
            table[(i, 0)].set_facecolor('#2E86AB')
            table[(i, 1)].set_facecolor('#2E86AB')
            table[(i, 0)].set_text_props(weight='bold', color='white')
            table[(i, 1)].set_text_props(weight='bold', color='white')
        else:
            table[(i, 0)].set_facecolor('#E8F4F8' if i % 2 == 0 else 'white')
            table[(i, 1)].set_facecolor('#E8F4F8' if i % 2 == 0 else 'white')
    
    plt.suptitle('Backtest Performance Dashboard', fontsize=18, fontweight='bold', y=0.98)
    
    plt.savefig('results/dashboard.png', dpi=300, bbox_inches='tight')
    print("[v0] Dashboard saved to results/dashboard.png")
    plt.close()
    
    print("[v0] All visualizations generated successfully!")
