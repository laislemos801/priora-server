def create_suspect(tx, data):
    query = """
    MATCH (c:Caso {id: $casoId})
    CREATE (s:Suspeito {
        id: randomUUID(),
        nome: $nome,
        idade: $idade,
        fotoUrl: $fotoUrl,

        probabilidadeAtual: 0.0,
        posicaoRanking: null,
        tendencia: 'Estável',

        comportamento: $comportamento,
        agressividade: $agressividade,
        proximidade: $proximidade,
        conexoesSociais: $conexoesSociais,
        nivelConfissao: $nivelConfissao,

        crimeSimilarAntes: $crimeSimilarAntes,
        histDescumprimento: $histDescumprimento,

        criadoEm: datetime(),
        atualizadoEm: datetime()
    })
    CREATE (c)-[:TEM_SUSPEITO {adicionadoEm: datetime()}]->(s)
    RETURN s {
        .id,
        .nome,
        .probabilidadeAtual,
        .posicaoRanking,
        .tendencia
    } AS suspeito
    """

    result = tx.run(query, **data)
    record = result.single()

    if not record:
        raise Exception("Caso não encontrado")

    return record["suspeito"]


def list_suspects_by_case(tx, caso_id):
    query = """
    MATCH (c:Caso {id: $casoId})-[:TEM_SUSPEITO]->(s:Suspeito)
    OPTIONAL MATCH (s)<-[:VINCULA]-(e:Evidencia)
    RETURN
        s.posicaoRanking AS posicaoRanking,
        s.id AS id,
        s.nome AS nome,
        s.fotoUrl AS fotoUrl,
        s.probabilidadeAtual AS probabilidadeAtual,
        s.tendencia AS tendencia,
        count(e) AS qtdEvidencias
    ORDER BY s.probabilidadeAtual DESC
    """

    result = tx.run(query, casoId=caso_id)
    return [record.data() for record in result]


def update_suspect_ranking(tx, caso_id):
    query = """
    MATCH (c:Caso {id: $casoId})-[:TEM_SUSPEITO]->(s:Suspeito)
    WITH s ORDER BY s.probabilidadeAtual DESC
    WITH collect(s) AS ranking
    UNWIND range(0, size(ranking)-1) AS i
    WITH ranking[i] AS s, i+1 AS pos
    SET s.posicaoRanking = pos,
        s.atualizadoEm = datetime()
    RETURN
        s.id AS id,
        s.nome AS nome,
        s.posicaoRanking AS posicaoRanking,
        s.probabilidadeAtual AS probabilidadeAtual
    ORDER BY s.posicaoRanking ASC
    """

    result = tx.run(query, casoId=caso_id)
    return [record.data() for record in result]