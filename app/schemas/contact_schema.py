from pydantic import BaseModel, Field
from typing import Optional


class CreateContactRequest(BaseModel):
    casoId: str
    nome: str = Field(..., example="Eric Mason")
    cargo: str = Field(..., example="Delegado")
    celular: Optional[str] = Field(None, example="(19) 99032-7454")


class UpdateContactRequest(BaseModel):
    nome: Optional[str] = None
    cargo: Optional[str] = None
    celular: Optional[str] = None