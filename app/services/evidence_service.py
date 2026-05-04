from app.database.neo4j import get_session
from app.repositories.evidence_repository import (
    create_evidence,
    list_evidences_by_case
)


def create_evidence_service(data):
    with get_session() as session:
        return create_evidence(session, data)


def list_evidences_service(caso_id):
    with get_session() as session:
        return list_evidences_by_case(session, caso_id)