from app.database.neo4j import get_session
from app.repositories.case_repository import (
    create_case,
    get_cases_by_user,
    update_case_uncertainty,
    get_case_by_id_tx,
    update_case,
    delete_case
)

def create_case_service(user_id, data):
    with get_session() as tx:
        return create_case(tx, user_id, data)


def get_cases_service(user_id):
    with get_session() as tx:
        return get_cases_by_user(tx, user_id)


def get_case_service(caso_id: str):
    with get_session() as tx:
        return get_case_by_id_tx(tx, caso_id)


def update_uncertainty_service(caso_id, nova_incerteza):
    with get_session() as tx:
        return update_case_uncertainty(tx, caso_id, nova_incerteza)


def update_case_service(caso_id, data):
    with get_session() as tx:
        return update_case(tx, caso_id, data)
    
    
def delete_case_service(caso_id):
    with get_session() as tx:
        return delete_case(tx, caso_id)