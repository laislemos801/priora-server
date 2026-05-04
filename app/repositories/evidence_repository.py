def create_evidence(tx, data):
    query = """
    MATCH (c:Caso {id: $casoId}),
          (s:Suspeito {id: $suspeitoId})
    CREATE (e:Evidencia {
      id:              randomUUID(),
      nome:            $nome,
      tipo:            $tipo,
      descricao:       $descricao,
      status:          'Coletada',
      dataColeta:      date($dataColeta),
      pesoCondicional: $peso,
      criadoEm:        datetime(),
      atualizadoEm:    datetime()
    })
    CREATE (c)-[:TEM_EVIDENCIA {
      adicionadaEm: datetime()
    }]->(e)
    CREATE (e)-[:VINCULA {
      pesoCondicional: $pesoVinculo,
      vinculadoEm: datetime()
    }]->(s)
    RETURN e {
      .id, .nome, .tipo, .status, .pesoCondicional
    } AS evidencia
    """

    result = tx.run(query, **data)
    record = result.single()

    if not record:
        raise Exception("Caso ou Suspeito não encontrado")

    return record["evidencia"]


def list_evidences_by_case(tx, caso_id):
    query = """
    MATCH (c:Caso {id: $casoId})-[:TEM_EVIDENCIA]->(e:Evidencia)
    RETURN e {
      .id, .nome, .tipo, .status, .dataColeta, .pesoCondicional
    } AS evidencia
    ORDER BY e.criadoEm DESC
    """

    result = tx.run(query, casoId=caso_id)
    return [record["evidencia"] for record in result]