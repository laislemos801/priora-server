def generate_analysis(tx, data):
    query = """
    MATCH (c:Caso {id: $casoId})
    MATCH (c)-[:TEM_SUSPEITO]->(s:Suspeito)

    WITH c, collect(s) AS suspeitos
    WITH c, suspeitos, size(suspeitos) AS nSuspeitos
    WHERE nSuspeitos > 0

    OPTIONAL MATCH (c)-[:TEM_ANALISE]->(old:AnaliseProb)
    WITH c, suspeitos, nSuspeitos, coalesce(max(old.versao), 0) + 1 AS novaVersao

    UNWIND suspeitos AS s

    OPTIONAL MATCH (e:Evidencia)-[v:VINCULA]->(s)
    WITH c, s, nSuspeitos, novaVersao,
        collect(e.pesoCondicional * coalesce(v.pesoCondicional, 1.0)) AS pesos

    WITH c, s, nSuspeitos, novaVersao, pesos,
         CASE
           WHEN size(pesos) = 0 THEN null
           ELSE reduce(acc = 1.0, p IN pesos | acc * p)
         END AS pEH

    WITH c, s, nSuspeitos, novaVersao, pesos, pEH,
         1.0 / toFloat(nSuspeitos) AS pH,
         1.0 - (1.0 / toFloat(nSuspeitos)) AS pNaoH

    WITH c, s, nSuspeitos, novaVersao, pesos, pEH, pH, pNaoH,
         CASE
           WHEN size(pesos) = 0 THEN null
           ELSE 1.0 - pEH
         END AS pENaoH

    WITH c, s, nSuspeitos, novaVersao, pesos, pEH, pH, pNaoH, pENaoH,
         CASE
           WHEN size(pesos) = 0 THEN null
           ELSE pEH * pH
         END AS num,
         CASE
           WHEN size(pesos) = 0 THEN null
           ELSE (pEH * pH) + (pENaoH * pNaoH)
         END AS den

    WITH c, s, novaVersao, pesos, pH, pEH, pENaoH, num, den,
         CASE
           WHEN size(pesos) = 0 THEN pH
           WHEN den = 0 THEN 0.0
           ELSE num / den
         END AS pHE

    CREATE (a:AnaliseProb {
        id: randomUUID(),
        versao: novaVersao,
        pHipotese: pH,
        pEvidenciaDadoH: coalesce(pEH, 0.0),
        pEvidenciaDadoNaoH: coalesce(pENaoH, 0.0),
        numerador: coalesce(num, 0.0),
        denominador: coalesce(den, 0.0),
        pHdadoE: pHE,
        incerteza: 100.0 - (pHE * 100.0),
        geradaEm: datetime(),
        geradaPorId: $userId
    })

    CREATE (c)-[:TEM_ANALISE {geradaEm: datetime()}]->(a)

    CREATE (a)-[:AVALIA {
        probabilidade: pHE,
        posicao: null
    }]->(s)

    CREATE (s)-[:HISTORICO_EM {
        probabilidadeNaEpoca: pHE,
        dataSnapshot: datetime()
    }]->(a)

    SET s.probabilidadeAtual = pHE * 100.0,
        s.atualizadoEm = datetime()

    WITH DISTINCT c, novaVersao

    MATCH (c)-[:TEM_SUSPEITO]->(ranked:Suspeito)
    WITH c, novaVersao, ranked
    ORDER BY ranked.probabilidadeAtual DESC

    WITH c, novaVersao, collect(ranked) AS ranking
    UNWIND range(0, size(ranking)-1) AS i
    WITH c, novaVersao, ranking[i] AS s, i + 1 AS pos

    SET s.posicaoRanking = pos,
        s.atualizadoEm = datetime()

    WITH c, novaVersao, collect({
        id: s.id,
        nome: s.nome,
        probabilidadeAtual: s.probabilidadeAtual,
        posicaoRanking: s.posicaoRanking
    }) AS rankingFinal

    WITH c, novaVersao, rankingFinal,
         reduce(total = 0.0, item IN rankingFinal | total + item.probabilidadeAtual) / size(rankingFinal) AS mediaProbabilidade

    SET c.incerteza = 100.0 - mediaProbabilidade,
        c.atualizadoEm = datetime()

    RETURN {
        versao: novaVersao,
        incertezaCaso: c.incerteza,
        ranking: rankingFinal
    } AS resultado
    """

    result = tx.run(query, **data)
    record = result.single()

    if not record:
        raise Exception("Caso não encontrado ou sem suspeitos")

    return record["resultado"]


def get_case_uncertainty_evolution(tx, caso_id):
    query = """
    MATCH (c:Caso {id: $casoId})-[:TEM_ANALISE]->(a:AnaliseProb)
    RETURN
        a.versao AS versao,
        avg(a.incerteza) AS incerteza,
        toString(min(a.geradaEm)) AS geradaEm
    ORDER BY versao ASC
    """

    result = tx.run(query, casoId=caso_id)
    return [record.data() for record in result]


def get_suspect_history(tx, suspeito_id):
    query = """
    MATCH (s:Suspeito {id: $suspeitoId})-[h:HISTORICO_EM]->(a:AnaliseProb)
    RETURN
        h.probabilidadeNaEpoca * 100.0 AS probabilidade,
        toString(h.dataSnapshot) AS data,
        a.versao AS versao
    ORDER BY h.dataSnapshot ASC
    """

    result = tx.run(query, suspeitoId=suspeito_id)
    return [record.data() for record in result]


def get_suspect_analysis(tx, caso_id, suspeito_id):
    query = """
    MATCH (c:Caso {id: $casoId})-[:TEM_SUSPEITO]->(s:Suspeito {id: $suspeitoId})

    OPTIONAL MATCH (e:Evidencia)-[v:VINCULA]->(s)

    WITH s, collect(
        CASE
            WHEN e IS NOT NULL THEN {
                id: e.id,
                nome: e.nome,
                tipo: e.tipo,
                status: e.status,

                // valor utilizado no cálculo bayesiano
                pesoCondicional: e.pesoCondicional * coalesce(v.pesoCondicional, 1.0),

                // valor original da evidência
                pesoEvidencia: e.pesoCondicional,

                // valor original do vínculo
                pesoVinculo: coalesce(v.pesoCondicional, 1.0),

                dataColeta: toString(e.dataColeta),
                descricao: e.descricao
            }
            ELSE NULL
        END
    ) AS todasEvidencias

    WITH s, [ev IN todasEvidencias WHERE ev IS NOT NULL] AS evidencias

    MATCH (c:Caso {id: $casoId})-[:TEM_SUSPEITO]->(todos:Suspeito)

    WITH s, evidencias, count(todos) AS nSuspeitos

    RETURN {
        id: s.id,
        nome: s.nome,
        fotoUrl: s.fotoUrl,
        probabilidadeAtual: s.probabilidadeAtual,
        posicaoRanking: s.posicaoRanking,
        tendencia: s.tendencia,
        nSuspeitos: nSuspeitos,
        evidencias: evidencias
    } AS resultado
    """

    result = tx.run(
        query,
        casoId=caso_id,
        suspeitoId=suspeito_id
    )

    record = result.single()

    if not record:
        raise Exception("Suspeito não encontrado")

    return record["resultado"]