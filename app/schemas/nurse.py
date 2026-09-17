from pydantic import BaseModel, Field


class NurseUpdate(BaseModel):
    """Champs modifiables du profil infirmier (CDC F1.5 / WBS 1.3).

    Tous optionnels : seuls les champs fournis sont mis à jour.
    """

    last_name: str | None = Field(default=None, min_length=1, max_length=255)
    first_name: str | None = Field(default=None, min_length=1, max_length=255)
    replacement_nurse: bool | None = None
    company_name: str | None = Field(default=None, max_length=255)
    siret: int | None = None
    note: str | None = None
