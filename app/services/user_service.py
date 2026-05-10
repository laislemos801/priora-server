from app.database.neo4j import get_session
from app.utils.jwt import create_access_token
from fastapi import HTTPException
from app.utils.email import send_recovery_email
from app.repositories.user_repository import (
    create_user,
    login_user,
    set_recovery_token,
    reset_password
)
import bcrypt
import secrets



def create_user_service(email, primeiro_nome, sobrenome, senha):
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

    with get_session() as tx:
        return create_user(tx, email, primeiro_nome, sobrenome, senha_hash)


def login_user_service(email, senha):
    with get_session() as tx:
        user = login_user(tx, email)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Email ou senha inválidos"
            )

        senha_correta = bcrypt.checkpw(
            senha.encode(),
            user["senhaHash"].encode()
        )

        if not senha_correta:
            raise HTTPException(
                status_code=401,
                detail="Email ou senha inválidos"
            )

        token = create_access_token({
            "sub": user["id"]
        })

        del user["senhaHash"]

        return {
            "user": user,
            "token": token
        }


async def recovery_token_service(email):
    token = secrets.token_urlsafe(32)

    with get_session() as tx:
        user = set_recovery_token(tx, email, token)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    await send_recovery_email(email, token)

    return {
        "message": "Email enviado"
    }


def reset_password_service(token, nova_senha):
    nova_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()

    with get_session() as tx:
        return reset_password(tx, token, nova_hash)