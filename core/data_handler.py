"""
Asynchronous market data handler for streaming historical data.
"""
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional
from core.event import MarketEvent
from core.event_engine import EventEngine


class DataHandler:
    """
    Streams historical market data as MarketEvents.
    Supports asynchronous I/O for faster loading.
    """
    
    def __init__(self, event_engine: EventEngine, symbols: List[str]):
        self.event_engine = event_engine
        self.symbols = symbols
        self.data: Dict[str, pd.DataFrame] = {}
        self.current_index = 0
        
    def generate_synthetic_data(self, symbol: str, start_date: datetime, 
                                end_date: datetime, freq: str = '1H') -> pd.DataFrame:
        """
        Generate synthetic OHLCV data for demonstration.
        Uses geometric Brownian motion with mean reversion.
        """
        dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        n = len(dates)
        
        # Parameters for price simulation
        initial_price = 100.0
        drift = 0.0001
        volatility = 0.02
        mean_reversion_strength = 0.05
        mean_price = initial_price
        
        # Generate prices with mean reversion
        prices = [initial_price]
        for i in range(1, n):
            # Mean reversion component
            reversion = mean_reversion_strength * (mean_price - prices[-1])
            # Random walk component
            random_shock = np.random.normal(drift + reversion, volatility)
            new_price = prices[-1] * (1 + random_shock)
            prices.append(new_price)
        
        # Generate OHLC from close prices
        df = pd.DataFrame(index=dates)
        df['close'] = prices
        df['open'] = df['close'].shift(1).fillna(initial_price)
        
        # High and low with realistic spreads
        spread = df['close'] * 0.005  # 0.5% spread
        df['high'] = df[['open', 'close']].max(axis=1) + spread * np.random.uniform(0, 1, n)
        df['low'] = df[['open', 'close']].min(axis=1) - spread * np.random.uniform(0, 1, n)
        
        # Volume
        df['volume'] = np.random.lognormal(10, 1, n)
        
        return df
    
    async def load_data(self, start_date: datetime, end_date: datetime):
        """Load or generate data for all symbols asynchronously."""
        tasks = []
        for symbol in self.symbols:
            # Simulate async I/O
            await asyncio.sleep(0.01)
            df = self.generate_synthetic_data(symbol, start_date, end_date)
            self.data[symbol] = df
            
    def get_latest_bars(self, symbol: str, n: int = 1) -> Optional[pd.DataFrame]:
        """Get the latest N bars for a symbol."""
        if symbol not in self.data:
            return None
        
        if self.current_index < n:
            return None
            
        return self.data[symbol].iloc[self.current_index - n:self.current_index]
    
    async def stream_next_bar(self):
        """Stream the next bar for all symbols as MarketEvents."""
        if not self.data:
            return False
            
        # Check if we've reached the end
        max_length = min(len(df) for df in self.data.values())
        if self.current_index >= max_length:
            return False
        
        # Create market events for all symbols
        for symbol in self.symbols:
            df = self.data[symbol]
            bar = df.iloc[self.current_index]
            
            event = MarketEvent(
                timestamp=df.index[self.current_index],
                symbol=symbol,
                open=bar['open'],
                high=bar['high'],
                low=bar['low'],
                close=bar['close'],
                volume=bar['volume']
            )
            
            self.event_engine.put_event(event)
        
        self.current_index += 1
        return True
