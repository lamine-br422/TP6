from typing import List
from models.member import Member
from interfaces.storage import Storage

class MemberRepository:
    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    def save_all(self, members: List[Member]) -> None:
        data = [m.__dict__ for m in members]
        self._storage.save_members(data)

    def load_all(self) -> List[Member]:
        records = self._storage.load_members()
        return [Member(**r) for r in records]
