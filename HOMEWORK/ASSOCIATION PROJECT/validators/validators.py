"""
Implémentations concrètes des validateurs utilisant le pattern Strategy.
"""
import re
from datetime import datetime
from typing import Optional
from .validation_strategy import ValidationStrategy, ValidationResult


class RequiredFieldValidator(ValidationStrategy):
    """Valide qu'un champ est rempli."""
    
    def __init__(self, field_name: str = None):
        """
        Args:
            field_name: Nom du champ pour personnaliser le message d'erreur
        """
        self.field_name = field_name
    
    def validate(self, value: str) -> ValidationResult:
        if not value or not value.strip():
            if self.field_name:
                # Messages personnalisés selon le champ
                messages = {
                    "full_name": "Veuillez saisir votre nom complet",
                    "donor_name": "Veuillez saisir le nom du donateur",
                    "address": "Veuillez saisir l'adresse",
                    "event_name": "Veuillez saisir le nom de l'événement",
                    "description": "Veuillez saisir la description",
                "source": "Veuillez saisir la source",
                "subscription_status": "Veuillez saisir le statut d'abonnement (Paid/Pending/Unpaid)",
                "status": "Veuillez saisir le statut (paid/unpaid/pending)",
                "kind": "Veuillez saisir le type d'abonnement (monthly/annual/base)",
            }
                error_msg = messages.get(self.field_name, f"Veuillez saisir {self.field_name}")
            else:
                error_msg = "Ce champ est obligatoire"
            
            return ValidationResult(
                is_valid=False,
                error_message=error_msg
            )
        return ValidationResult(is_valid=True)


class EmailValidator(ValidationStrategy):
    """Valide qu'un email se termine par @ quelquechose.com ou .fr"""
    
    def validate(self, value: str) -> ValidationResult:
        if not value or not value.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Veuillez saisir votre email"
            )
        
        email = value.strip()
        # Vérifier le format général d'email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return ValidationResult(
                is_valid=False,
                error_message="Format d'email invalide. L'email doit être au format : nom@domaine.com ou nom@domaine.fr"
            )
        
        # Vérifier que ça se termine par .com ou .fr
        if not (email.endswith('.com') or email.endswith('.fr')):
            return ValidationResult(
                is_valid=False,
                error_message="L'email doit se terminer par .com ou .fr (exemple : nom@exemple.com ou nom@exemple.fr)"
            )
        
        return ValidationResult(is_valid=True)


class PhoneValidator(ValidationStrategy):
    """Valide qu'un numéro de téléphone commence par 05, 06 ou 07 et a 10 chiffres."""
    
    def validate(self, value: str) -> ValidationResult:
        if not value or not value.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Veuillez saisir votre numéro de téléphone"
            )
        
        # Enlever les espaces et caractères spéciaux
        phone = re.sub(r'[\s\-\.\(\)]', '', value.strip())
        
        # Vérifier que c'est composé uniquement de chiffres
        if not phone.isdigit():
            return ValidationResult(
                is_valid=False,
                error_message="Le numéro de téléphone doit contenir uniquement des chiffres (exemple : 0612345678)"
            )
        
        # Vérifier qu'il commence par 05, 06 ou 07
        if not phone.startswith(('05', '06', '07')):
            return ValidationResult(
                is_valid=False,
                error_message="Le numéro doit commencer par 05, 06 ou 07 (exemple : 0612345678)"
            )
        
        # Vérifier qu'il a exactement 10 chiffres
        if len(phone) != 10:
            return ValidationResult(
                is_valid=False,
                error_message=f"Le numéro doit contenir exactement 10 chiffres (vous avez saisi {len(phone)} chiffres). Exemple : 0612345678"
            )
        
        return ValidationResult(is_valid=True)


class DateValidator(ValidationStrategy):
    """Valide qu'une date est au format YYYY-MM-DD."""
    
    def __init__(self, field_name: str = None):
        """
        Args:
            field_name: Nom du champ pour personnaliser le message d'erreur
        """
        self.field_name = field_name
    
    def validate(self, value: str) -> ValidationResult:
        if not value or not value.strip():
            messages = {
                "join_date": "Veuillez saisir la date d'inscription",
                "event_date": "Veuillez saisir la date de l'événement",
                "date": "Veuillez saisir la date",
            }
            error_msg = messages.get(self.field_name, "Veuillez saisir la date")
            return ValidationResult(
                is_valid=False,
                error_message=error_msg
            )
        
        date_str = value.strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return ValidationResult(is_valid=True)
        except ValueError:
            return ValidationResult(
                is_valid=False,
                error_message=f"Format de date invalide. Veuillez utiliser le format YYYY-MM-DD (exemple : 2024-12-25)"
            )


