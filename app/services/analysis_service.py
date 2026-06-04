from app.database.neo4j import get_session
from app.repositories.analysis_repository import (
    generate_analysis,
    get_case_uncertainty_evolution,
    get_suspect_history,
    get_suspect_analysis
)


def generate_analysis_service(data):
    with get_session() as tx:
        return generate_analysis(tx, data)


def get_case_uncertainty_evolution_service(caso_id):
    with get_session() as tx:
        return get_case_uncertainty_evolution(tx, caso_id)


def get_suspect_history_service(suspeito_id):
    with get_session() as tx:
        return get_suspect_history(tx, suspeito_id)
    

def get_suspect_analysis_service(caso_id, suspeito_id):
    with get_session() as tx:
        return get_suspect_analysis(tx, caso_id, suspeito_id)