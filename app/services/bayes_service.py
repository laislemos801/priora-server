from app.database.neo4j import get_session
from app.bayes.model import BayesianNetwork
from app.core.authorization import require_case_role, READ_ROLES
from app.repositories.bayes_repository import (
    get_suspects_for_bayes,
    get_evidences_for_bayes,
    get_previous_results_for_bayes,
    save_bayes_results,
    save_analysis_snapshot,
)


def recalculate_case(tx, caso_id: str) -> dict | None:
    """
    Executa a inferência bayesiana completa para o caso e persiste os
    resultados (ranking dos suspeitos + snapshot :AnaliseProb).

    Reutilizada tanto pelo endpoint explícito POST /bayes/preview/{caso_id}
    quanto automaticamente pelos serviços de suspeito e evidência sempre
    que um cadastro/edição/exclusão altera os dados do caso (UC02, UC05,
    UC07 da documentação).

    Retorna None se o caso ainda não possui suspeitos cadastrados
    (nada para calcular).
    """
    suspects = get_suspects_for_bayes(tx, caso_id)

    if not suspects:
        return None

    evidences         = get_evidences_for_bayes(tx, caso_id)
    previous_results  = get_previous_results_for_bayes(tx, caso_id)

    network = BayesianNetwork()
    result  = network.run(
        case_id=caso_id,
        suspects=suspects,
        evidences=evidences,
        version=1,
        previous_results=previous_results,
    )

    result_dict = result.to_dict()

    save_bayes_results(
        tx,
        caso_id,
        result_dict["ranking"],
        result_dict["case_uncertainty"],
    )

    save_analysis_snapshot(
        tx,
        caso_id,
        result_dict["ranking"],
    )

    return result_dict


def run_bayes_preview_service(current_user_id: str, caso_id):
    with get_session() as tx:
        require_case_role(tx, current_user_id, caso_id, READ_ROLES)
        return recalculate_case(tx, caso_id)
