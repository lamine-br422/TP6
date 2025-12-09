"""
Module de validation utilisant le pattern Strategy.
"""
from .validation_strategy import ValidationStrategy, ValidationResult
from .validators import (
    EmailValidator,
    PhoneValidator,
    RequiredFieldValidator,
    DateValidator,
    NumberValidator,
    IntegerValidator,
    IdsListValidator,
)
from .field_validator import FieldValidator, FieldDefinition

__all__ = [
    "ValidationStrategy",
    "ValidationResult",
    "EmailValidator",
    "PhoneValidator",
    "RequiredFieldValidator",
    "DateValidator",
    "NumberValidator",
    "IntegerValidator",
    "IdsListValidator",
    "FieldValidator",
    "FieldDefinition",
]

