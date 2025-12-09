from __future__ import annotations
from dataclasses import dataclass
from datetime import date

from models.subscription import Subscription


@dataclass
class AnnualSubscription(Subscription):
    year: int = date.today().year
    discount_rate: float = 0.10

    def total_amount(self) -> float:
        base = self.amount * 12
        return base * (1 - self.discount_rate)
