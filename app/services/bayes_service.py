from app.database.neo4j import get_session
from app.bayes.model import BayesianNetwork
from app.repositories.bayes_repository import (
    get_suspects_for_bayes,
    get_evidences_for_bayes,
    save_bayes_results,
)


def run_bayes_preview_service(caso_id):
    with get_session() as tx:
        suspects  = get_suspects_for_bayes(tx, caso_id)
        evidences = get_evidences_for_bayes(tx, caso_id)

        network = BayesianNetwork()
        result  = network.run(
            case_id=caso_id,
            suspects=suspects,
            evidences=evidences,
            version=1,
        )

        save_bayes_results(tx, caso_id, result.to_dict()["ranking"])

        return result.to_dict()