class NumberValidator(ValidationStrategy):
    """Valide qu'une valeur est un nombre."""
    
    def __init__(self, min_value: Optional[float] = None, max_value: Optional[float] = None, field_name: str = None):
        self.min_value = min_value
        self.max_value = max_value
        self.field_name = field_name
    
    def validate(self, value: str) -> ValidationResult:
        if not value or not value.strip():
            messages = {
                "amount": "Veuillez saisir le montant",
            }
            error_msg = messages.get(self.field_name, "Ce champ est obligatoire")
            return ValidationResult(
                is_valid=False,
                error_message=error_msg
            )
        
        try:
            num = float(value.strip())
            
            if self.min_value is not None and num < self.min_value:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Le montant doit être supérieur ou égal à {self.min_value}"
                )
            
            if self.max_value is not None and num > self.max_value:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Le montant doit être inférieur ou égal à {self.max_value}"
                )
            
            return ValidationResult(is_valid=True)
        except ValueError:
            return ValidationResult(
                is_valid=False,
                error_message="Veuillez saisir un nombre valide (exemple : 100.50)"
            )


class IntegerValidator(ValidationStrategy):
    """Valide qu'une valeur est un entier."""
    
    def __init__(self, min_value: Optional[int] = None, max_value: Optional[int] = None, field_name: str = None):
        self.min_value = min_value
        self.max_value = max_value
        self.field_name = field_name
    
    def validate(self, value: str) -> ValidationResult:
        if not value or not value.strip():
            messages = {
                "student_id": "Veuillez saisir l'ID de l'étudiant",
            }
            error_msg = messages.get(self.field_name, "Ce champ est obligatoire")
            return ValidationResult(
                is_valid=False,
                error_message=error_msg
            )
        
        try:
            num = int(value.strip())
            
            if self.min_value is not None and num < self.min_value:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"L'ID doit être supérieur ou égal à {self.min_value}"
                )
            
            if self.max_value is not None and num > self.max_value:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"L'ID doit être inférieur ou égal à {self.max_value}"
                )
            
            return ValidationResult(is_valid=True)
        except ValueError:
            return ValidationResult(
                is_valid=False,
                error_message="Veuillez saisir un nombre entier valide (exemple : 1, 2, 3...)"
            )


class IdsListValidator(ValidationStrategy):
    """Valide qu'une liste d'IDs séparés par des virgules est valide."""
    
    def __init__(self, field_name: str = None):
        self.field_name = field_name
    
    def validate(self, value: str) -> ValidationResult:
        if not value or not value.strip():
            messages = {
                "organizer_ids": "Veuillez saisir au moins un ID d'organisateur (exemple : 1, 2, 3)",
                "participant_ids": "Veuillez saisir au moins un ID de participant (exemple : 1, 2, 3)",
            }
            error_msg = messages.get(self.field_name, "Ce champ est obligatoire")
            return ValidationResult(
                is_valid=False,
                error_message=error_msg
            )
        
        # Séparer par virgule et nettoyer
        ids_str = [x.strip() for x in value.split(",") if x.strip()]
        
        if not ids_str:
            messages = {
                "organizer_ids": "Veuillez saisir au moins un ID d'organisateur (exemple : 1, 2, 3)",
                "participant_ids": "Veuillez saisir au moins un ID de participant (exemple : 1, 2, 3)",
            }
            error_msg = messages.get(self.field_name, "Veuillez saisir au moins un ID")
            return ValidationResult(
                is_valid=False,
                error_message=error_msg
            )
        
        # Vérifier que chaque ID est un entier valide
        for id_str in ids_str:
            try:
                id_int = int(id_str)
                if id_int < 1:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Les IDs doivent être des nombres entiers positifs (exemple : 1, 2, 3). '{id_str}' n'est pas valide."
                    )
            except ValueError:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Format invalide. Veuillez saisir des IDs séparés par des virgules (exemple : 1, 2, 3). '{id_str}' n'est pas un nombre valide."
                )
        
        return ValidationResult(is_valid=True)

