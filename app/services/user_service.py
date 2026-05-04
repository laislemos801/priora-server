from app.database.neo4j import get_session
from app.repositories.user_repository import (
    create_user,
    login_user,
    set_recovery_token,
    reset_password
)
import bcrypt


def create_user_service(email, primeiro_nome, sobrenome, senha):
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

    with get_session() as tx:
        return create_user(tx, email, primeiro_nome, sobrenome, senha_hash)


def login_user_service(email):
    with get_session() as tx:
        return login_user(tx, email)


def recovery_token_service(email, token):
    with get_session() as tx:
        return set_recovery_token(tx, email, token)


def reset_password_service(token, nova_senha):
    nova_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()

    with get_session() as tx:
        return reset_password(tx, token, nova_hash)