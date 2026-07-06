"""
Integration Tests for Event Bus
"""
import pytest
import asyncio
from backend.infrastructure.event_bus.models import BaseEvent
from backend.infrastructure.event_bus.bus import event_bus
from backend.infrastructure.event_bus.publisher import EventPublisher
from backend.infrastructure.event_bus.subscriber import EventHandler

class DummyEvent(BaseEvent):
    """A test event."""
    message: str

class DummyHandler(EventHandler):
    """A test handler."""
    def __init__(self):
        self.received_events = []

    async def handle(self, event: BaseEvent) -> None:
        self.received_events.append(event)

class FailingHandler(EventHandler):
    """A test handler that always fails to ensure dispatcher resilience."""
    async def handle(self, event: BaseEvent) -> None:
        raise ValueError("Intentional failure")


@pytest.mark.asyncio
async def test_event_bus_publish_subscribe():
    """Verifies that an event published to the bus reaches registered subscribers."""
    handler = DummyHandler()
    event_bus.subscribe(DummyEvent, handler)
    
    event = DummyEvent(message="Hello World")
    await EventPublisher.publish(event)
    
    # Allow async tasks to flush
    await asyncio.sleep(0.1)
    
    assert len(handler.received_events) == 1
    assert handler.received_events[0].message == "Hello World"
    assert handler.received_events[0].event_id == event.event_id


@pytest.mark.asyncio
async def test_event_bus_resilience():
    """Verifies that a failing handler does not crash the dispatcher."""
    handler1 = FailingHandler()
    handler2 = DummyHandler()
    
    event_bus.subscribe(DummyEvent, handler1)
    event_bus.subscribe(DummyEvent, handler2)
    
    event = DummyEvent(message="Resilience Test")
    
    # Should not raise an exception to the publisher
    await EventPublisher.publish(event)
    
    await asyncio.sleep(0.1)
    
    # The second handler should still have received the event despite the first failing
    assert len(handler2.received_events) > 0
    assert handler2.received_events[-1].message == "Resilience Test"
