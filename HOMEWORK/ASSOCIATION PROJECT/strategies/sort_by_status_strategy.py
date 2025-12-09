"""Stratégie de tri par statut d'abonnement"""

from __future__ import annotations
from typing import Any, Dict, List
from .sort_strategy import SortStrategy


class SortByStatusStrategy(SortStrategy):
    """
    Stratégie de tri des étudiants par statut d'abonnement.
    Ordre : Paid -> Pending -> Unpaid
    """
    
    def sort(self, members: List[Dict[str, Any]], reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Trie les membres par statut d'abonnement.
        
        Args:
            members: Liste des membres à trier
            reverse: Si True, inverse l'ordre de tri
            
        Returns:
            Liste des membres triés par statut d'abonnement
        """
        def get_status_priority(member: Dict[str, Any]) -> int:
            """Retourne une priorité numérique pour le statut"""
            status = str(member.get("subscription_status", "")).lower()
            if status == "paid":
                return 1
            elif status == "pending":
                return 2
            elif status == "unpaid":
                return 3
            else:
                return 4  # Statut inconnu à la fin
        
        sorted_members = sorted(
            members,
            key=lambda m: (get_status_priority(m), m.get("full_name", "").lower()),
            reverse=reverse
        )
        
        # Si reverse est True, on inverse l'ordre des priorités
        if reverse:
            # Réorganiser pour avoir Unpaid -> Pending -> Paid
            unpaid = [m for m in sorted_members if get_status_priority(m) == 3]
            pending = [m for m in sorted_members if get_status_priority(m) == 2]
            paid = [m for m in sorted_members if get_status_priority(m) == 1]
            unknown = [m for m in sorted_members if get_status_priority(m) == 4]
            return unpaid + pending + paid + unknown
        
        return sorted_members
    
    def get_name(self) -> str:
        """Retourne le nom de la stratégie"""
        return "Par statut d'abonnement"

