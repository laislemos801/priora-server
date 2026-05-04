from pydantic import BaseModel
from typing import Optional


class CreateCaseRequest(BaseModel):
    userId: str
    nome: str
    descricao: str
    status: str
    prioridade: str

    enderecoLogradouro: Optional[str] = None
    enderecoNumero: Optional[str] = None
    enderecoBairro: Optional[str] = None
    enderecoCidade: Optional[str] = None
    enderecoEstado: Optional[str] = None

    dataOcorrencia: str

class UpdateUncertaintyRequest(BaseModel):
    incerteza: float