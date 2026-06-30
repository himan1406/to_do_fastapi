import re
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, Literal
from datetime import datetime


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, strip_whitespace=True)
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = "medium"
    due_date: Optional[datetime] = None

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None

class TodoReplace(BaseModel):
    title: str = Field(min_length=1, strip_whitespace=True)
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = "medium"
    completed: bool = False
    due_date: Optional[datetime] = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    completed: bool
    created_at: datetime
    due_date: Optional[datetime] = None
    user_id: int

    model_config = {"from_attributes": True}


# ── User schemas ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str = Field(min_length=1, strip_whitespace=True)
    email: EmailStr
    phone: str = Field(min_length=1, strip_whitespace=True)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r'^\+\d{1,3}\d{10}$', v):
            raise ValueError(
                "Phone must include country code followed by exactly 10 digits (e.g., +919876543210)"
            )
        return v

    password: str = Field(min_length=6)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    created_at: datetime

    model_config = {"from_attributes": True}

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r'^\+\d{1,3}\d{10}$', v):
            raise ValueError(
                "Phone must include country code followed by exactly 10 digits (e.g., +919876543210)"
            )
        return v

    new_password: str = Field(min_length=6)