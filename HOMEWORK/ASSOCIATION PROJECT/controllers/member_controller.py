from __future__ import annotations
from typing import List, Dict, Any
from interfaces.storage_interface import StorageInterface
from observers.data_observer import Subject
from factories.member_factory import MemberFactory
from strategies.member_sorter import MemberSorter
from strategies.sort_strategy import SortStrategy
from strategies.sort_by_name_strategy import SortByNameStrategy
from strategies.sort_by_date_strategy import SortByDateStrategy
from strategies.sort_by_group_strategy import SortByGroupStrategy
from strategies.sort_by_status_strategy import SortByStatusStrategy


class MemberController(Subject):
    """Controller pour gérer les opérations sur les membres (étudiants, professeurs)"""
    
    def __init__(self, storage: StorageInterface) -> None:
        super().__init__()
        self._storage = storage
        self._sorter = MemberSorter()  # Utilise le pattern Strategy pour le tri
        
    def get_all_members(self) -> List[Dict[str, Any]]:
        """Récupère tous les membres depuis le storage"""
        return self._storage.load_members()
    
    def get_students(self) -> List[Dict[str, Any]]:
        """Récupère uniquement les étudiants"""
        members = self.get_all_members()
        return [m for m in members if "student_id" in m]
    
    def get_teachers(self) -> List[Dict[str, Any]]:
        """Récupère uniquement les professeurs"""
        members = self.get_all_members()
        return [m for m in members if "teacher_id" in m]
    
    def get_teachers_sorted(self, sort_by: str = "name", reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Récupère les professeurs triés selon une stratégie.
        
        Utilise le pattern Strategy pour permettre différents types de tri.
        Note: Les stratégies "group" et "status" ne sont pas applicables aux teachers.
        
        Args:
            sort_by: Critère de tri ("name", "date")
            reverse: Si True, trie en ordre décroissant
            
        Returns:
            Liste des professeurs triés
        """
        teachers = self.get_teachers()
        # Pour les teachers, seules les stratégies "name" et "date" sont valides
        if sort_by not in ["name", "date"]:
            sort_by = "name"
        
        strategy = self._get_sort_strategy(sort_by)
        self._sorter.set_strategy(strategy)
        return self._sorter.sort(teachers, reverse)
    
    def get_member_by_id(self, member_id: int, member_type: str = "student") -> Dict[str, Any] | None:
        """Récupère un membre par son ID"""
        members = self.get_all_members()
        id_key = f"{member_type}_id" if member_type in ["student", "teacher"] else "id"
        
        for member in members:
            if member.get(id_key) == member_id:
                return member
        return None
    
    def add_member(self, member: Dict[str, Any]) -> None:
        """Ajoute un nouveau membre"""
        members = self.get_all_members()
        members.append(member)
        self._storage.save_members(members)
        member_type = "student" if "student_id" in member else "teacher"
        self.notify(f"member_added_{member_type}", member)
    
    def delete_member(self, member_id: int, member_type: str = "student") -> bool:
        """Supprime un membre par son ID"""
        members = self.get_all_members()
        id_key = f"{member_type}_id" if member_type in ["student", "teacher"] else "id"
        
        original_count = len(members)
        members = [m for m in members if m.get(id_key) != member_id]
        
        if len(members) < original_count:
            self._storage.save_members(members)
            self.notify(f"member_deleted_{member_type}", {"id": member_id})
            return True
        return False
    
    def get_next_student_id(self) -> int:
        """Retourne le prochain ID disponible pour un étudiant"""
        students = self.get_students()
        if not students:
            return 1
        ids = [s.get("student_id", 0) for s in students if s.get("student_id") is not None]
        return max(ids, default=0) + 1
    
    def get_next_teacher_id(self) -> int:
        """Retourne le prochain ID disponible pour un enseignant"""
        teachers = self.get_teachers()
        if not teachers:
            return 1
        ids = [t.get("teacher_id", 0) for t in teachers if t.get("teacher_id") is not None]
        return max(ids, default=0) + 1

    def update_student_group(self, student_id: int, group: int | None) -> bool:
        """Met à jour le champ 'groupe' d'un étudiant et sauvegarde.

        Retourne True si l'étudiant a été trouvé et mis à jour.
        """
        members = self.get_all_members()
        updated = False
        for member in members:
            if member.get("student_id") == student_id:
                member["groupe"] = group
                updated = True
                break
        if updated:
            self._storage.save_members(members)
            self.notify("member_updated", {"student_id": student_id, "group": group})
        return updated

    def create_student(self, **kwargs) -> Dict[str, Any]:
        """Crée un étudiant en utilisant la Factory"""
        return MemberFactory.create_student(**kwargs)

    def create_teacher(self, **kwargs) -> Dict[str, Any]:
        """Crée un professeur en utilisant la Factory"""
        return MemberFactory.create_teacher(**kwargs)
    
    # ==================== MÉTHODES UTILISANT LE PATTERN STRATEGY ====================
    
    def get_students_sorted(self, sort_by: str = "name", reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Récupère les étudiants triés selon une stratégie.
        
        Utilise le pattern Strategy pour permettre différents types de tri.
        
        Args:
            sort_by: Critère de tri ("name", "date", "group", "status")
            reverse: Si True, trie en ordre décroissant
            
        Returns:
            Liste des étudiants triés
        """
        students = self.get_students()
        strategy = self._get_sort_strategy(sort_by)
        self._sorter.set_strategy(strategy)
        return self._sorter.sort(students, reverse)
    
    def get_all_members_sorted(self, sort_by: str = "name", reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Récupère tous les membres triés selon une stratégie.
        
        Utilise le pattern Strategy pour permettre différents types de tri.
        
        Args:
            sort_by: Critère de tri ("name", "date", "group", "status")
            reverse: Si True, trie en ordre décroissant
            
        Returns:
            Liste des membres triés
        """
        members = self.get_all_members()
        strategy = self._get_sort_strategy(sort_by)
        self._sorter.set_strategy(strategy)
        return self._sorter.sort(members, reverse)
    
    def _get_sort_strategy(self, sort_by: str) -> SortStrategy:
        """
        Retourne la stratégie de tri correspondante.
        
        Args:
            sort_by: Nom de la stratégie ("name", "date", "group", "status")
            
        Returns:
            Instance de SortStrategy
        """
        strategies = {
            "name": SortByNameStrategy(),
            "date": SortByDateStrategy(),
            "group": SortByGroupStrategy(),
            "status": SortByStatusStrategy(),
        }
        return strategies.get(sort_by.lower(), SortByNameStrategy())
    
    def set_sort_strategy(self, strategy: SortStrategy) -> None:
        """
        Définit la stratégie de tri à utiliser.
        
        Args:
            strategy: Instance de SortStrategy à utiliser
        """
        self._sorter.set_strategy(strategy)

