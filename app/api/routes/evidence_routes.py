from fastapi import APIRouter
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
def create_evidence(data: CreateEvidenceRequest):
    return create_evidence_service(data.dict())


@router.get("/case/{caso_id}")
def list_evidences(caso_id: str):
    return list_evidences_service(caso_id)


@router.delete("/")
def delete_evidences(data: DeleteEvidencesRequest):
    return delete_evidences_service(data.ids)


@router.patch("/{evidence_id}")
def update_evidence(evidence_id: str, data: UpdateEvidenceRequest):
    payload = {k: v for k, v in data.dict().items() if v is not None}
    return update_evidence_service(evidence_id, payload)

@router.get("/{evidence_id}")
def get_evidence(evidence_id: str):
    return get_evidence_service(evidence_id)