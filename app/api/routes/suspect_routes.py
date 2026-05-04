from fastapi import APIRouter
from app.schemas.suspect_schema import CreateSuspectRequest
from app.services.suspect_service import (
    create_suspect_service,
    list_suspects_service,
    update_suspect_ranking_service
)

router = APIRouter(prefix="/suspects", tags=["Suspects"])


@router.post("/", status_code=201)
def create_suspect(data: CreateSuspectRequest):
    return create_suspect_service(data.dict())


@router.get("/case/{caso_id}")
def list_suspects(caso_id: str):
    return list_suspects_service(caso_id)


@router.patch("/case/{caso_id}/ranking")
def update_ranking(caso_id: str):
    return update_suspect_ranking_service(caso_id)