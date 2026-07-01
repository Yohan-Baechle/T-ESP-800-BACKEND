import uuid

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserStatus


class NurseRegister(BaseModel):
    """Données d'inscription d'un infirmier (CDC F1.1 / US-01)."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    order_number: int
    last_name: str = Field(min_length=1, max_length=255)
    first_name: str = Field(min_length=1, max_length=255)
    replacement_nurse: bool = False
    company_name: str | None = None
    siret: int | None = None


class NursePublic(BaseModel):
    """Représentation publique d'un infirmier (sans données sensibles)."""

    user_id: uuid.UUID
    email: EmailStr
    status: UserStatus
    order_number: int
    last_name: str
    first_name: str
    replacement_nurse: bool

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """Identifiants de connexion (CDC F6.1)."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Jeton d'accès JWT renvoyé après authentification."""

    access_token: str
    token_type: str = "bearer"
