"""
Strategy Pattern - MemberSorter (Context)

Cette classe utilise le pattern Strategy pour trier les membres.
Elle maintient une référence à une stratégie de tri et délègue le tri à cette stratégie.

Problème résolu :
- Permet de changer dynamiquement la stratégie de tri sans modifier le code client.
- Le client peut choisir parmi différentes stratégies (par nom, date, groupe, statut).

Bénéfices :
- Flexibilité : changement de stratégie à l'exécution
- Extensibilité : facile d'ajouter de nouvelles stratégies
- Code client simplifié : une seule interface pour toutes les stratégies
"""

from __future__ import annotations
from typing import Any, Dict, List
from .sort_strategy import SortStrategy
from .sort_by_name_strategy import SortByNameStrategy


class MemberSorter:
    """
    Context qui utilise une stratégie de tri pour trier les membres.
    
    Cette classe encapsule la logique de tri et permet de changer
    dynamiquement la stratégie utilisée.
    """
    
    def __init__(self, strategy: SortStrategy | None = None) -> None:
        """
        Initialise le trieur avec une stratégie.
        
        Args:
            strategy: Stratégie de tri à utiliser (par défaut : tri par nom)
        """
        self._strategy = strategy or SortByNameStrategy()
    
    def set_strategy(self, strategy: SortStrategy) -> None:
        """
        Change la stratégie de tri.
        
        Args:
            strategy: Nouvelle stratégie de tri à utiliser
        """
        self._strategy = strategy
    
    def get_strategy(self) -> SortStrategy:
        """
        Retourne la stratégie actuelle.
        
        Returns:
            La stratégie de tri actuelle
        """
        return self._strategy
    
    def sort(self, members: List[Dict[str, Any]], reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Trie les membres en utilisant la stratégie actuelle.
        
        Args:
            members: Liste des membres à trier
            reverse: Si True, trie en ordre décroissant
            
        Returns:
            Liste des membres triés selon la stratégie
        """
        return self._strategy.sort(members, reverse)
    
    def get_strategy_name(self) -> str:
        """
        Retourne le nom de la stratégie actuelle.
        
        Returns:
            Nom de la stratégie
        """
        return self._strategy.get_name()

