"""
Facade Pattern - AssociationFacade

Cette classe fournit une interface simplifiée et unifiée pour accéder
aux différents services de l'association (membres, événements, finances).

Problème résolu :
- Avant : Le code devait accéder à plusieurs contrôleurs séparément (MemberController,
  EventController, FinanceController), ce qui créait de la complexité et du couplage.
- Après : Une seule interface Facade permet d'accéder à toutes les fonctionnalités
  principales de manière simplifiée et cohérente.

Bénéfices :
- Simplifie l'utilisation pour les clients (UI, API)
- Réduit le couplage entre les composants
- Centralise les opérations courantes
- Facilite la maintenance et les tests
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from controllers.association_controller import AssociationController
from interfaces.storage_interface import StorageInterface


class AssociationFacade:
    """
    Facade qui simplifie l'accès aux services de l'association.
    
    Cette classe encapsule les interactions avec les différents contrôleurs
    et fournit des méthodes de haut niveau pour les opérations courantes.
    """
    
    def __init__(self, storage: StorageInterface) -> None:
        """
        Initialise la Facade avec le storage.
        
        Args:
            storage: Interface de stockage des données
        """
        self._controller = AssociationController(storage)
    
    # ==================== MÉTHODES DASHBOARD ET STATISTIQUES ====================
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Récupère toutes les données nécessaires pour le tableau de bord.
        
        Returns:
            Dictionnaire contenant membres, événements, abonnements et dons
        """
        return self._controller.get_dashboard_data()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Récupère les statistiques globales de l'association.
        
        Returns:
            Dictionnaire avec les statistiques (nombre de membres, total finances, etc.)
        """
        members = self._controller.get_member_controller().get_all_members()
        students = self._controller.get_member_controller().get_students()
        teachers = self._controller.get_member_controller().get_teachers()
        events = self._controller.get_event_controller().get_all_events()
        
        finance_controller = self._controller.get_finance_controller()
        total_donations = finance_controller.calculate_total_donations()
        total_subscriptions = finance_controller.calculate_total_subscriptions()
        paid_subscriptions = finance_controller.calculate_total_subscriptions("paid")
        
        return {
            "total_members": len(members),
            "total_students": len(students),
            "total_teachers": len(teachers),
            "total_events": len(events),
            "total_donations": total_donations,
            "total_subscriptions": total_subscriptions,
            "paid_subscriptions": paid_subscriptions,
            "pending_subscriptions": total_subscriptions - paid_subscriptions,
        }
    
    # ==================== MÉTHODES MEMBRES ====================
    
    def get_all_members(self, sort_by: Optional[str] = None, reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Récupère tous les membres (étudiants et professeurs).
        
        Args:
            sort_by: Critère de tri ("name", "date", "group", "status") ou None pour pas de tri
            reverse: Si True, trie en ordre décroissant
            
        Returns:
            Liste des membres, optionnellement triés
        """
        if sort_by:
            return self._controller.get_member_controller().get_all_members_sorted(sort_by, reverse)
        return self._controller.get_member_controller().get_all_members()
    
    def get_students(self, sort_by: Optional[str] = None, reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Récupère uniquement les étudiants.
        
        Args:
            sort_by: Critère de tri ("name", "date", "group", "status") ou None pour pas de tri
            reverse: Si True, trie en ordre décroissant
            
        Returns:
            Liste des étudiants, optionnellement triés
        """
        if sort_by:
            return self._controller.get_member_controller().get_students_sorted(sort_by, reverse)
        return self._controller.get_member_controller().get_students()
    
    def get_teachers(self, sort_by: Optional[str] = None, reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Récupère uniquement les professeurs.
        
        Args:
            sort_by: Critère de tri ("name", "date") ou None pour pas de tri
            reverse: Si True, trie en ordre décroissant
            
        Returns:
            Liste des professeurs, optionnellement triés
        """
        if sort_by:
            return self._controller.get_member_controller().get_teachers_sorted(sort_by, reverse)
        return self._controller.get_member_controller().get_teachers()
    
    def get_member_by_id(self, member_id: int, member_type: str = "student") -> Optional[Dict[str, Any]]:
        """Récupère un membre par son ID"""
        return self._controller.get_member_controller().get_member_by_id(member_id, member_type)
    
    def add_member(self, member: Dict[str, Any]) -> None:
        """Ajoute un nouveau membre"""
        self._controller.get_member_controller().add_member(member)
    
    def delete_member(self, member_id: int, member_type: str = "student") -> bool:
        """Supprime un membre par son ID"""
        return self._controller.get_member_controller().delete_member(member_id, member_type)
    
    def create_student(self, **kwargs) -> Dict[str, Any]:
        """Crée un étudiant en utilisant la Factory"""
        return self._controller.get_member_controller().create_student(**kwargs)
    
    def create_teacher(self, **kwargs) -> Dict[str, Any]:
        """Crée un professeur en utilisant la Factory"""
        return self._controller.get_member_controller().create_teacher(**kwargs)
    
    # ==================== MÉTHODES ÉVÉNEMENTS ====================
    
    def get_all_events(self) -> List[Dict[str, Any]]:
        """Récupère tous les événements"""
        return self._controller.get_event_controller().get_all_events()
    
    def get_event_by_name(self, event_name: str) -> Optional[Dict[str, Any]]:
        """Récupère un événement par son nom"""
        return self._controller.get_event_controller().get_event_by_name(event_name)
    
    def get_events_by_date(self, date: str) -> List[Dict[str, Any]]:
        """Récupère les événements pour une date donnée"""
        return self._controller.get_event_controller().get_events_by_date(date)
    
    def add_event(self, event: Dict[str, Any]) -> None:
        """Ajoute un nouvel événement"""
        self._controller.get_event_controller().add_event(event)
    
    def delete_event(self, event_name: str) -> bool:
        """Supprime un événement par son nom"""
        return self._controller.get_event_controller().delete_event(event_name)
    
    # ==================== MÉTHODES FINANCES ====================
    
    def get_all_subscriptions(self) -> List[Dict[str, Any]]:
        """Récupère tous les abonnements"""
        return self._controller.get_finance_controller().get_all_subscriptions()
    
    def get_all_donations(self) -> List[Dict[str, Any]]:
        """Récupère tous les dons"""
        return self._controller.get_finance_controller().get_all_donations()
    
    def get_subscriptions_by_student(self, student_id: int) -> List[Dict[str, Any]]:
        """Récupère les abonnements d'un étudiant"""
        return self._controller.get_finance_controller().get_subscriptions_by_student(student_id)
    
    def get_subscriptions_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Récupère les abonnements par statut"""
        return self._controller.get_finance_controller().get_subscriptions_by_status(status)
    
    def calculate_total_donations(self) -> float:
        """Calcule le total des dons"""
        return self._controller.get_finance_controller().calculate_total_donations()
    
    def calculate_total_subscriptions(self, status: Optional[str] = None) -> float:
        """Calcule le total des abonnements, optionnellement filtré par statut"""
        return self._controller.get_finance_controller().calculate_total_subscriptions(status)
    
    def add_subscription(self, subscription: Dict[str, Any]) -> None:
        """Ajoute un nouvel abonnement"""
        self._controller.get_finance_controller().add_subscription(subscription)
    
    def delete_subscription(self, student_id: int, date: str) -> bool:
        """Supprime un abonnement"""
        return self._controller.get_finance_controller().delete_subscription(student_id, date)
    
    def add_donation(self, donation: Dict[str, Any]) -> None:
        """Ajoute un nouveau don"""
        self._controller.get_finance_controller().add_donation(donation)
    
    def delete_donation(self, donor_name: str, date: str, amount: float) -> bool:
        """Supprime un don"""
        return self._controller.get_finance_controller().delete_donation(donor_name, date, amount)
    
    # ==================== MÉTHODES OBSERVER ====================
    
    def attach_observer(self, observer) -> None:
        """
        Attache un observer pour être notifié des changements.
        
        Args:
            observer: Instance d'Observer à attacher
        """
        self._controller.attach_observer(observer)
    
    # ==================== MÉTHODES UTILITAIRES ====================
    
    def get_controller(self) -> AssociationController:
        """
        Retourne le contrôleur principal (pour accès avancé si nécessaire).
        
        Returns:
            Le contrôleur AssociationController
        """
        return self._controller

