from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List

from interfaces.storage_interface import StorageInterface


class JSONStorage(StorageInterface):
    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir

    def _load_array(self, filename: str) -> List[Dict[str, Any]]:
        path = self._base_dir / filename
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
            return []
        except Exception:
            return []

    def load_members(self) -> List[Dict[str, Any]]:
        return self._load_array("members.json")

    def load_events(self) -> List[Dict[str, Any]]:
        return self._load_array("events.json")

    def load_subscriptions(self) -> List[Dict[str, Any]]:
        return self._load_array("subscriptions.json")

    def load_donations(self) -> List[Dict[str, Any]]:
        return self._load_array("donations.json")
    
    def _save_array(self, filename: str, data: List[Dict[str, Any]]) -> None:
        """Sauvegarde une liste de dictionnaires dans un fichier JSON"""
        path = self._base_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    def save_members(self, members: List[Dict[str, Any]]) -> None:
        """Sauvegarde les membres"""
        self._save_array("members.json", members)
    
    def save_events(self, events: List[Dict[str, Any]]) -> None:
        """Sauvegarde les événements"""
        self._save_array("events.json", events)
    
    def save_subscriptions(self, subscriptions: List[Dict[str, Any]]) -> None:
        """Sauvegarde les abonnements"""
        self._save_array("subscriptions.json", subscriptions)
    
    def save_donations(self, donations: List[Dict[str, Any]]) -> None:
        """Sauvegarde les dons"""
        self._save_array("donations.json", donations)