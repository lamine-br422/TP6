"""
Système de validation de champs avec définition obligatoire/facultative.
"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from .validation_strategy import ValidationStrategy, ValidationResult
from .validators import RequiredFieldValidator


@dataclass
class FieldDefinition:
    """Définition d'un champ avec ses validateurs."""
    name: str
    label: str
    is_required: bool = True
    validators: List[ValidationStrategy] = field(default_factory=list)
    
    def get_label_with_asterisk(self) -> str:
        """Retourne le label avec * si le champ est obligatoire."""
        if self.is_required:
            return f"{self.label} *"
        return self.label


class FieldValidator:
    """Valide un ensemble de champs selon leurs définitions."""
    
    def __init__(self, field_definitions: List[FieldDefinition]):
        self.field_definitions = {fd.name: fd for fd in field_definitions}
    
    def validate_field(self, field_name: str, value: str) -> ValidationResult:
        """Valide un champ spécifique."""
        if field_name not in self.field_definitions:
            return ValidationResult(is_valid=True)  # Champ non défini = valide par défaut
        
        field_def = self.field_definitions[field_name]
        
        # Si le champ est obligatoire et vide, utiliser RequiredFieldValidator
        if field_def.is_required:
            required_validator = RequiredFieldValidator()
            result = required_validator.validate(value)
            if not result:
                return result
        
        # Appliquer tous les validateurs spécifiques
        for validator in field_def.validators:
            result = validator.validate(value)
            if not result:
                return result
        
        return ValidationResult(is_valid=True)
    
    def validate_all(self, field_values: Dict[str, str]) -> Dict[str, ValidationResult]:
        """Valide tous les champs et retourne un dictionnaire de résultats."""
        results = {}
        for field_name, value in field_values.items():
            results[field_name] = self.validate_field(field_name, value)
        return results
    
    def is_all_valid(self, field_values: Dict[str, str]) -> bool:
        """Vérifie si tous les champs sont valides."""
        results = self.validate_all(field_values)
        return all(result.is_valid for result in results.values())
    
    def get_errors(self, field_values: Dict[str, str]) -> Dict[str, str]:
        """Retourne un dictionnaire des erreurs par champ."""
        results = self.validate_all(field_values)
        errors = {}
        for field_name, result in results.items():
            if not result.is_valid:
                errors[field_name] = result.error_message or "Erreur de validation"
        return errors

