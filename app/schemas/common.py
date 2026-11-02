from __future__ import annotations

import re
from collections.abc import Mapping

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator

REQUIRED = "This field is required."
_REQUIRED_TYPES = {
    "missing",
    "string_type",
    "string_too_short",
    "date_type",
    "int_type",
    "none_required",
    "literal_error_missing",
}


class FormModel(BaseModel):
    """Base for HTML form payloads: strips strings and turns blank strings into None."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def _blank_to_none(cls, data):
        if isinstance(data, dict):
            return {k: (None if isinstance(v, str) and v.strip() == "" else v) for k, v in data.items()}
        return data


def _message(err: dict) -> str:
    etype = err["type"]
    if etype in _REQUIRED_TYPES:
        return REQUIRED
    if etype == "value_error":
        ctx = err.get("ctx", {}).get("error")
        return str(ctx) if ctx else "Enter a valid value."
    if etype.startswith("date"):
        return "Enter a valid date (YYYY-MM-DD)."
    if etype == "string_too_long":
        return f"Must be at most {err['ctx']['max_length']} characters."
    if etype == "literal_error":
        return "Select a valid option."
    if etype.startswith("int"):
        return "Select a valid option."
    return "Enter a valid value."


def validate_form[T: FormModel](model: type[T], data: Mapping) -> tuple[T | None, dict[str, str]]:
    try:
        return model.model_validate(dict(data)), {}
    except ValidationError as exc:
        errors: dict[str, str] = {}
        for err in exc.errors():
            key = str(err["loc"][0]) if err["loc"] else "_"
            errors.setdefault(key, _message(err))
        return None, errors


def digits_only(value: str, label: str, min_len: int = 1, max_len: int = 20) -> str:
    if not re.fullmatch(r"\d+", value):
        raise ValueError(f"{label} must contain digits only.")
    if not min_len <= len(value) <= max_len:
        raise ValueError(f"{label} must be {min_len}-{max_len} digits.")
    return value


def clean_email(value: str) -> str:
    try:
        return validate_email(value, check_deliverability=False).normalized.lower()
    except EmailNotValidError as exc:
        raise ValueError("Enter a valid email address.") from exc
