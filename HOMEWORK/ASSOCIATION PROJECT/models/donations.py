from dataclasses import dataclass
from datetime import date

@dataclass
class Donation:
    donor_name: str
    amount: float
    date: date
