from dataclasses import dataclass
from datetime import date
from .event import Event

@dataclass
class Meeting(Event):
    room: str = "Room A"

    def describe(self) -> str:
        return f"Meeting: {self.event_name} in {self.room}"
