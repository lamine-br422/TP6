"""
Pattern Strategy pour la validation des champs.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationResult:
    """Résultat d'une validation."""
    is_valid: bool
    error_message: Optional[str] = None

    def __bool__(self) -> bool:
        return self.is_valid


class ValidationStrategy(ABC):
    """Interface Strategy pour les validateurs."""
    
    @abstractmethod
    def validate(self, value: str) -> ValidationResult:
        """
        Valide une valeur.
        
        Args:
            value: La valeur à valider
            
        Returns:
            ValidationResult avec is_valid=True si valide, False sinon avec un message d'erreur
        """
        pass

