from __future__ import annotations
from typing import Any, Dict
from interfaces.storage_interface import StorageInterface
from controllers.member_controller import MemberController
from controllers.event_controller import EventController
from controllers.finance_controller import FinanceController
from observers.data_observer import Observer


class AssociationController:
    """Contrôleur principal qui coordonne toutes les opérations de l'association"""
    
    def __init__(self, storage: StorageInterface) -> None:
        self._storage = storage
        self._member_controller = MemberController(storage)
        self._event_controller = EventController(storage)
        self._finance_controller = FinanceController(storage)

    def attach_observer(self, observer: Observer) -> None:
        self._member_controller.attach(observer)
        self._event_controller.attach(observer)
        self._finance_controller.attach(observer)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Récupère toutes les données pour le tableau de bord"""
        return {
            "members": self._member_controller.get_all_members(),
            "events": self._event_controller.get_all_events(),
            "subscriptions": self._finance_controller.get_all_subscriptions(),
            "donations": self._finance_controller.get_all_donations(),
        }
    
    def get_member_controller(self) -> MemberController:
        """Retourne le contrôleur des membres"""
        return self._member_controller
    
    def get_event_controller(self) -> EventController:
        """Retourne le contrôleur des événements"""
        return self._event_controller
    
    def get_finance_controller(self) -> FinanceController:
        """Retourne le contrôleur des finances"""
        return self._finance_controller

