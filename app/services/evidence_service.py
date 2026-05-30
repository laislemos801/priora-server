from app.database.neo4j import get_session
from app.repositories.evidence_repository import (
    create_evidence,
    list_evidences_by_case,
    delete_evidences,
    update_evidence,
    get_evidence_by_id
)


def create_evidence_service(data):
    with get_session() as session:
        return create_evidence(session, data)


def list_evidences_service(caso_id):
    with get_session() as session:
        return list_evidences_by_case(session, caso_id)

def delete_evidences_service(ids: list[str]):
    with get_session() as session:
        return delete_evidences(session, ids)

def update_evidence_service(evidence_id: str, data: dict):
    with get_session() as session:
        return update_evidence(session, evidence_id, data)

def get_evidence_service(evidence_id: str):
    with get_session() as session:
        return get_evidence_by_id(session, evidence_id)
