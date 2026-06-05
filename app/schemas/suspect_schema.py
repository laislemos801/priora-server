from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class TendenciaSuspeito(str, Enum):
    Alta = "Alta"
    Baixa = "Baixa"
    Estavel = "Estável"


class RespostaHistorico(str, Enum):
    Sim = "Sim"
    NaoSei = "Não sei"
    Nao = "Não"


class CreateSuspectRequest(BaseModel):
    casoId: str

    nome: str = Field(..., example="Elvin Bond")
    idade: int = Field(..., ge=0, example=32)
    fotoUrl: Optional[str] = None

    comportamento: float = Field(..., ge=0, le=100, example=70)
    agressividade: float = Field(..., ge=0, le=100, example=55)
    proximidade: float = Field(..., ge=0, le=100, example=80)
    conexoesSociais: float = Field(..., ge=0, le=100, example=60)
    nivelConfissao: float = Field(..., ge=0, le=100, example=20)

    crimeSimilarAntes: RespostaHistorico
    histDescumprimento: RespostaHistorico

class UpdateSuspectRequest(BaseModel):
    nome: str
    idade: Optional[int] = None
    fotoUrl: Optional[str] = None

    comportamento: float
    agressividade: float
    proximidade: float
    conexoesSociais: float
    nivelConfissao: float

    crimeSimilarAntes: str
    histDescumprimento: str