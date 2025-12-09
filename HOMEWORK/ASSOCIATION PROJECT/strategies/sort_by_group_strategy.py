"""Stratégie de tri par groupe"""

from __future__ import annotations
from typing import Any, Dict, List
from .sort_strategy import SortStrategy


class SortByGroupStrategy(SortStrategy):
    """
    Stratégie de tri des étudiants par groupe.
    Les membres sans groupe sont placés à la fin.
    """
    
    def sort(self, members: List[Dict[str, Any]], reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Trie les membres par groupe.
        
        Args:
            members: Liste des membres à trier
            reverse: Si True, trie du groupe le plus élevé au plus bas
            
        Returns:
            Liste des membres triés par groupe
        """
        def get_group(member: Dict[str, Any]) -> int:
            """Extrait le numéro de groupe, retourne -1 si absent"""
            groupe = member.get("groupe")
            if groupe is None:
                return -1
            try:
                return int(groupe)
            except (ValueError, TypeError):
                return -1
        
        sorted_members = sorted(
            members,
            key=get_group,
            reverse=reverse
        )
        
        # Placer les membres sans groupe à la fin
        with_group = [m for m in sorted_members if get_group(m) != -1]
        without_group = [m for m in sorted_members if get_group(m) == -1]
        
        return with_group + without_group
    
    def get_name(self) -> str:
        """Retourne le nom de la stratégie"""
        return "Par groupe"

