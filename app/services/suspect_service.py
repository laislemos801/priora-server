from fastapi import HTTPException, status

from app.database.neo4j import get_session
from app.core.authorization import require_case_role, READ_ROLES, WRITE_ROLES
from app.services.bayes_service import recalculate_case
from app.repositories.suspect_repository import (
    create_suspect,
    list_suspects_by_case,
    update_suspect_ranking,
    update_suspect,
    delete_suspect,
    get_case_id_for_suspect,
)


def create_suspect_service(current_user_id: str, data):
    with get_session() as tx:
        require_case_role(tx, current_user_id, data["casoId"], WRITE_ROLES)
        suspeito = create_suspect(tx, data)
        # cadastrar um novo suspeito muda o denominador (n) e dispara o
        # recálculo automático das probabilidades (doc, UC02, regra de negócio)
        recalculate_case(tx, data["casoId"])
        return suspeito


def list_suspects_service(current_user_id: str, caso_id):
    with get_session() as tx:
        require_case_role(tx, current_user_id, caso_id, READ_ROLES)
        return list_suspects_by_case(tx, caso_id)


def update_suspect_ranking_service(current_user_id: str, caso_id):
    with get_session() as tx:
        require_case_role(tx, current_user_id, caso_id, WRITE_ROLES)
        return update_suspect_ranking(tx, caso_id)


def update_suspect_service(current_user_id: str, suspect_id, data):
    with get_session() as tx:
        caso_id = get_case_id_for_suspect(tx, suspect_id)
        if not caso_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suspeito não encontrado")
        require_case_role(tx, current_user_id, caso_id, WRITE_ROLES)
        suspeito = update_suspect(tx, suspect_id, data)
        # editar o perfil de um suspeito não muda a fórmula bayesiana em si,
        # mas dispara o recálculo para manter o ranking/tendência atualizados
        # (doc, UC02, regra de negócio: "Ao cadastrar ou editar um suspeito...")
        recalculate_case(tx, caso_id)
        return suspeito


def delete_suspect_service(current_user_id: str, caso_id, suspect_id):
    with get_session() as tx:
        require_case_role(tx, current_user_id, caso_id, WRITE_ROLES)
        result = delete_suspect(tx, caso_id, suspect_id)
        # remover um suspeito muda o denominador (n) e o conjunto de
        # hipóteses — recalcula para os suspeitos remanescentes
        recalculate_case(tx, caso_id)
        return result