"""Stratégie de tri par nom (alphabétique)"""

from __future__ import annotations
from typing import Any, Dict, List
from .sort_strategy import SortStrategy


class SortByNameStrategy(SortStrategy):
    """
    Stratégie de tri des membres par nom complet (ordre alphabétique).
    """
    
    def sort(self, members: List[Dict[str, Any]], reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Trie les membres par nom complet.
        
        Args:
            members: Liste des membres à trier
            reverse: Si True, trie de Z à A, sinon de A à Z
            
        Returns:
            Liste des membres triés par nom
        """
        return sorted(
            members,
            key=lambda m: m.get("full_name", "").lower(),
            reverse=reverse
        )
    
    def get_name(self) -> str:
        """Retourne le nom de la stratégie"""
        return "Par nom"

