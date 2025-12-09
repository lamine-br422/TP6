"""Stratégie de tri par date d'inscription"""

from __future__ import annotations
from typing import Any, Dict, List
from datetime import datetime
from .sort_strategy import SortStrategy


class SortByDateStrategy(SortStrategy):
    """
    Stratégie de tri des membres par date d'inscription.
    """
    
    def sort(self, members: List[Dict[str, Any]], reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Trie les membres par date d'inscription.
        
        Args:
            members: Liste des membres à trier
            reverse: Si True, trie du plus récent au plus ancien (décroissant), 
                     sinon du plus ancien au plus récent (croissant)
            
        Returns:
            Liste des membres triés par date d'inscription
        """
        def get_date(member: Dict[str, Any]) -> datetime:
            """Extrait et parse la date d'inscription"""
            join_date = member.get("join_date", "")
            if isinstance(join_date, str):
                try:
                    # Essayer différents formats de date
                    if "T" in join_date:
                        # Format ISO avec heure
                        return datetime.fromisoformat(join_date.split("T")[0])
                    else:
                        # Format YYYY-MM-DD
                        return datetime.strptime(join_date, "%Y-%m-%d")
                except (ValueError, TypeError):
                    # Si le parsing échoue, mettre à la fin (date minimale)
                    return datetime.min
            elif hasattr(join_date, "isoformat"):
                # Objet date
                date_str = join_date.isoformat()
                if "T" in date_str:
                    return datetime.fromisoformat(date_str.split("T")[0])
                return datetime.fromisoformat(date_str)
            return datetime.min
        
        return sorted(
            members,
            key=get_date,
            reverse=reverse
        )
    
    def get_name(self) -> str:
        """Retourne le nom de la stratégie"""
        return "Par date d'inscription"

