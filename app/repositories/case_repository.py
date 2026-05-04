def create_case(tx, user_id, data):
    query = """
    MATCH (u:Usuario {id: $userId})
    CREATE (c:Caso {
        id: randomUUID(),
        nome: $nome,
        descricao: $descricao,
        status: $status,
        prioridade: $prioridade,
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
    OPTIONAL MATCH (c)-[:TEM_SUSPEITO]->(s:Suspeito)
    OPTIONAL MATCH (c)-[:TEM_EVIDENCIA]->(e:Evidencia)
    WITH c,
         collect(DISTINCT s)[0] AS topSuspeito,
         count(DISTINCT s)     AS qtdSuspeitos,
         count(DISTINCT e)     AS qtdEvidencias
    RETURN DISTINCT
      c.id AS id,
      c.nome AS nome,
      c.descricao AS descricao,
      c.status AS status,
      c.prioridade AS prioridade,
      c.incerteza AS incerteza,
      c.dataOcorrencia AS dataOcorrencia,
      c.enderecoCidade AS cidade,
      c.enderecoEstado AS estado,
      topSuspeito.nome AS topSuspeitoNome,
      topSuspeito.probabilidadeAtual AS topSuspeitoProbab,
      qtdSuspeitos,
      qtdEvidencias
    ORDER BY c.atualizadoEm DESC
    """
    result = tx.run(query, userId=user_id)
    return [record.data() for record in result]


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