from typing import Callable, Dict, List, Any
from collections import defaultdict
from datetime import datetime


class Event:                                                    # represents a domain event with timestamp and payload
    def __init__(self, event_type, data: Dict[str, Any]):
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"Event({self.event_type.value}, {self.timestamp.strftime('%H:%M:%S')})"


class EventBus:                                                 # event dispatcher, pub-sub pattern
    def __init__(self):
        self._listeners: Dict[Any, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type, callback: Callable):        # registers a listener for an event type
        self._listeners[event_type].append(callback)

    def unsubscribe(self, event_type, callback: Callable):      # removes a listener
        if callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)

    def emit(self, event_type, data: Dict[str, Any] = None):    # emits an event to all subscribers
        if data is None:
            data = {}
        event = Event(event_type, data)
        for callback in self._listeners[event_type]:
            try:
                callback(event)
            except Exception as e:
                print(f"Error in event handler for {event_type.value}: {e}")
        return event
