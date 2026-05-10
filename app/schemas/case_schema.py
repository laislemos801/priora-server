from pydantic import BaseModel
from typing import Optional


class CreateCaseRequest(BaseModel):
    userId: str
    nome: str
    descricao: str
    status: str
    prioridade: str
    enderecoCep: str | None = None        # ← novo
    enderecoLogradouro: str | None = None
    enderecoNumero: str | None = None
    enderecoBairro: str | None = None
    enderecoCidade: str | None = None
    enderecoEstado: str | None = None
    dataOcorrencia: str | None = None

class UpdateUncertaintyRequest(BaseModel):
    incerteza: float