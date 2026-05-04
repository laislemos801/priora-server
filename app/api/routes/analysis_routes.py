from fastapi import APIRouter
from app.schemas.analysis_schema import GenerateAnalysisRequest
from app.services.analysis_service import (
    generate_analysis_service,
    get_case_uncertainty_evolution_service,
    get_suspect_history_service
)

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/generate")
def generate_analysis(data: GenerateAnalysisRequest):
    return generate_analysis_service(data.dict())


@router.get("/case/{caso_id}/uncertainty")
def get_case_uncertainty_evolution(caso_id: str):
    return get_case_uncertainty_evolution_service(caso_id)


@router.get("/suspect/{suspeito_id}/history")
def get_suspect_history(suspeito_id: str):
    return get_suspect_history_service(suspeito_id)