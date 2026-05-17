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
        s.idade AS idade,
        s.fotoUrl AS fotoUrl,
        s.probabilidadeAtual AS probabilidadeAtual,
        s.tendencia AS tendencia,
        s.comportamento AS comportamento,
        s.agressividade AS agressividade,
        s.proximidade AS proximidade,
        s.conexoesSociais AS conexoesSociais,
        s.nivelConfissao AS nivelConfissao,
        s.crimeSimilarAntes AS crimeSimilarAntes,
        s.histDescumprimento AS histDescumprimento,
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


def update_suspect(tx, suspect_id, data):
    query = """
    MATCH (s:Suspeito {id: $suspectId})
    SET s.nome = $nome,
        s.idade = $idade,
        s.fotoUrl = $fotoUrl,
        s.comportamento = $comportamento,
        s.agressividade = $agressividade,
        s.proximidade = $proximidade,
        s.conexoesSociais = $conexoesSociais,
        s.nivelConfissao = $nivelConfissao,
        s.crimeSimilarAntes = $crimeSimilarAntes,
        s.histDescumprimento = $histDescumprimento,
        s.atualizadoEm = datetime()
    RETURN s {
        .id, .nome, .idade, .fotoUrl,
        .comportamento, .agressividade, .proximidade,
        .conexoesSociais, .nivelConfissao,
        .crimeSimilarAntes, .histDescumprimento,
        .probabilidadeAtual, .posicaoRanking, .tendencia
    } AS suspeito
    """

    result = tx.run(query, suspectId=suspect_id, **data)
    record = result.single()

    if not record:
        raise Exception("Suspeito não encontrado")

    return record["suspeito"]


def delete_suspect(tx, caso_id, suspect_id):
    query = """
    MATCH (c:Caso {id: $casoId})-[r:TEM_SUSPEITO]->(s:Suspeito {id: $suspectId})

    OPTIONAL MATCH (e:Evidencia)-[v:VINCULA]->(s)
    DELETE v

    WITH c, r, s

    OPTIONAL MATCH (s)-[rel]-()
    DELETE rel

    WITH r, s

    DELETE r, s

    RETURN $suspectId AS suspectId
    """

    result = tx.run(
        query,
        casoId=caso_id,
        suspectId=suspect_id
    )

    record = result.single()

    if not record:
        raise Exception("Suspeito não encontrado neste caso")

    return {
        "deleted": True,
        "suspectId": suspect_id
    }