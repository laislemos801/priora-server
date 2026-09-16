from fastapi import APIRouter, Depends
from app.core.security import get_current_user_id
from app.schemas.evidence_schema import (
    CreateEvidenceRequest,
    DeleteEvidencesRequest,
    UpdateEvidenceRequest,
)
from app.services.evidence_service import (
    create_evidence_service,
    list_evidences_service,
    delete_evidences_service,
    update_evidence_service,
    get_evidence_service,
)
router = APIRouter(prefix="/evidences", tags=["Evidences"])


@router.post("/", status_code=201)
def create_evidence(data: CreateEvidenceRequest, current_user_id: str = Depends(get_current_user_id)):
    return create_evidence_service(current_user_id, data.dict())


@router.get("/case/{caso_id}")
def list_evidences(caso_id: str, current_user_id: str = Depends(get_current_user_id)):
    return list_evidences_service(current_user_id, caso_id)


@router.delete("/")
def delete_evidences(data: DeleteEvidencesRequest, current_user_id: str = Depends(get_current_user_id)):
    return delete_evidences_service(current_user_id, data.ids)


@router.patch("/{evidence_id}")
def update_evidence(evidence_id: str, data: UpdateEvidenceRequest, current_user_id: str = Depends(get_current_user_id)):
    payload = {k: v for k, v in data.dict().items() if v is not None}
    return update_evidence_service(current_user_id, evidence_id, payload)

@router.get("/{evidence_id}")
def get_evidence(evidence_id: str, current_user_id: str = Depends(get_current_user_id)):
    return get_evidence_service(current_user_id, evidence_id)