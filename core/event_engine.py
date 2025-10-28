"""
Async event engine for dispatching and handling events.
"""
import asyncio
from collections import deque
from typing import Callable, Dict, List
from core.event import Event, EventType


class EventEngine:
    """
    Central event dispatcher managing events in FIFO order.
    Uses asyncio for concurrent event handling.
    """
    
    def __init__(self):
        self.event_queue = deque()
        self.handlers: Dict[EventType, List[Callable]] = {
            event_type: [] for event_type in EventType
        }
        self.running = False
        
    def register_handler(self, event_type: EventType, handler: Callable):
        """Register an event handler for a specific event type."""
        self.handlers[event_type].append(handler)
        
    def put_event(self, event: Event):
        """Add an event to the queue."""
        self.event_queue.append(event)
        
    async def process_events(self):
        """Process all events in the queue asynchronously."""
        while self.event_queue:
            event = self.event_queue.popleft()
            
            # Get handlers for this event type
            handlers = self.handlers.get(event.event_type, [])
            
            # Execute all handlers for this event
            for handler in handlers:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
                    
    async def run(self):
        """Main event loop."""
        self.running = True
        while self.running:
            if self.event_queue:
                await self.process_events()
            else:
                await asyncio.sleep(0.001)  # Small delay to prevent busy waiting
                
    def stop(self):
        """Stop the event engine."""
        self.running = False
