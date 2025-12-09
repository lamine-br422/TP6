from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

@dataclass
class Member:
    full_name: str
    email: str
    phone: str
    address: str
    join_date: date
    skills: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)

    def display(self) -> str:
        return f"{self.full_name} | {self.email} | {self.phone} | {self.address} | {self.join_date.isoformat()}"

    def add_skill(self, skill: str) -> None:
        s = skill.strip()
        if s and s not in self.skills:
            self.skills.append(s)

    def add_interest(self, interest: str) -> None:
        i = interest.strip()
        if i and i not in self.interests:
            self.interests.append(i)

    def update_contact(self, email: Optional[str] = None, phone: Optional[str] = None, address: Optional[str] = None) -> None:
        if email is not None:
            self.email = email
        if phone is not None:
            self.phone = phone
        if address is not None:
            self.address = address
