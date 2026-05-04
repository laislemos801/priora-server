from fastapi import APIRouter
from app.services.access_service import (
    invite_user_service,
    accept_invite_service,
    list_case_users_service
)

from app.schemas.access_schema import (
    InviteUserRequest,
    AcceptInviteRequest
)

router = APIRouter(prefix="/access", tags=["Access"])


@router.post("/invite", status_code=201)
def invite_user(data: InviteUserRequest):
    return invite_user_service(
        data.email,
        data.casoId,
        data.papel
    )


@router.post("/accept")
def accept_invite(data: AcceptInviteRequest):
    return accept_invite_service(
        data.userId,
        data.casoId
    )


@router.get("/case/{caso_id}")
def list_users(caso_id: str):
    return list_case_users_service(caso_id)