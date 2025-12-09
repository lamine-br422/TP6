from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict


class UIInterface(ABC):
    @abstractmethod
    def show_dashboard(self, project: Dict[str, Any]) -> None:
        ...
