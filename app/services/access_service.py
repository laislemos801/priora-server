from app.database.neo4j import get_session
from app.repositories.access_repository import (
    invite_user_to_case,
    accept_invite,
    list_case_users
)


def invite_user_service(email, caso_id, papel):
    with get_session() as tx:
        return invite_user_to_case(tx, email, caso_id, papel)


def accept_invite_service(user_id, caso_id):
    with get_session() as tx:
        return accept_invite(tx, user_id, caso_id)


def list_case_users_service(caso_id):
    with get_session() as tx:
        return list_case_users(tx, caso_id)