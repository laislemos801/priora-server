import json


def get_case_history(tx, caso_id):

    query = """
    MATCH (h:HistoricoCaso)-[:REFERENTE_A]->(c:Caso {id: $casoId})

    OPTIONAL MATCH (u:Usuario)-[:REALIZOU]->(h)

    RETURN {
        id: h.id,
        casoId: c.id,

        action: h.tipo,
        entityType: h.entidade,

        entityId: h.entityId,
        entityName: h.entityName,

        details: h.valorNovo,

        createdAt: toString(h.criadoEm),

        user: CASE
            WHEN u IS NULL THEN NULL
            ELSE {
                id: u.id,
                primeiroNome: u.primeiroNome,
                sobrenome: u.sobrenome,
                fotoUrl: u.fotoUrl
            }
        END
    } AS historico

    ORDER BY h.criadoEm DESC
    """

    result = tx.run(
        query,
        casoId=caso_id
    )

    return [
        record["historico"]
        for record in result
    ]



def create_history(
    tx,
    user_id,
    caso_id,
    action,
    entity_type,
    entity_id=None,
    entity_name=None,
    details=None,
    valor_novo=None,
):

    query = """
    MATCH (u:Usuario {id: $userId})
    MATCH (c:Caso {id: $casoId})

    CREATE (h:HistoricoCaso {

        id: randomUUID(),

        tipo: $tipo,

        entidade: $entidade,

        entityId: $entityId,

        entityName: $entityName,

        valorNovo: $valorNovo,

        criadoEm: datetime()
    })


    CREATE (u)-[:REALIZOU]->(h)

    CREATE (h)-[:REFERENTE_A]->(c)

    RETURN h
    """


    if valor_novo is not None and not isinstance(valor_novo, str):

        valor_novo = json.dumps(
            valor_novo,
            ensure_ascii=False,
            default=str
        )


    if details is not None and not isinstance(details, str):

        details = json.dumps(
            details,
            ensure_ascii=False,
            default=str
        )


    result = tx.run(
        query,

        userId=user_id,

        casoId=caso_id,

        tipo=action,

        entidade=entity_type,

        entityId=entity_id,

        entityName=entity_name,

        valorNovo=details or valor_novo
    )


    return result.single()