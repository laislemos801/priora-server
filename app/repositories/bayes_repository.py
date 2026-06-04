from app.bayes.model import (
    Suspect,
    Evidence,
    EvidenceType,
    EvidenceStatus,
)


def get_suspects_for_bayes(tx, caso_id):
    query = """
    MATCH (c:Caso {id: $casoId})-[:TEM_SUSPEITO]->(s:Suspeito)
    RETURN s {
        .id,
        .nome,
        .idade,
        .fotoUrl,
        .comportamento,
        .agressividade,
        .proximidade,
        .conexoesSociais,
        .nivelConfissao,
        .crimeSimilarAntes,
        .histDescumprimento
    } AS suspeito
    ORDER BY s.criadoEm ASC
    """

    result = tx.run(query, casoId=caso_id)

    suspects = []

    for record in result:
        s = record["suspeito"]

        suspects.append(
            Suspect(
                id=s["id"],
                name=s["nome"],
                age=s.get("idade") or 0,
                photo_url=s.get("fotoUrl"),
                behavior=s.get("comportamento") or 50.0,
                aggressiveness=s.get("agressividade") or 50.0,
                proximity=s.get("proximidade") or 50.0,
                social_connections=s.get("conexoesSociais") or 50.0,
                confession_level=s.get("nivelConfissao") or 50.0,
                crime_before=s.get("crimeSimilarAntes") or "Não sei",
                non_compliance=s.get("histDescumprimento") or "Não sei",
            )
        )

    return suspects


def get_evidences_for_bayes(tx, caso_id):
    query = """
    MATCH (c:Caso {id: $casoId})-[:TEM_EVIDENCIA]->(e:Evidencia)
    OPTIONAL MATCH (e)-[v:VINCULA]->(s:Suspeito)
    WITH e, collect({
        suspectId: s.id,
        pesoVinculo: v.pesoVinculo
    }) AS vinculos
    RETURN e {
        .id, .nome, .tipo, .status,
        .pesoCondicional, .dataColeta, .descricao
    } AS evidencia,
    vinculos
    ORDER BY e.criadoEm ASC
    """

    result = tx.run(query, casoId=caso_id)
    evidences = []

    for record in result:
        e = record["evidencia"]
        vinculos = record["vinculos"]
        peso_evidencia = float(e.get("pesoCondicional") or 0.5)

        for v in vinculos:
            if v["suspectId"] is None:
                continue

            peso_vinculo = float(v["pesoVinculo"] or 1.0)
            peso_final   = peso_evidencia * peso_vinculo

            evidences.append(
                Evidence(
                    id=f"{e['id']}_{v['suspectId']}",
                    name=e["nome"],
                    type=EvidenceType(e["tipo"]),
                    status=EvidenceStatus(e["status"]),
                    weight=peso_final,
                    suspect_ids=[v["suspectId"]],
                    date=str(e["dataColeta"]) if e.get("dataColeta") else "",
                    description=e.get("descricao") or "",
                )
            )

    return evidences

def save_bayes_results(tx, caso_id, ranking):
    query = """
    UNWIND $ranking AS r
    MATCH (s:Suspeito {id: r.suspect_id})
    SET s.probabilidadeAtual = r.probability_pct,
        s.posicaoRanking     = r.position,
        s.tendencia          = r.trend,
        s.atualizadoEm       = datetime()
    """
    tx.run(query, casoId=caso_id, ranking=ranking)