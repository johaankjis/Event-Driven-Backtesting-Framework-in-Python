"""
Portfolio manager for tracking positions, PnL, and performance.
"""
import pandas as pd
from datetime import datetime
from typing import Dict, List
from core.event import FillEvent, SignalEvent, OrderEvent, SignalType, OrderType
from core.event_engine import EventEngine


class Portfolio:
    """
    Tracks holdings, PnL, and performance metrics.
    Generates orders based on signals.
    """
    
    def __init__(self, event_engine: EventEngine, initial_capital: float = 100000.0):
        self.event_engine = event_engine
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # Position tracking
        self.positions: Dict[str, int] = {}  # symbol -> quantity
        self.holdings: Dict[str, float] = {}  # symbol -> current value
        
        # Performance tracking
        self.equity_curve: List[tuple] = []  # (timestamp, equity)
        self.trades: List[Dict] = []
        self.current_prices: Dict[str, float] = {}
        
    def update_market_price(self, symbol: str, price: float, timestamp: datetime):
        """Update current market price and recalculate portfolio value."""
        self.current_prices[symbol] = price
        
        # Update holdings value
        if symbol in self.positions:
            self.holdings[symbol] = self.positions[symbol] * price
            
        # Calculate total equity
        total_equity = self.current_capital + sum(self.holdings.values())
        self.equity_curve.append((timestamp, total_equity))
        
    def process_signal(self, event: SignalEvent):
        """
        Process signal and generate order.
        Uses simple position sizing based on signal strength.
        """
        symbol = event.symbol
        
        # Simple position sizing: use 10% of capital per trade
        position_size = int((self.current_capital * 0.1 * event.strength) / 
                           self.current_prices.get(symbol, 100))
        
        if position_size == 0:
            return
            
        # Generate order based on signal type
        if event.signal_type == SignalType.LONG:
            order = OrderEvent(
                timestamp=event.timestamp,
                symbol=symbol,
                order_type=OrderType.MARKET,
                quantity=position_size,
                direction='BUY'
            )
            self.event_engine.put_event(order)
            
        elif event.signal_type == SignalType.SHORT:
            order = OrderEvent(
                timestamp=event.timestamp,
                symbol=symbol,
                order_type=OrderType.MARKET,
                quantity=position_size,
                direction='SELL'
            )
            self.event_engine.put_event(order)
            
        elif event.signal_type == SignalType.EXIT:
            # Close existing position
            if symbol in self.positions and self.positions[symbol] > 0:
                order = OrderEvent(
                    timestamp=event.timestamp,
                    symbol=symbol,
                    order_type=OrderType.MARKET,
                    quantity=self.positions[symbol],
                    direction='SELL'
                )
                self.event_engine.put_event(order)
                
    def process_fill(self, event: FillEvent):
        """Update portfolio based on fill event."""
        symbol = event.symbol
        
        # Update positions
        if symbol not in self.positions:
            self.positions[symbol] = 0
            
        if event.direction == 'BUY':
            self.positions[symbol] += event.quantity
            cost = event.fill_price * event.quantity + event.commission
            self.current_capital -= cost
        else:
            self.positions[symbol] -= event.quantity
            proceeds = event.fill_price * event.quantity - event.commission
            self.current_capital += proceeds
            
        # Update holdings
        if symbol in self.current_prices:
            self.holdings[symbol] = self.positions[symbol] * self.current_prices[symbol]
            
        # Log trade
        self.trades.append({
            'timestamp': event.timestamp,
            'symbol': symbol,
            'direction': event.direction,
            'quantity': event.quantity,
            'price': event.fill_price,
            'commission': event.commission,
            'slippage': event.slippage
        })
        
    def get_total_equity(self) -> float:
        """Calculate total portfolio equity."""
        return self.current_capital + sum(self.holdings.values())
    
    def get_returns(self) -> pd.Series:
        """Get portfolio returns as a pandas Series."""
        if not self.equity_curve:
            return pd.Series()
            
        df = pd.DataFrame(self.equity_curve, columns=['timestamp', 'equity'])
        df.set_index('timestamp', inplace=True)
        returns = df['equity'].pct_change().dropna()
        return returns
