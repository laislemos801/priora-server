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

# buscar evidência por id, incluindo suspeitos vinculados e pesoVinculo
def get_evidence_by_id(tx, evidence_id: str):
    query = """
    MATCH (e:Evidencia {id: $evidenceId})
    OPTIONAL MATCH (e)-[v:VINCULA]->(s:Suspeito)
    WITH e, collect(s { .id, .nome }) AS suspeitos,
         collect(v.pesoCondicional)[0] AS pesoVinculo
    RETURN e {
      .id, .nome, .tipo, .status, .descricao,
      .pesoCondicional, .dataColeta
    } AS evidencia, suspeitos, pesoVinculo
    """
    result = tx.run(query, evidenceId=evidence_id)
    record = result.single()
    if not record:
        raise Exception("Evidência não encontrada")
    ev = dict(record["evidencia"])
    ev["dataColeta"]  = str(ev["dataColeta"]) if ev.get("dataColeta") else None
    ev["pesoVinculo"] = record["pesoVinculo"]
    ev["suspeitos"]   = record["suspeitos"]
    return ev


def update_evidence(tx, evidence_id: str, data: dict):
    """
    Atualiza campos escalares da evidência e,
    se suspeitoIds for passado, recria os vínculos VINCULA.
    """
    # Monta SET dinâmico só com os campos enviados
    scalar_fields = {
        k: v for k, v in data.items()
        if k not in ("suspeitoIds",) and v is not None
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
        "pesoVinculo": None,  # tratado via vínculos
    }

    for field, value in scalar_fields.items():
        if field == "pesoVinculo":
            continue           # só atualizado nos vínculos
        if field not in field_map or field_map[field] is None:
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

    # Se suspeitoIds foi enviado, recria vínculos VINCULA
    suspeitoIds = data.get("suspeitoIds")
    pesoVinculo = data.get("pesoVinculo")

    if suspeitoIds is not None:
        query += """
    WITH e
    OPTIONAL MATCH (e)-[r:VINCULA]->()
    DELETE r
    WITH e
    UNWIND $suspeitoIds AS sid
    MATCH (s:Suspeito {id: sid})
    CREATE (e)-[:VINCULA {
        pesoCondicional: $pesoVinculo,
        vinculadoEm: datetime()
    }]->(s)
        """
        params["suspeitoIds"] = suspeitoIds
        params["pesoVinculo"] = pesoVinculo if pesoVinculo is not None else 0.5

    query += """
    WITH e
    OPTIONAL MATCH (e)-[:VINCULA]->(s:Suspeito)
    WITH e, collect(s { .id, .nome }) AS suspeitos
    RETURN e {
        .id, .nome, .tipo, .status, .descricao,
        .pesoCondicional
    } AS evidencia, suspeitos
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