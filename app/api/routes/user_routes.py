from fastapi import APIRouter
from app.services.user_service import (
    create_user_service,
    login_user_service,
    recovery_token_service,
    reset_password_service
)

from app.schemas.user_schema import (
    CreateUserRequest,
    LoginRequest,
    RecoverRequest,
    ResetPasswordRequest
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=201)
def create_user(data: CreateUserRequest):
    return create_user_service(
        data.email,
        data.primeiroNome,
        data.sobrenome,
        data.senha
    )


@router.post("/login")
def login(data: LoginRequest):
    return login_user_service(
        data.email,
        data.senha
    )


@router.post("/recover")
async def recover(data: RecoverRequest):
    return await recovery_token_service(data.email)


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest):
    return reset_password_service(
        data.token,
        data.novaSenha
    )