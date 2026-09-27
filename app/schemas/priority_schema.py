from enum import Enum
from pydantic import BaseModel


class AcaoStatus(str, Enum):
    Sugerida = "Sugerida"
    EmProgresso = "Em progresso"
    Concluida = "Concluída"
    Descartada = "Descartada"


class UpdateActionStatusRequest(BaseModel):
    status: AcaoStatus
