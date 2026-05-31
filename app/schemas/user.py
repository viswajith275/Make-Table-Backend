import re

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator
from typing import Optional, Self
from datetime import datetime


# Base user model
class UsersResponse(BaseModel):
    username: str
    email: str
    created_at: datetime
    disabled: bool

    model_config = ConfigDict(from_attributes=True)


# user create model
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_validation(cls, u: str) -> str:
        if " " in u:
            raise ValueError("Username cannot contain spaces")
        if len(u) < 3 or len(u) > 20:
            raise ValueError("Length of username should be between 3 and 20")
        if re.search(r'[!#$%^&*(),.?":{}|<>]', u):
            raise ValueError(
                "Username should not contain any special characters other than @"
            )
        return u

    @field_validator("password")
    @classmethod
    def password_constraints(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(v) > 20:
            raise ValueError("Password must be at most 20 characters long")
        if " " in v:
            raise ValueError("Password must not contain a space")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_validation(cls, u: str) -> str:
        if " " in u:
            raise ValueError("Username cannot contain spaces")
        if len(u) < 3 or len(u) > 20:
            raise ValueError("Length of username should be between 3 and 20")
        if re.search(r'[!#$%^&*(),.?":{}|<>]', u):
            raise ValueError(
                "Username should not contain any special characters other than @"
            )
        return u


class PasswordUpdationRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str

    @field_validator("new_password")
    @classmethod
    def password_constraints(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(v) > 20:
            raise ValueError("Password must be at most 20 characters long")
        if " " in v:
            raise ValueError("Password must not contain a space")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")
        return v

    @model_validator(mode="after")
    def validation(self) -> Self:
        if self.new_password != self.confirm_new_password:
            raise ValueError("Passwords doesnt match!")
        return self
