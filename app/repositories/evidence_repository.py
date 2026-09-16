def get_case_id_for_evidence(tx, evidence_id: str) -> str | None:
    query = """
    MATCH (c:Caso)-[:TEM_EVIDENCIA]->(e:Evidencia {id: $evidenceId})
    RETURN c.id AS casoId
    """
    record = tx.run(query, evidenceId=evidence_id).single()
    return record["casoId"] if record else None


def get_case_ids_for_evidences(tx, evidence_ids: list[str]) -> list[str]:
    query = """
    UNWIND $ids AS eid
    MATCH (c:Caso)-[:TEM_EVIDENCIA]->(e:Evidencia {id: eid})
    RETURN DISTINCT c.id AS casoId
    """
    result = tx.run(query, ids=evidence_ids)
    return [record["casoId"] for record in result]


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
    UNWIND $vinculos AS v
    MATCH (s:Suspeito {id: v.suspeitoId})
    CREATE (e)-[:VINCULA {
      pesoVinculo: v.pesoVinculo,
      vinculadoEm: datetime()
    }]->(s)
    RETURN e { .id, .nome, .tipo, .status, .pesoCondicional } AS evidencia
    """
    result = tx.run(query,
        casoId=data["casoId"],
        vinculos=data["vinculos"],
        nome=data["nome"],
        tipo=data["tipo"],
        descricao=data.get("descricao"),
        status=data["status"],
        dataColeta=data["dataColeta"],
        peso=data["peso"],
    )
    record = result.single()
    if not record:
        raise Exception("Caso não encontrado")
    return record["evidencia"]


_SUSPEITOS_COM_PESO = """
    WITH e, collect(
        CASE WHEN s IS NOT NULL
            THEN { id: s.id, nome: s.nome, pesoVinculo: v.pesoVinculo }
            ELSE NULL
        END
    ) AS suspeitosRaw
    WITH e, [x IN suspeitosRaw WHERE x IS NOT NULL] AS suspeitos
"""


def list_evidences_by_case(tx, caso_id):
    query = f"""
    MATCH (c:Caso {{id: $casoId}})-[:TEM_EVIDENCIA]->(e:Evidencia)
    OPTIONAL MATCH (e)-[v:VINCULA]->(s:Suspeito)
    {_SUSPEITOS_COM_PESO}
    ORDER BY e.criadoEm DESC
    RETURN e {{
      .id, .nome, .tipo, .status, .dataColeta, .pesoCondicional
    }} AS evidencia,
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

# buscar evidência por id, incluindo suspeitos vinculados e o pesoVinculo de cada um
def get_evidence_by_id(tx, evidence_id: str):
    query = f"""
    MATCH (e:Evidencia {{id: $evidenceId}})
    OPTIONAL MATCH (e)-[v:VINCULA]->(s:Suspeito)
    {_SUSPEITOS_COM_PESO}
    RETURN e {{
      .id, .nome, .tipo, .status, .descricao,
      .pesoCondicional, .dataColeta
    }} AS evidencia, suspeitos
    """
    result = tx.run(query, evidenceId=evidence_id)
    record = result.single()
    if not record:
        raise Exception("Evidência não encontrada")
    ev = dict(record["evidencia"])
    ev["dataColeta"]  = str(ev["dataColeta"]) if ev.get("dataColeta") else None
    ev["suspeitos"]   = record["suspeitos"]
    return ev


def update_evidence(tx, evidence_id: str, data: dict):
    """
    Atualiza campos escalares da evidência e,
    se `vinculos` for passado, recria os vínculos VINCULA
    com o pesoVinculo individual de cada suspeito.
    """
    # Monta SET dinâmico só com os campos enviados
    scalar_fields = {
        k: v for k, v in data.items()
        if k not in ("vinculos",) and v is not None
    }

    set_clauses = []
    params: dict = {"evidenceId": evidence_id}

    field_map = {
        "nome":       "e.nome",
        "tipo":       "e.tipo",
        "status":     "e.status",
        "descricao":  "e.descricao",
        "dataColeta": "e.dataColeta",
        "peso":       "e.pesoCondicional",
    }

    for field, value in scalar_fields.items():
        if field not in field_map:
            continue
        neo4j_prop = field_map[field]
        param_name = field
        if field == "dataColeta":
            set_clauses.append(f"{neo4j_prop} = date(${param_name})")
        else:
            set_clauses.append(f"{neo4j_prop} = ${param_name}")
        params[param_name] = value

    set_clauses.append("e.atualizadoEm = datetime()")

    set_str = ", ".join(set_clauses)

    query = f"""
    MATCH (e:Evidencia {{id: $evidenceId}})
    SET {set_str}
    """

    # Se vinculos foi enviado, recria os vínculos VINCULA com o peso de cada suspeito
    vinculos = data.get("vinculos")

    if vinculos is not None:
        query += """
    WITH e
    OPTIONAL MATCH (e)-[r:VINCULA]->()
    DELETE r
    WITH e
    UNWIND $vinculos AS v
    MATCH (s:Suspeito {id: v.suspeitoId})
    CREATE (e)-[:VINCULA {
        pesoVinculo: v.pesoVinculo,
        vinculadoEm: datetime()
    }]->(s)
        """
        params["vinculos"] = vinculos

    query += f"""
    WITH e
    OPTIONAL MATCH (e)-[v:VINCULA]->(s:Suspeito)
    {_SUSPEITOS_COM_PESO}
    RETURN e {{
        .id, .nome, .tipo, .status, .descricao,
        .pesoCondicional
    }} AS evidencia, suspeitos
    """

    result = tx.run(query, **params)
    record = result.single()
    if not record:
        raise Exception("Evidência não encontrada")

    ev = dict(record["evidencia"])
    if ev.get("dataColeta"):
        ev["dataColeta"] = str(ev["dataColeta"])
    ev["suspeitos"] = record["suspeitos"]
    return ev
