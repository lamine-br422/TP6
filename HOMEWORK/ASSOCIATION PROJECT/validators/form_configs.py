"""
Configurations de validation pour les différents formulaires.
"""
from .field_validator import FieldDefinition
from .validators import (
    EmailValidator,
    PhoneValidator,
    RequiredFieldValidator,
    DateValidator,
    NumberValidator,
    IntegerValidator,
    IdsListValidator,
)


def get_student_field_definitions() -> list[FieldDefinition]:
    """Retourne les définitions de champs pour le formulaire Student."""
    return [
        FieldDefinition(
            name="full_name",
            label="Full Name",
            is_required=True,
            validators=[RequiredFieldValidator(field_name="full_name")],
        ),
        FieldDefinition(
            name="email",
            label="Email",
            is_required=True,
            validators=[EmailValidator()],
        ),
        FieldDefinition(
            name="phone",
            label="Phone",
            is_required=True,
            validators=[PhoneValidator()],
        ),
        FieldDefinition(
            name="address",
            label="Address",
            is_required=True,
            validators=[RequiredFieldValidator(field_name="address")],
        ),
        FieldDefinition(
            name="join_date",
            label="Join Date (YYYY-MM-DD)",
            is_required=True,
            validators=[DateValidator(field_name="join_date")],
        ),
        FieldDefinition(
            name="subscription_status",
            label="Subscription Status (Paid/Pending/Unpaid)",
            is_required=True,
            validators=[RequiredFieldValidator(field_name="subscription_status")],
        ),
        FieldDefinition(
            name="skills",
            label="Skills (comma separated)",
            is_required=False,
            validators=[],
        ),
        FieldDefinition(
            name="interests",
            label="Interests (comma separated)",
            is_required=False,
            validators=[],
        ),
    ]


def get_teacher_field_definitions() -> list[FieldDefinition]:
    """Retourne les définitions de champs pour le formulaire Teacher."""
    return [
        FieldDefinition(
            name="full_name",
            label="Full Name",
            is_required=True,
            validators=[RequiredFieldValidator(field_name="full_name")],
        ),
        FieldDefinition(
            name="email",
            label="Email",
            is_required=True,
            validators=[EmailValidator()],
        ),
        FieldDefinition(
            name="phone",
            label="Phone",
            is_required=True,
            validators=[PhoneValidator()],
        ),
        FieldDefinition(
            name="address",
            label="Address",
            is_required=True,
            validators=[RequiredFieldValidator(field_name="address")],
        ),
        FieldDefinition(
            name="join_date",
            label="Join Date (YYYY-MM-DD)",
            is_required=True,
            validators=[DateValidator(field_name="join_date")],
        ),
        FieldDefinition(
            name="skills",
            label="Skills (comma separated)",
            is_required=False,
            validators=[],
        ),
        FieldDefinition(
            name="interests",
            label="Interests (comma separated)",
            is_required=False,
            validators=[],
        ),
    ]


def get_event_field_definitions() -> list[FieldDefinition]:
    """Retourne les définitions de champs pour le formulaire Event."""
    return [
        FieldDefinition(
            name="event_name",
            label="Event Name",
            is_required=True,
            validators=[RequiredFieldValidator(field_name="event_name")],
        ),
        FieldDefinition(
            name="description",
            label="Description",
            is_required=True,
            validators=[RequiredFieldValidator(field_name="description")],
        ),
        FieldDefinition(
            name="event_date",
            label="Date (YYYY-MM-DD)",
            is_required=True,
            validators=[DateValidator(field_name="event_date")],
        ),
        FieldDefinition(
            name="organizer_ids",
            label="Organizer IDs (comma separated)",
            is_required=True,
            validators=[IdsListValidator(field_name="organizer_ids")],
        ),
        FieldDefinition(
            name="participant_ids",
            label="Participant IDs (comma separated)",
            is_required=True,
            validators=[IdsListValidator(field_name="participant_ids")],
        ),
    ]


def get_donation_field_definitions() -> list[FieldDefinition]:
    """Retourne les définitions de champs pour le formulaire Donation."""
    return [
        FieldDefinition(
            name="donor_name",
            label="Donor Name",
            is_required=True,
            validators=[RequiredFieldValidator(field_name="donor_name")],
        ),
        FieldDefinition(
            name="source",
            label="Source",
            is_required=True,
            validators=[RequiredFieldValidator(field_name="source")],
        ),
        FieldDefinition(
            name="amount",
            label="Amount",
            is_required=True,
            validators=[NumberValidator(min_value=0, field_name="amount")],
        ),
        FieldDefinition(
            name="date",
            label="Date (YYYY-MM-DD)",
            is_required=True,
            validators=[DateValidator(field_name="date")],
        ),
        FieldDefinition(
            name="purpose",
            label="Purpose",
            is_required=False,
            validators=[],
        ),
        FieldDefinition(
            name="note",
            label="Note",
            is_required=False,
            validators=[],
        ),
    ]


def get_subscription_field_definitions() -> list[FieldDefinition]:
    """Retourne les définitions de champs pour le formulaire Subscription."""
    return [
        FieldDefinition(
            name="student_id",
            label="Student ID",
            is_required=True,
            validators=[IntegerValidator(min_value=1, field_name="student_id")],
        ),
        FieldDefinition(
            name="amount",
            label="Amount",
            is_required=True,
            validators=[NumberValidator(min_value=0, field_name="amount")],
        ),
        FieldDefinition(
            name="date",
            label="Date (YYYY-MM-DD)",
            is_required=True,
            validators=[DateValidator(field_name="date")],
        ),
        FieldDefinition(
            name="status",
            label="Status (paid/unpaid/pending)",
            is_required=True,
            validators=[RequiredFieldValidator(field_name="status")],
        ),
        FieldDefinition(
            name="kind",
            label="Kind (monthly/annual/base)",
            is_required=True,
            validators=[RequiredFieldValidator(field_name="kind")],
        ),
    ]

