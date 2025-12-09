from __future__ import annotations
from typing import List, Dict, Any
from interfaces.storage_interface import StorageInterface
from observers.data_observer import Subject


class EventController(Subject):
    """Controller pour gérer les opérations sur les événements"""
    
    def __init__(self, storage: StorageInterface) -> None:
        super().__init__()
        self._storage = storage
        
    def get_all_events(self) -> List[Dict[str, Any]]:
        """Récupère tous les événements depuis le storage"""
        return self._storage.load_events()
    
    def get_event_by_name(self, event_name: str) -> Dict[str, Any] | None:
        """Récupère un événement par son nom"""
        events = self.get_all_events()
        for event in events:
            if event.get("event_name") == event_name:
                return event
        return None
    
    def get_events_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Récupère les événements pour une date donnée"""
        events = self.get_all_events()
        return [e for e in events if e.get("event_date") == date]
    
    def add_event(self, event: Dict[str, Any]) -> None:
        """Ajoute un nouvel événement"""
        events = self.get_all_events()
        events.append(event)
        self._storage.save_events(events)
        self.notify("event_added", event)
    
    def delete_event(self, event_name: str) -> bool:
        """Supprime un événement par son nom"""
        events = self.get_all_events()
        original_count = len(events)
        events = [e for e in events if e.get("event_name") != event_name]
        
        if len(events) < original_count:
            self._storage.save_events(events)
            self.notify("event_deleted", {"event_name": event_name})
            return True
        return False

