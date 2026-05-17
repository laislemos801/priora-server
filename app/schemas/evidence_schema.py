from pydantic import BaseModel, Field
from enum import Enum


class TipoEvidencia(str, Enum):
    Digital = "Digital"
    DNA = "DNA"
    Depoimento = "Depoimento"
    Documental = "Documental"
    Fisica = "Física"
    Audiovisual = "Audiovisual"
    Biologica = "Biológica"


class StatusEvidencia(str, Enum):
    Coletada = "Coletada"
    EmAnalise = "Em análise"
    Custodiada = "Custodiada"
    Descartada = "Descartada"
    EnviadaPericia = "Enviada a perícia"


class CreateEvidenceRequest(BaseModel):
    casoId: str
    suspeitoIds: list[str] 

    nome: str = Field(..., example="Digital no local")
    tipo: TipoEvidencia
    status: StatusEvidencia = StatusEvidencia.Coletada 
    descricao: str | None = None

    dataColeta: str = Field(..., example="2025-04-24")

    peso: float = Field(..., ge=0.0, le=1.0, example=0.5)
    pesoVinculo: float = Field(..., ge=0.0, le=1.0, example=0.75)


class DeleteEvidencesRequest(BaseModel):
    ids: list[str]