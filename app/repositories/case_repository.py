def create_case(tx, user_id, data):
    query = """
    MATCH (u:Usuario {id: $userId})
    CREATE (c:Caso {
        id: randomUUID(),
        nome: $nome,
        descricao: $descricao,
        status: $status,
        prioridade: $prioridade,
        enderecoCep: $cep,
        enderecoLogradouro: $logradouro,
        enderecoNumero: $numero,
        enderecoBairro: $bairro,
        enderecoCidade: $cidade,
        enderecoEstado: $estado,
        dataOcorrencia: date($dataOcorrencia),
        incerteza: 100.0,
        criadoEm: datetime(),
        atualizadoEm: datetime()
    })
    CREATE (u)-[:RESPONSAVEL_POR {atribuidoEm: datetime()}]->(c)
    RETURN c {
        .id, .nome, .status, .prioridade, .incerteza
    } AS caso
    """
    result = tx.run(query,
        userId=user_id,
        nome=data["nome"],
        descricao=data["descricao"],
        status=data["status"],
        prioridade=data["prioridade"],
        cep=data.get("enderecoCep"),      
        logradouro=data.get("enderecoLogradouro"),
        numero=data.get("enderecoNumero"),
        bairro=data.get("enderecoBairro"),
        cidade=data.get("enderecoCidade"),
        estado=data.get("enderecoEstado"),
        dataOcorrencia=data.get("dataOcorrencia")
    )
    return result.single()["caso"]


def get_cases_by_user(tx, user_id):
    query = """
    MATCH (u:Usuario {id: $userId})
    OPTIONAL MATCH (u)-[:RESPONSAVEL_POR]->(c1:Caso)
    OPTIONAL MATCH (u)-[:TEM_ACESSO {status: 'Ativo'}]->(c2:Caso)

    WITH collect(c1) + collect(c2) AS todos
    UNWIND todos AS c
    WITH c
    WHERE c IS NOT NULL

    OPTIONAL MATCH (c)-[:TEM_SUSPEITO]->(s:Suspeito)
    OPTIONAL MATCH (c)-[:TEM_EVIDENCIA]->(e:Evidencia)
    OPTIONAL MATCH (resp:Usuario)-[:RESPONSAVEL_POR]->(c)

    WITH c, resp,
         collect(DISTINCT s)[0] AS topSuspeito,
         count(DISTINCT s)      AS qtdSuspeitos,
         count(DISTINCT e)      AS qtdEvidencias,
         c.atualizadoEm         AS atualizadoEm

    RETURN DISTINCT
      c.id               AS id,
      c.nome             AS nome,
      c.descricao        AS descricao,
      c.status           AS status,
      c.prioridade       AS prioridade,
      c.incerteza        AS incerteza,
      c.dataOcorrencia   AS dataOcorrencia,
      c.enderecoCidade   AS cidade,
      c.enderecoEstado   AS estado,
      resp.primeiroNome  AS responsavelPrimeiroNome,
      resp.sobrenome     AS responsavelSobrenome,
      topSuspeito.nome   AS topSuspeitoNome,
      topSuspeito.probabilidadeAtual AS topSuspeitoProbab,
      qtdSuspeitos,
      qtdEvidencias,
      atualizadoEm
    ORDER BY atualizadoEm DESC
    """

    result = tx.run(query, userId=user_id)

    return [
        {
            **record.data(),
            "dataOcorrencia": str(record["dataOcorrencia"]) if record["dataOcorrencia"] else None
        }
        for record in result
    ]


def update_case_uncertainty(tx, caso_id, nova_incerteza):
    query = """
    MATCH (c:Caso {id: $casoId})
    SET c.incerteza = $novaIncerteza,
        c.atualizadoEm = datetime()
    RETURN c.id AS id, c.incerteza AS incerteza
    """
    result = tx.run(query,
        casoId=caso_id,
        novaIncerteza=nova_incerteza
    )
    return result.single()

def get_case_by_id_tx(tx, case_id):
    query = """
    MATCH (c:Caso {id: $caseId})

    OPTIONAL MATCH (u:Usuario)-[:RESPONSAVEL_POR]->(c)

    OPTIONAL MATCH (c)-[:TEM_SUSPEITO]->(s:Suspeito)
    WITH c, u, count(DISTINCT s) AS totalSuspeitos

    OPTIONAL MATCH (c)-[:TEM_EVIDENCIA]->(e:Evidencia)
    WITH c, u, totalSuspeitos,
         count(DISTINCT e) AS totalEvidencias

    RETURN c {
        .id,
        .nome,
        .descricao,
        .status,
        .prioridade,
        .enderecoCep,
        .enderecoLogradouro,
        .enderecoNumero,
        .enderecoBairro,
        .enderecoCidade,
        .enderecoEstado,
        .incerteza,

        dataOcorrencia: toString(c.dataOcorrencia),
        criadoEm: toString(c.criadoEm),
        atualizadoEm: toString(c.atualizadoEm),

        totalSuspeitos: totalSuspeitos,
        totalEvidencias: totalEvidencias,

        responsavel: u {
            .id,
            .primeiroNome,
            .sobrenome,
            .email
        }
    } AS caso
    """

    result = tx.run(query, caseId=case_id)
    record = result.single()

    return record["caso"] if record else None

def update_case(tx, caso_id, data):
    query = """
    MATCH (c:Caso {id: $casoId})
    SET c.nome = $nome,
        c.descricao = $descricao,
        c.status = $status,
        c.prioridade = $prioridade,
        c.enderecoCep = $enderecoCep,
        c.enderecoLogradouro = $enderecoLogradouro,
        c.enderecoNumero = $enderecoNumero,
        c.enderecoBairro = $enderecoBairro,
        c.enderecoCidade = $enderecoCidade,
        c.enderecoEstado = $enderecoEstado,
        c.dataOcorrencia = date($dataOcorrencia),
        c.atualizadoEm = datetime()
    RETURN c {
        .id, .nome, .descricao, .status, .prioridade,
        .enderecoCep, .enderecoLogradouro, .enderecoNumero,
        .enderecoBairro, .enderecoCidade, .enderecoEstado,
        dataOcorrencia: toString(c.dataOcorrencia),
        atualizadoEm: toString(c.atualizadoEm)
    } AS caso
    """
    result = tx.run(query, casoId=caso_id, **data)
    record = result.single()

    if not record:
        raise Exception("Caso não encontrado")

    return record["caso"]

def delete_case(tx, caso_id):
    query = """
    MATCH (c:Caso {id: $casoId})

    OPTIONAL MATCH (c)-[r]-()
    DELETE r

    WITH c

    DELETE c

    RETURN $casoId AS casoId
    """

    result = tx.run(query, casoId=caso_id)
    record = result.single()

    if not record:
        raise Exception("Caso não encontrado")

    return {
        "deleted": True,
        "casoId": caso_id
    }