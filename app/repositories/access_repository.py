def invite_user_to_case(tx, email, caso_id, papel):
    query = """
    MATCH (u:Usuario {email: $email}),
          (c:Caso {id: $casoId})
    MERGE (u)-[r:TEM_ACESSO]->(c)
    SET r.papel = $papel,
        r.status = 'Pendente',
        r.convidadoEm = datetime()
    RETURN u.email AS email, r.papel AS papel, r.status AS status
    """
    result = tx.run(query,
        email=email,
        casoId=caso_id,
        papel=papel
    )
    record = result.single()
    if not record:
        raise Exception("Usuário ou Caso não encontrado")
    return record.data()


def accept_invite(tx, user_id, caso_id):
    query = """
    MATCH (u:Usuario {id: $userId})-[r:TEM_ACESSO]->(c:Caso {id: $casoId})
    SET r.status = 'Ativo'
    RETURN c.id AS casoId, r.status AS status
    """
    result = tx.run(query,
        userId=user_id,
        casoId=caso_id
    )
    record = result.single()
    if not record:
        raise Exception("Convite não encontrado")
    return record.data()


def list_case_users(tx, caso_id):
    query = """
    MATCH (u:Usuario)-[r:TEM_ACESSO]->(c:Caso {id: $casoId})
    RETURN u {
        .id, .email, .primeiroNome, .sobrenome
    } AS usuario,
    r.papel AS papel,
    r.status AS status
    """
    result = tx.run(query, casoId=caso_id)
    return [record.data() for record in result]