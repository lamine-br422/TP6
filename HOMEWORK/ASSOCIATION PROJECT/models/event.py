from dataclasses import dataclass, field
from datetime import date
from typing import List

@dataclass
class Event:
    event_name: str
    description: str
    event_date: date
    organizers: List['Teacher'] = field(default_factory=list)
    participants: List['Student'] = field(default_factory=list)

    def display(self) -> str:
        return f"{self.event_name} | {self.event_date.isoformat()}"

    def add_participant(self, s: 'Student') -> None:
        if s not in self.participants:
            self.participants.append(s)

    def remove_participant(self, s: 'Student') -> None:
        if s in self.participants:
            self.participants.remove(s)
