from __future__ import annotations
from typing import List, Dict, Any
from interfaces.storage_interface import StorageInterface
from managers.finance_manager import FinanceManager
from observers.data_observer import Subject


class FinanceController(Subject):
    """Controller pour gérer les opérations financières (abonnements, dons)"""
    
    def __init__(self, storage: StorageInterface) -> None:
        super().__init__()
        self._storage = storage
        self._finance_manager = FinanceManager()
        
    def get_all_subscriptions(self) -> List[Dict[str, Any]]:
        """Récupère tous les abonnements"""
        return self._storage.load_subscriptions()
    
    def get_all_donations(self) -> List[Dict[str, Any]]:
        """Récupère tous les dons"""
        return self._storage.load_donations()
    
    def get_subscriptions_by_student(self, student_id: int) -> List[Dict[str, Any]]:
        """Récupère les abonnements d'un étudiant"""
        subscriptions = self.get_all_subscriptions()
        return [s for s in subscriptions if s.get("student_id") == student_id]
    
    def get_subscriptions_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Récupère les abonnements par statut (paid, unpaid, pending)"""
        subscriptions = self.get_all_subscriptions()
        return [s for s in subscriptions if s.get("status", "").lower() == status.lower()]
    
    def calculate_total_donations(self) -> float:
        """Calcule le total des dons"""
        donations = self.get_all_donations()
        total = 0.0
        for donation in donations:
            total += float(donation.get("amount", 0.0))
        return total
    
    def calculate_total_subscriptions(self, status: str | None = None) -> float:
        """Calcule le total des abonnements, optionnellement filtré par statut"""
        subscriptions = self.get_all_subscriptions()
        if status:
            subscriptions = [s for s in subscriptions if s.get("status", "").lower() == status.lower()]
        
        total = 0.0
        for subscription in subscriptions:
            total += float(subscription.get("amount", 0.0))
        return total
    
    def add_subscription(self, subscription: Dict[str, Any]) -> None:
        """Ajoute un nouvel abonnement"""
        subscriptions = self.get_all_subscriptions()
        subscriptions.append(subscription)
        self._storage.save_subscriptions(subscriptions)
        self.notify("subscription_added", subscription)
    
    def delete_subscription(self, student_id: int, date: str) -> bool:
        """Supprime un abonnement par student_id et date"""
        subscriptions = self.get_all_subscriptions()
        original_count = len(subscriptions)
        subscriptions = [s for s in subscriptions 
                        if not (s.get("student_id") == student_id and s.get("date") == date)]
        
        if len(subscriptions) < original_count:
            self._storage.save_subscriptions(subscriptions)
            self.notify("subscription_deleted", {"student_id": student_id, "date": date})
            return True
        return False
    
    def add_donation(self, donation: Dict[str, Any]) -> None:
        """Ajoute un nouveau don"""
        donations = self.get_all_donations()
        donations.append(donation)
        self._storage.save_donations(donations)
        self.notify("donation_added", donation)
    
    def delete_donation(self, donor_name: str, date: str, amount: float) -> bool:
        """Supprime un don par nom du donateur, date et montant"""
        donations = self.get_all_donations()
        original_count = len(donations)
        donations = [d for d in donations 
                    if not (d.get("donor_name") == donor_name 
                           and d.get("date") == date 
                           and float(d.get("amount", 0)) == amount)]
        
        if len(donations) < original_count:
            self._storage.save_donations(donations)
            self.notify("donation_deleted", {"donor_name": donor_name, "date": date, "amount": amount})
            return True
        return False

