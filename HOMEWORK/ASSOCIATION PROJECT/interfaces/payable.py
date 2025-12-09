from abc import ABC, abstractmethod

class Payable(ABC):
    @abstractmethod
    def process_payment(self) -> float: ...
