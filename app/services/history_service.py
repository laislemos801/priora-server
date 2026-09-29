from app.database.neo4j import get_session


def get_case_history_service(user_id: str, caso_id: str):
    query = """
    MATCH (u:Usuario {id: $user_id})-[:REALIZOU]->(h:HistoricoCaso)-[:REFERENTE_A]->(c:Caso {id: $caso_id})

    RETURN {
        id: h.id,
        userId: u.id,
        casoId: c.id,
        action: h.tipo,
        entityType: h.entidade,
        entityId: c.id,
        entityName: c.nome,
        details: h.valorNovo,
        createdAt: toString(h.criadoEm),
        user: {
            id: u.id,
            primeiroNome: u.primeiroNome,
            sobrenome: u.sobrenome,
            fotoUrl: u.fotoUrl
        }
    } AS historico

    ORDER BY h.criadoEm DESC
    """

    with get_session() as session:
        result = session.run(
            query,
            user_id=user_id,
            caso_id=caso_id
        )

        return [record["historico"] for record in result]