"""Stratégie de tri par ID"""

from __future__ import annotations
from typing import Any, Dict, List
from .sort_strategy import SortStrategy


class SortByIdStrategy(SortStrategy):
    """
    Stratégie de tri des membres par ID (numérique).
    """
    
    def sort(self, members: List[Dict[str, Any]], reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Trie les membres par ID.
        
        Args:
            members: Liste des membres à trier
            reverse: Si True, trie de haut en bas (ID décroissant), sinon de bas en haut (ID croissant)
            
        Returns:
            Liste des membres triés par ID
        """
        def get_id(member: Dict[str, Any]) -> int:
            """Extrait l'ID du membre (student_id ou teacher_id)"""
            student_id = member.get("student_id")
            teacher_id = member.get("teacher_id")
            if student_id is not None:
                try:
                    return int(student_id)
                except (ValueError, TypeError):
                    return 0
            elif teacher_id is not None:
                try:
                    return int(teacher_id)
                except (ValueError, TypeError):
                    return 0
            return 0
        
        return sorted(
            members,
            key=get_id,
            reverse=reverse
        )
    
    def get_name(self) -> str:
        """Retourne le nom de la stratégie"""
        return "Par ID"

