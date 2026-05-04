from app.database.neo4j import get_session
from app.repositories.suspect_repository import (
    create_suspect,
    list_suspects_by_case,
    update_suspect_ranking
)


def create_suspect_service(data):
    with get_session() as tx:
        return create_suspect(tx, data)


def list_suspects_service(caso_id):
    with get_session() as tx:
        return list_suspects_by_case(tx, caso_id)


def update_suspect_ranking_service(caso_id):
    with get_session() as tx:
        return update_suspect_ranking(tx, caso_id)