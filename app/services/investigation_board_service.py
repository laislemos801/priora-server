import json

from app.database.neo4j import get_session
from app.repositories.investigation_board_repository import (
    get_case_exists,
    get_board,
    save_board,
)


def get_board_service(caso_id: str):
    """
    Retorna:
      - None                         -> caso não existe (rota deve responder 404)
      - {"nodes": [], "edges": []}   -> caso existe, mas quadro ainda não foi salvo
      - {"nodes": [...], "edges": [...]} -> quadro salvo
    """
    with get_session() as tx:
        if not get_case_exists(tx, caso_id):
            return None

        raw = get_board(tx, caso_id)

    if not raw:
        return {"nodes": [], "edges": []}

    try:
        return json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        # dado corrompido/manual no banco — não derruba a rota, volta vazio
        return {"nodes": [], "edges": []}


def save_board_service(caso_id: str, nodes: list, edges: list):
    with get_session() as tx:
        return save_board(tx, caso_id, nodes, edges)
