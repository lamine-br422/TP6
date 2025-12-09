from dataclasses import dataclass
from datetime import date
from .member import Member

@dataclass
class Student(Member):
    student_id: int = 0
    groupe: int = 0
    subscription_status: str = "Pending"

    def display(self) -> str:
        return f"#{self.student_id} {self.full_name} [{self.subscription_status}]"

    def check_subscription(self) -> str:
        return self.subscription_status
