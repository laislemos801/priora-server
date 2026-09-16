from fastapi import HTTPException, status

from app.database.neo4j import get_session
from app.core.authorization import require_case_role, READ_ROLES, WRITE_ROLES, OWNER_ROLES
from app.repositories.access_repository import (
    invite_user_to_case,
    accept_invite,
    list_case_users,
    update_case_access,
    delete_case_access
)


def invite_user_service(current_user_id: str, email, caso_id, papel):
    with get_session() as tx:
        require_case_role(tx, current_user_id, caso_id, WRITE_ROLES)
        # quem convida é sempre o usuário autenticado, nunca um userId
        # arbitrário enviado no corpo da requisição.
        return invite_user_to_case(tx, email, caso_id, papel, current_user_id)


def accept_invite_service(current_user_id: str, user_id, caso_id):
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode aceitar convites destinados à sua própria conta",
        )
    with get_session() as tx:
        return accept_invite(tx, user_id, caso_id)


def list_case_users_service(current_user_id: str, caso_id):
    with get_session() as tx:
        require_case_role(tx, current_user_id, caso_id, READ_ROLES)
        return list_case_users(tx, caso_id)


def update_case_access_service(current_user_id: str, caso_id, user_id, papel):
    with get_session() as tx:
        # somente o responsável pelo caso pode alterar papéis de colaboradores
        require_case_role(tx, current_user_id, caso_id, OWNER_ROLES)
        return update_case_access(tx, caso_id, user_id, papel)


def delete_case_access_service(current_user_id: str, caso_id, user_id):
    with get_session() as tx:
        # somente o responsável pelo caso pode remover o acesso de colaboradores
        require_case_role(tx, current_user_id, caso_id, OWNER_ROLES)
        return delete_case_access(tx, caso_id, user_id)