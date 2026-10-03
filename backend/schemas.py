from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator

class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)

    @field_validator("username", mode="before")
    @classmethod
    def strip_username(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return str(value).lower()

class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=100)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return str(value).lower()

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    bio: str
    is_online: bool
    last_seen: datetime
    model_config = {"from_attributes": True}

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class MessageIn(BaseModel):
    body: str = Field(min_length=1, max_length=5000)

    @field_validator("body", mode="before")
    @classmethod
    def strip_body(cls, value):
        return value.strip() if isinstance(value, str) else value

class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    body: str
    is_read: bool
    created_at: datetime
    model_config = {"from_attributes": True}

class ReportIn(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)

    @field_validator("reason", mode="before")
    @classmethod
    def strip_reason(cls, value):
        return value.strip() if isinstance(value, str) else value
