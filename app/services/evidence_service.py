from fastapi import HTTPException, status

from app.database.neo4j import get_session
from app.core.authorization import require_case_role, READ_ROLES, WRITE_ROLES
from app.services.bayes_service import recalculate_case
from app.repositories.evidence_repository import (
    create_evidence,
    list_evidences_by_case,
    delete_evidences,
    update_evidence,
    get_evidence_by_id,
    get_case_id_for_evidence,
    get_case_ids_for_evidences,
)


def create_evidence_service(current_user_id: str, data):
    with get_session() as session:
        require_case_role(session, current_user_id, data["casoId"], WRITE_ROLES)
        evidencia = create_evidence(session, data)
        # nova evidência (e seus vínculos) alteram o score de todos os
        # suspeitos vinculados — recálculo automático (doc, UC01/UC07)
        recalculate_case(session, data["casoId"])
        return evidencia


def list_evidences_service(current_user_id: str, caso_id):
    with get_session() as session:
        require_case_role(session, current_user_id, caso_id, READ_ROLES)
        return list_evidences_by_case(session, caso_id)

def delete_evidences_service(current_user_id: str, ids: list[str]):
    with get_session() as session:
        caso_ids = get_case_ids_for_evidences(session, ids)
        if not caso_ids:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidências não encontradas")
        for caso_id in caso_ids:
            require_case_role(session, current_user_id, caso_id, WRITE_ROLES)
        result = delete_evidences(session, ids)
        # remover evidências muda a força/exclusividade das que restam —
        # recalcula todos os casos afetados
        for caso_id in caso_ids:
            recalculate_case(session, caso_id)
        return result

def update_evidence_service(current_user_id: str, evidence_id: str, data: dict):
    with get_session() as session:
        caso_id = get_case_id_for_evidence(session, evidence_id)
        if not caso_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidência não encontrada")
        require_case_role(session, current_user_id, caso_id, WRITE_ROLES)
        evidencia = update_evidence(session, evidence_id, data)
        # editar peso/vínculos de uma evidência altera diretamente o score
        # bayesiano — recálculo automático (doc, UC05: "Ao criar ou
        # modificar um vínculo, o cálculo é disparado automaticamente")
        recalculate_case(session, caso_id)
        return evidencia

def get_evidence_service(current_user_id: str, evidence_id: str):
    with get_session() as session:
        caso_id = get_case_id_for_evidence(session, evidence_id)
        if not caso_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidência não encontrada")
        require_case_role(session, current_user_id, caso_id, READ_ROLES)
        return get_evidence_by_id(session, evidence_id)
