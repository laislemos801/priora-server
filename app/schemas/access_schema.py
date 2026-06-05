from enum import Enum
from pydantic import BaseModel, EmailStr


class PapelAcesso(str, Enum):
    Editor = "Editor"
    Leitor = "Leitor"


class InviteUserRequest(BaseModel):
    email: EmailStr
    casoId: str
    papel: PapelAcesso
    userId: str


class AcceptInviteRequest(BaseModel):
    userId: str
    casoId: str


class UpdateAccessRequest(BaseModel):
    papel: PapelAcesso