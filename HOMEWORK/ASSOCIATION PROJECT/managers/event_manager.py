from typing import List
from models.event import Event
from interfaces.storage import Storage

class EventManager:
    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    def save_all(self, events: List[Event]) -> None:
        payload = []
        for e in events:
            payload.append({
                "event_name": e.event_name,
                "description": e.description,
                "event_date": e.event_date.isoformat(),
                # On stocke des IDs simples pour rester sérialisable
                "organizer_ids": [getattr(o, "teacher_id", None) for o in e.organizers],
                "participant_ids": [getattr(s, "student_id", None) for s in e.participants],
            })
        self._storage.save_events(payload)
