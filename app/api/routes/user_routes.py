from fastapi import APIRouter
from app.services.user_service import (
    create_user_service,
    login_user_service,
    recovery_token_service,
    reset_password_service
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/")
def create_user(data: dict):
    return create_user_service(
        data["email"],
        data["primeiroNome"],
        data["sobrenome"],
        data["senha"]
    )


@router.post("/login")
def login(data: dict):
    return login_user_service(data["email"])


@router.post("/recover")
def recover(data: dict):
    return recovery_token_service(data["email"], data["token"])


@router.post("/reset-password")
def reset_password(data: dict):
    return reset_password_service(
        data["token"],
        data["novaSenha"]
    )