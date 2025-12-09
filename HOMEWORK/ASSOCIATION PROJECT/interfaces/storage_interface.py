from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List, Dict


class StorageInterface(ABC):
    @abstractmethod
    def load_members(self) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def load_events(self) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def load_subscriptions(self) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def load_donations(self) -> List[Dict[str, Any]]:
        ...
    
    @abstractmethod
    def save_members(self, members: List[Dict[str, Any]]) -> None:
        ...
    
    @abstractmethod
    def save_events(self, events: List[Dict[str, Any]]) -> None:
        ...
    
    @abstractmethod
    def save_subscriptions(self, subscriptions: List[Dict[str, Any]]) -> None:
        ...
    
    @abstractmethod
    def save_donations(self, donations: List[Dict[str, Any]]) -> None:
        ...