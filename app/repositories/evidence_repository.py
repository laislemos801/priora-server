def create_evidence(tx, data):
    query = """
    MATCH (c:Caso {id: $casoId})
    CREATE (e:Evidencia {
      id:              randomUUID(),
      nome:            $nome,
      tipo:            $tipo,
      descricao:       $descricao,
      status:          $status,
      dataColeta:      date($dataColeta),
      pesoCondicional: $peso,
      criadoEm:        datetime(),
      atualizadoEm:    datetime()
    })
    CREATE (c)-[:TEM_EVIDENCIA { adicionadaEm: datetime() }]->(e)
    WITH e
    UNWIND $suspeitoIds AS suspeitoId
    MATCH (s:Suspeito {id: suspeitoId})
    CREATE (e)-[:VINCULA {
      pesoCondicional: $pesoVinculo,
      vinculadoEm: datetime()
    }]->(s)
    RETURN e { .id, .nome, .tipo, .status, .pesoCondicional } AS evidencia
    """
    result = tx.run(query,
        casoId=data["casoId"],
        suspeitoIds=data["suspeitoIds"],
        nome=data["nome"],
        tipo=data["tipo"],
        descricao=data.get("descricao"),
        status=data["status"],
        dataColeta=data["dataColeta"],
        peso=data["peso"],
        pesoVinculo=data["pesoVinculo"],
    )
    record = result.single()
    if not record:
        raise Exception("Caso não encontrado")
    return record["evidencia"]


def list_evidences_by_case(tx, caso_id):
    query = """
    MATCH (c:Caso {id: $casoId})-[:TEM_EVIDENCIA]->(e:Evidencia)
    OPTIONAL MATCH (e)-[:VINCULA]->(s:Suspeito)
    WITH e, collect(s { .id, .nome }) AS suspeitos
    ORDER BY e.criadoEm DESC
    RETURN e {
      .id, .nome, .tipo, .status, .dataColeta, .pesoCondicional
    } AS evidencia,
    suspeitos
    """
    result = tx.run(query, casoId=caso_id)
    return [
        {
            **record["evidencia"],
            "dataColeta": str(record["evidencia"]["dataColeta"]) if record["evidencia"]["dataColeta"] else None,
            "suspeitos": record["suspeitos"]
        }
        for record in result
    ]

def delete_evidences(tx, evidence_ids: list[str]):
  query = """
  UNWIND $ids AS eid
  MATCH (e:Evidencia {id: eid})
  DETACH DELETE e
  """
  tx.run(query, ids=evidence_ids)