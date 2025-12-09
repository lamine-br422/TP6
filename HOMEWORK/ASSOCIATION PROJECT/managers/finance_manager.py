from typing import Iterable
from interfaces.payable import Payable

class FinanceManager:
    def total_payments(self, items: Iterable[Payable]) -> float:
        total = 0.0
        for it in items:
            if hasattr(it, "amount"):
                total += it.amount
        return total
