"""
Strategy Pattern - Interface SortStrategy

Cette interface définit le contrat pour toutes les stratégies de tri des membres.

Problème résolu :
- Avant : Le tri était codé en dur dans les méthodes, rendant difficile l'ajout
  de nouveaux critères de tri sans modifier le code existant.
- Après : Chaque stratégie de tri est encapsulée dans sa propre classe, permettant
  de changer dynamiquement la stratégie de tri sans modifier le code client.

Bénéfices :
- Extensibilité : facile d'ajouter de nouvelles stratégies de tri
- Flexibilité : changement de stratégie à l'exécution
- Séparation des responsabilités : chaque stratégie gère son propre algorithme
- Testabilité : chaque stratégie peut être testée indépendamment
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class SortStrategy(ABC):
    """
    Interface abstraite pour les stratégies de tri des membres.
    
    Chaque stratégie concrète doit implémenter la méthode sort()
    qui définit comment trier une liste de membres.
    """
    
    @abstractmethod
    def sort(self, members: List[Dict[str, Any]], reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Trie une liste de membres selon la stratégie.
        
        Args:
            members: Liste des membres à trier
            reverse: Si True, trie en ordre décroissant
            
        Returns:
            Liste des membres triés
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Retourne le nom de la stratégie.
        
        Returns:
            Nom de la stratégie
        """
        pass

