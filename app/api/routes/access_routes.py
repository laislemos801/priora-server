from fastapi import APIRouter
from app.services.access_service import (
    invite_user_service,
    accept_invite_service,
    list_case_users_service
)

router = APIRouter(prefix="/access", tags=["Access"])


@router.post("/invite")
def invite_user(data: dict):
    return invite_user_service(
        data["email"],
        data["casoId"],
        data["papel"]
    )


@router.post("/accept")
def accept_invite(data: dict):
    return accept_invite_service(
        data["userId"],
        data["casoId"]
    )


@router.get("/case/{caso_id}")
def list_users(caso_id: str):
    return list_case_users_service(caso_id)