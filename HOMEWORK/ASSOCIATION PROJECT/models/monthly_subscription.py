from __future__ import annotations
from dataclasses import dataclass
from datetime import date

from models.subscription import Subscription


@dataclass
class MonthlySubscription(Subscription):
    months: int = 1

    def total_amount(self) -> float:
        return self.amount * self.months
