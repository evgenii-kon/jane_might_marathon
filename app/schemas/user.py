from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3)
    email: EmailStr
    telegram: str | None = Field(None, max_length=32)
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    telegram: str | None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = Field(None, min_length=3)
    telegram: str | None = Field(None, max_length=32)
    password: str | None = Field(None, min_length=6)

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
