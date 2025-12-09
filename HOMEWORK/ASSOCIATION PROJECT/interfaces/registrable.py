from abc import ABC, abstractmethod

class Registrable(ABC):
    """Interface pour tout ce qui peut enregistrer un membre (ex: EventManager)."""

    @abstractmethod
    def register_member(self, member) -> None:
        """Enregistrer un membre."""
        pass
