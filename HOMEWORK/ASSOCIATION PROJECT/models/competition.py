from dataclasses import dataclass
from .event import Event

@dataclass
class Competition(Event):
    level: str = "local"

    def describe(self) -> str:
        return f"Competition: {self.event_name} ({self.level})"
