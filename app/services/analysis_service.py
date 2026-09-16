from fastapi import HTTPException, status

from app.database.neo4j import get_session
from app.core.authorization import require_case_role, READ_ROLES
from app.repositories.analysis_repository import (
    generate_analysis,
    get_case_uncertainty_evolution,
    get_suspect_history,
    get_suspect_analysis
)
from app.repositories.suspect_repository import get_case_id_for_suspect


def generate_analysis_service(current_user_id: str, data):
    with get_session() as tx:
        require_case_role(tx, current_user_id, data["casoId"], READ_ROLES)
        return generate_analysis(tx, data)


def get_case_uncertainty_evolution_service(current_user_id: str, caso_id):
    with get_session() as tx:
        require_case_role(tx, current_user_id, caso_id, READ_ROLES)
        return get_case_uncertainty_evolution(tx, caso_id)


def get_suspect_history_service(current_user_id: str, suspeito_id):
    with get_session() as tx:
        caso_id = get_case_id_for_suspect(tx, suspeito_id)
        if not caso_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suspeito não encontrado")
        require_case_role(tx, current_user_id, caso_id, READ_ROLES)
        return get_suspect_history(tx, suspeito_id)


def get_suspect_analysis_service(current_user_id: str, caso_id, suspeito_id):
    with get_session() as tx:
        require_case_role(tx, current_user_id, caso_id, READ_ROLES)
        return get_suspect_analysis(tx, caso_id, suspeito_id)