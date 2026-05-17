from app.database.neo4j import get_session
from app.repositories.access_repository import (
    invite_user_to_case,
    accept_invite,
    list_case_users,
    update_case_access,
    delete_case_access
)


def invite_user_service(email, caso_id, papel, user_id):
    with get_session() as tx:
        return invite_user_to_case(tx, email, caso_id, papel, user_id)


def accept_invite_service(user_id, caso_id):
    with get_session() as tx:
        return accept_invite(tx, user_id, caso_id)


def list_case_users_service(caso_id):
    with get_session() as tx:
        return list_case_users(tx, caso_id)
    

def update_case_access_service(caso_id, user_id, papel):
    with get_session() as tx:
        return update_case_access(tx, caso_id, user_id, papel)


def delete_case_access_service(caso_id, user_id):
    with get_session() as tx:
        return delete_case_access(tx, caso_id, user_id)