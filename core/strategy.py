"""
Base strategy class and signal generation logic.
"""
from abc import ABC, abstractmethod
import pandas as pd
from core.event import MarketEvent, SignalEvent, SignalType
from core.event_engine import EventEngine
from core.data_handler import DataHandler


class Strategy(ABC):
    """
    Base strategy class for generating trading signals.
    Supports plug-in architecture for quick prototyping.
    """
    
    def __init__(self, event_engine: EventEngine, data_handler: DataHandler):
        self.event_engine = event_engine
        self.data_handler = data_handler
        
    @abstractmethod
    def calculate_signals(self, event: MarketEvent):
        """
        Calculate trading signals based on market data.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Must implement calculate_signals()")


class MeanReversionStrategy(Strategy):
    """
    Mean reversion strategy using Bollinger Bands.
    Generates signals when price deviates from moving average.
    """
    
    def __init__(self, event_engine: EventEngine, data_handler: DataHandler,
                 symbol: str, lookback: int = 20, num_std: float = 2.0):
        super().__init__(event_engine, data_handler)
        self.symbol = symbol
        self.lookback = lookback
        self.num_std = num_std
        self.position = 0  # Track current position
        
    def calculate_signals(self, event: MarketEvent):
        """
        Generate signals based on Bollinger Band mean reversion.
        """
        if event.symbol != self.symbol:
            return
            
        # Get historical bars
        bars = self.data_handler.get_latest_bars(self.symbol, self.lookback)
        
        if bars is None or len(bars) < self.lookback:
            return
        
        # Calculate Bollinger Bands
        closes = bars['close']
        sma = closes.mean()
        std = closes.std()
        
        upper_band = sma + (self.num_std * std)
        lower_band = sma - (self.num_std * std)
        
        current_price = event.close
        
        # Generate signals
        signal = None
        
        # Price below lower band and no position -> BUY signal
        if current_price < lower_band and self.position == 0:
            signal = SignalEvent(
                timestamp=event.timestamp,
                symbol=self.symbol,
                signal_type=SignalType.LONG,
                strength=min(1.0, (lower_band - current_price) / std)
            )
            self.position = 1
            
        # Price above upper band and have position -> SELL signal
        elif current_price > upper_band and self.position == 1:
            signal = SignalEvent(
                timestamp=event.timestamp,
                symbol=self.symbol,
                signal_type=SignalType.EXIT,
                strength=min(1.0, (current_price - upper_band) / std)
            )
            self.position = 0
            
        # Mean reversion - close to mean
        elif abs(current_price - sma) < 0.5 * std and self.position == 1:
            signal = SignalEvent(
                timestamp=event.timestamp,
                symbol=self.symbol,
                signal_type=SignalType.EXIT,
                strength=0.5
            )
            self.position = 0
        
        if signal:
            self.event_engine.put_event(signal)
