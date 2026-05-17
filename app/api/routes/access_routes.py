from fastapi import APIRouter
from app.services.access_service import (
    invite_user_service,
    accept_invite_service,
    list_case_users_service,
    update_case_access_service,
    delete_case_access_service
)

from app.schemas.access_schema import (
    InviteUserRequest,
    AcceptInviteRequest,
    UpdateAccessRequest
)

router = APIRouter(prefix="/access", tags=["Access"])


@router.post("/invite", status_code=201)
def invite_user(data: InviteUserRequest):
    return invite_user_service(
        data.email,
        data.casoId,
        data.papel,
        data.userId
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


@router.patch("/case/{caso_id}/user/{user_id}")
def update_access(caso_id: str, user_id: str, data: UpdateAccessRequest):
    return update_case_access_service(
        caso_id,
        user_id,
        data.papel
    )


@router.delete("/case/{caso_id}/user/{user_id}")
def delete_access(caso_id: str, user_id: str):
    return delete_case_access_service(caso_id, user_id)