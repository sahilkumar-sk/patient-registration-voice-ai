import re
from datetime import date, datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, EmailStr, field_validator


# ---------------------------------------------------------
# Constants
# ---------------------------------------------------------

VALID_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC"
}


# ---------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------

def validate_name(value: str) -> str:
    value = value.strip()

    if not 1 <= len(value) <= 50:
        raise ValueError("Name must be between 1 and 50 characters")

    if not re.fullmatch(r"[A-Za-z'-]+", value):
        raise ValueError(
            "Name may only contain letters, hyphens, and apostrophes"
        )

    return value


def validate_dob(value: date) -> date:
    if value > date.today():
        raise ValueError("Date of birth cannot be in the future")

    return value


def validate_sex_value(value: str) -> str:
    normalized = value.strip().lower()

    mapping = {
        "male": "Male",
        "female": "Female",
        "other": "Other",
        "decline to answer": "Decline to Answer",
        "decline": "Decline to Answer",
    }

    if normalized not in mapping:
        raise ValueError(
            "Sex must be Male, Female, Other, or Decline to Answer"
        )

    return mapping[normalized]


def normalize_phone(value: Optional[str]) -> Optional[str]:
    if value is None or value.strip() == "":
        return None

    digits = re.sub(r"\D", "", value)

    # Accept +1XXXXXXXXXX
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]

    if len(digits) != 10:
        raise ValueError(
            "Phone number must be a valid U.S. 10-digit phone number"
        )

    return digits


def validate_state_code(value: str) -> str:
    value = value.upper().strip()

    if value not in VALID_STATES:
        raise ValueError(
            "State must be a valid 2-letter U.S. abbreviation"
        )

    return value


def validate_zip_code(value: str) -> str:
    value = value.strip()

    if not re.fullmatch(r"\d{5}(-\d{4})?", value):
        raise ValueError(
            "ZIP code must be 5 digits or ZIP+4"
        )

    return value


def validate_city_value(value: str) -> str:
    value = value.strip()

    if not 1 <= len(value) <= 100:
        raise ValueError(
            "City must be between 1 and 100 characters"
        )

    return value


# ---------------------------------------------------------
# Patient schemas
# ---------------------------------------------------------

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    sex: str
    phone_number: str

    email: Optional[EmailStr] = None

    address_line_1: str
    address_line_2: Optional[str] = None

    city: str
    state: str
    zip_code: str

    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None

    preferred_language: str = "English"

    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def name_validator(cls, value: str):
        return validate_name(value)

    @field_validator("date_of_birth")
    @classmethod
    def dob_validator(cls, value: date):
        return validate_dob(value)

    @field_validator("sex")
    @classmethod
    def sex_validator(cls, value: str):
        return validate_sex_value(value)

    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def phone_validator(cls, value):
        return normalize_phone(value)

    @field_validator("city")
    @classmethod
    def city_validator(cls, value: str):
        return validate_city_value(value)

    @field_validator("state")
    @classmethod
    def state_validator(cls, value: str):
        return validate_state_code(value)

    @field_validator("zip_code")
    @classmethod
    def zip_validator(cls, value: str):
        return validate_zip_code(value)


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    date_of_birth: Optional[date] = None
    sex: Optional[str] = None
    phone_number: Optional[str] = None

    email: Optional[EmailStr] = None

    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None

    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None

    preferred_language: Optional[str] = None

    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def name_validator(cls, value):
        if value is None:
            return None

        return validate_name(value)

    @field_validator("date_of_birth")
    @classmethod
    def dob_validator(cls, value):
        if value is None:
            return None

        return validate_dob(value)

    @field_validator("sex")
    @classmethod
    def sex_validator(cls, value):
        if value is None:
            return None

        return validate_sex_value(value)

    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def phone_validator(cls, value):
        return normalize_phone(value)

    @field_validator("city")
    @classmethod
    def city_validator(cls, value):
        if value is None:
            return None

        return validate_city_value(value)

    @field_validator("state")
    @classmethod
    def state_validator(cls, value):
        if value is None:
            return None

        return validate_state_code(value)

    @field_validator("zip_code")
    @classmethod
    def zip_validator(cls, value):
        if value is None:
            return None

        return validate_zip_code(value)


class PatientResponse(PatientBase):
    patient_id: str

    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }


# ---------------------------------------------------------
# API response schemas
# ---------------------------------------------------------

class ErrorDetail(BaseModel):
    message: str


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None


class DeleteResponse(BaseModel):
    patient_id: str
    deleted: bool