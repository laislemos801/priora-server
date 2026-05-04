from fastapi import APIRouter
from app.services.evidence_service import (
    create_evidence_service,
    list_evidences_service
)

from app.schemas.evidence_schema import CreateEvidenceRequest

router = APIRouter(prefix="/evidences", tags=["Evidences"])


@router.post("/", status_code=201)
def create_evidence(data: CreateEvidenceRequest):
    return create_evidence_service(data.dict())


@router.get("/case/{caso_id}")
def list_evidences(caso_id: str):
    return list_evidences_service(caso_id)