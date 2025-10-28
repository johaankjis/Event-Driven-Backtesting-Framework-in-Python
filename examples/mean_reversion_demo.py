"""
Mean reversion strategy demonstration.
Complete end-to-end backtest example.
"""
import asyncio
from datetime import datetime, timedelta
from core.event_engine import EventEngine
from core.data_handler import DataHandler
from core.strategy import MeanReversionStrategy
from core.portfolio import Portfolio
from core.execution import ExecutionHandler
from core.event import EventType, MarketEvent, SignalEvent, OrderEvent, FillEvent
from core.metrics import PerformanceMetrics
import pandas as pd


async def run_backtest():
    """
    Run a complete backtest with mean reversion strategy.
    """
    print("[v0] Initializing event-driven backtesting framework...")
    
    # Initialize components
    event_engine = EventEngine()
    symbols = ['AAPL']
    data_handler = DataHandler(event_engine, symbols)
    portfolio = Portfolio(event_engine, initial_capital=100000.0)
    execution_handler = ExecutionHandler(event_engine)
    strategy = MeanReversionStrategy(event_engine, data_handler, 'AAPL', lookback=20, num_std=2.0)
    
    # Define event handlers
    def handle_market_event(event: MarketEvent):
        """Handle market data updates."""
        portfolio.update_market_price(event.symbol, event.close, event.timestamp)
        execution_handler.update_market_price(event.symbol, event.close)
        strategy.calculate_signals(event)
    
    def handle_signal_event(event: SignalEvent):
        """Handle trading signals."""
        portfolio.process_signal(event)
    
    async def handle_order_event(event: OrderEvent):
        """Handle order execution."""
        await execution_handler.execute_order(event)
    
    def handle_fill_event(event: FillEvent):
        """Handle order fills."""
        portfolio.process_fill(event)
    
    # Register handlers
    event_engine.register_handler(EventType.MARKET, handle_market_event)
    event_engine.register_handler(EventType.SIGNAL, handle_signal_event)
    event_engine.register_handler(EventType.ORDER, handle_order_event)
    event_engine.register_handler(EventType.FILL, handle_fill_event)
    
    # Load data
    print("[v0] Loading market data...")
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 1, 1)
    await data_handler.load_data(start_date, end_date)
    print(f"[v0] Loaded {len(data_handler.data['AAPL'])} bars for AAPL")
    
    # Run backtest
    print("[v0] Running backtest...")
    bar_count = 0
    while await data_handler.stream_next_bar():
        await event_engine.process_events()
        bar_count += 1
        
        if bar_count % 100 == 0:
            print(f"[v0] Processed {bar_count} bars...")
    
    print(f"[v0] Backtest complete! Processed {bar_count} bars")
    
    # Calculate performance metrics
    print("\n" + "="*60)
    print("BACKTEST RESULTS")
    print("="*60)
    
    equity_df = pd.DataFrame(portfolio.equity_curve, columns=['timestamp', 'equity'])
    equity_df.set_index('timestamp', inplace=True)
    
    trades_df = pd.DataFrame(portfolio.trades)
    
    # Calculate PnL for each trade
    if len(trades_df) > 0:
        trades_df['pnl'] = 0.0
        for i in range(1, len(trades_df)):
            if trades_df.iloc[i]['direction'] == 'SELL':
                # Find matching buy
                buy_price = trades_df.iloc[i-1]['price']
                sell_price = trades_df.iloc[i]['price']
                quantity = trades_df.iloc[i]['quantity']
                trades_df.loc[i, 'pnl'] = (sell_price - buy_price) * quantity
    
    metrics = PerformanceMetrics.calculate_all_metrics(
        equity_df['equity'], 
        trades_df,
        periods_per_year=252 * 6  # Hourly data
    )
    
    print(f"\nInitial Capital: ${portfolio.initial_capital:,.2f}")
    print(f"Final Equity: ${portfolio.get_total_equity():,.2f}")
    print(f"Total Return: {metrics['total_return']:.2f}%")
    print(f"\nSharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"Sortino Ratio: {metrics['sortino_ratio']:.2f}")
    print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
    print(f"Volatility (annualized): {metrics['volatility']:.2f}%")
    print(f"\nTotal Trades: {metrics['total_trades']}")
    print(f"Average Return per Trade: {metrics['avg_return_per_trade']:.4f}%")
    
    if len(trades_df) > 0:
        hit_rate = PerformanceMetrics.hit_rate(trades_df)
        print(f"Hit Rate: {hit_rate * 100:.2f}%")
    
    # Save results
    print("\n" + "="*60)
    print("Saving results...")
    
    # Save trade log
    if len(trades_df) > 0:
        trades_df.to_csv('results/trade_log.csv', index=False)
        print("[v0] Trade log saved to results/trade_log.csv")
    
    # Save equity curve
    equity_df.to_csv('results/equity_curve.csv')
    print("[v0] Equity curve saved to results/equity_curve.csv")
    
    return portfolio, metrics, equity_df, trades_df


if __name__ == "__main__":
    portfolio, metrics, equity_df, trades_df = asyncio.run(run_backtest())
