from app.database.neo4j import get_session
from app.repositories.contact_repository import (
    create_contact,
    list_contacts_by_case,
    update_contact,
    delete_contact
)


def create_contact_service(data):
    with get_session() as tx:
        return create_contact(tx, data)


def list_contacts_service(caso_id):
    with get_session() as tx:
        return list_contacts_by_case(tx, caso_id)


def update_contact_service(contato_id, data):
    with get_session() as tx:
        return update_contact(tx, contato_id, data)


def delete_contact_service(caso_id, contato_id):
    with get_session() as tx:
        return delete_contact(tx, caso_id, contato_id)