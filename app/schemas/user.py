from pydantic import BaseModel, Field, EmailStr, field_validator
from pydantic_settings import SettingsConfigDict


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3)
    email: EmailStr
    telegram: str | None = Field(None, max_length=32)
    password: str = Field(..., min_length=8)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    telegram: str | None

    model_config = SettingsConfigDict(from_attributes = True)



class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = Field(None, min_length=3)
    telegram: str | None = Field(None, max_length=32)
    password: str | None = Field(None, min_length=8)

    model_config = SettingsConfigDict(from_attributes = True)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return v.lower().strip()



class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
