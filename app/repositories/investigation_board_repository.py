import json


def get_case_exists(tx, caso_id):
    query = """
    MATCH (c:Caso {id: $casoId})
    RETURN c.id AS id
    """
    result = tx.run(query, casoId=caso_id)
    return result.single() is not None


def get_board(tx, caso_id):
    """
    Retorna o JSON bruto (string) salvo em c.quadroInvestigativo, ou None se
    o caso não existir OU se o quadro ainda não tiver sido salvo nenhuma vez.
    """
    query = """
    MATCH (c:Caso {id: $casoId})
    RETURN c.quadroInvestigativo AS board
    """
    result = tx.run(query, casoId=caso_id)
    record = result.single()

    if record is None:
        return None  # caso não existe

    return record["board"]  # string JSON, ou None se nunca foi salvo


def save_board(tx, caso_id, nodes, edges):
    """
    Serializa nodes/edges como JSON e salva como propriedade do Caso.

    Guardamos como uma única string JSON (em vez de nós/relacionamentos reais)
    porque o quadro é um documento livre — o usuário pode criar quantas formas
    quiser, com qualquer texto/cor. Não precisamos consultar esses dados via
    Cypher (ex: "quais evidências este suspeito conecta"), então não compensa
    modelar como grafo por enquanto.
    """
    board_json = json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False)

    query = """
    MATCH (c:Caso {id: $casoId})
    SET c.quadroInvestigativo = $boardJson,
        c.atualizadoEm = datetime()
    RETURN c.id AS id
    """
    result = tx.run(query, casoId=caso_id, boardJson=board_json)
    record = result.single()

    if record is None:
        raise Exception("Caso não encontrado")

    return {"id": record["id"], "nodes": nodes, "edges": edges}
