import re
from typing import Any

from pydantic import BaseModel, EmailStr, validator, Field, field_validator
from pydantic_core.core_schema import ValidationInfo


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        examples=[
            "amp@indomobilhino.co.id",
            "sales.amp@indomobilhino.co.id",
            "angga.ardhianto1@hino.co.id",
            "sulfitriani.sofyan1@hino.co.id",
            "alexander1@hino.co.id",
            "irwan.supriyono1@hino.co.id",
            "takashi.muto1@hino.co.id",
        ],
    )
    password: str


class RegisterRequest(BaseModel):
    name: str = Field(..., examples=["Ari Davis"])
    email: EmailStr = Field(..., examples=["ari@example.com"])
    password: str = Field(..., examples=["AriDavis123!"])
    confirmation_password: str = Field(..., examples=["AriDavis123!"])

    @field_validator("name")
    def validate_name(cls, value: str) -> str:
        if len(value) > 50:
            raise ValueError("name exceeds maximum length of 50 characters")
        return value

    @field_validator("confirmation_password")
    def validate_confiration_password(cls, value: str, values: ValidationInfo) -> str:
        if "password" in values.data and value != values.data["password"]:
            raise ValueError("confirmation_password isn't the same with password")
        return value

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if not re.match(
            r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", value
        ):
            raise ValueError("Invalid password")
        return value
