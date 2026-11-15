from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import Field, field_validator

from app.schemas.common import FormModel, clean_email, digits_only


class AssetForm(FormModel):
    asset_tag_id: str = Field(max_length=60)
    asset_type: str = Field(default="laptop", max_length=40)
    description: str = Field(max_length=300)
    status: Literal["available", "under_maintenance"] = "available"
    brand: str = Field(max_length=100)
    model: str = Field(max_length=100)
    serial_number: str = Field(max_length=100)
    os: str | None = Field(default=None, max_length=100)
    os_version: str | None = Field(default=None, max_length=100)
    memory: str | None = Field(default=None, max_length=60)
    hard_disk: str | None = Field(default=None, max_length=60)
    processor: str | None = Field(default=None, max_length=120)
    department: str | None = Field(default=None, max_length=120)
    # Not every device on the books has paperwork; both are optional.
    purchase_date: date | None = None
    warranty_expiry: date | None = None
    last_password: str | None = Field(default=None, max_length=200)

    @field_validator("warranty_expiry")
    @classmethod
    def _warranty_after_purchase(cls, v, info):
        purchase = info.data.get("purchase_date")
        if v and purchase and v < purchase:
            raise ValueError("Warranty expiry cannot be before the purchase date.")
        return v


class PersonForm(FormModel):
    name: str = Field(max_length=120)
    employee_code: str = Field(max_length=40)
    mobile: str
    email: str
    address: str = Field(max_length=500)
    pincode: str
    location_id: int

    @field_validator("mobile")
    @classmethod
    def _mobile(cls, v):
        return digits_only(v, "Mobile number", 10, 10)

    @field_validator("pincode")
    @classmethod
    def _pincode(cls, v):
        return digits_only(v, "Pincode", 4, 10)

    @field_validator("email")
    @classmethod
    def _email(cls, v):
        return clean_email(v)


class LocationForm(FormModel):
    name: str = Field(max_length=120)
    floor: str = Field(max_length=40)
    building_name: str = Field(max_length=160)
    area: str = Field(max_length=160)
    pincode: str
    district: str = Field(max_length=120)
    state: str = Field(max_length=120)

    @field_validator("pincode")
    @classmethod
    def _pincode(cls, v):
        return digits_only(v, "Pincode", 6, 6)


class CheckoutForm(FormModel):
    employee_id: int
    location_id: int
    department: str = Field(max_length=120)
    checkout_date: date | None = None
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("checkout_date")
    @classmethod
    def _not_future(cls, v):
        if v and v > date.today():
            raise ValueError("Check-out date cannot be in the future.")
        return v


class CheckinForm(FormModel):
    notes: str | None = Field(default=None, max_length=1000)


class LoginForm(FormModel):
    email: str
    password: str


class PasswordResetForm(FormModel):
    password: str = Field(min_length=8, max_length=128)


class ProfileForm(FormModel):
    name: str = Field(max_length=120)
    email: str

    @field_validator("email")
    @classmethod
    def _email(cls, v):
        return clean_email(v)


class ChangePasswordForm(FormModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def _match(cls, v, info):
        if v != info.data.get("new_password"):
            raise ValueError("Passwords do not match.")
        return v
