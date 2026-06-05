from pydantic import BaseModel, Field


class GenerateAnalysisRequest(BaseModel):
    casoId: str
    userId: str