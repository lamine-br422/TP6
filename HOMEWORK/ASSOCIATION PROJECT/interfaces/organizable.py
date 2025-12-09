from abc import ABC, abstractmethod

class Organizable(ABC):
    @abstractmethod
    def schedule(self) -> str: ...
