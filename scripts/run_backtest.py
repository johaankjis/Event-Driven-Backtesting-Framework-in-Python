"""
Main script to run the complete backtest with visualization.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from examples.mean_reversion_demo import run_backtest
from visualization.dashboard import create_dashboard


async def main():
    """
    Run complete backtest and generate visualizations.
    """
    # Create results directory if it doesn't exist
    os.makedirs('results', exist_ok=True)
    
    # Run backtest
    portfolio, metrics, equity_df, trades_df = await run_backtest()
    
    # Generate dashboard
    create_dashboard(equity_df, metrics, trades_df)
    
    print("\n" + "="*60)
    print("BACKTEST COMPLETE!")
    print("="*60)
    print("\nResults saved to:")
    print("  - results/trade_log.csv")
    print("  - results/equity_curve.csv")
    print("  - results/pnl_curve.png")
    print("  - results/drawdown_chart.png")
    print("  - results/rolling_sharpe.png")
    print("  - results/returns_distribution.png")
    print("  - results/dashboard.png")
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(main())
