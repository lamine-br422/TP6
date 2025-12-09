from dataclasses import dataclass
from .event import Event

@dataclass
class Trip(Event):
    destination: str = ""

    def describe(self) -> str:
        d = self.destination or "(TBD)"
        return f"Trip: {self.event_name} to {d}"
