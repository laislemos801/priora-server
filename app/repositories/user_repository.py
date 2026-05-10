def create_user(tx, email, primeiro_nome, sobrenome, senha_hash):
    query = """
    CREATE (u:Usuario {
        id: randomUUID(),
        email: $email,
        primeiroNome: $primeiro_nome,
        sobrenome: $sobrenome,
        senhaHash: $senha_hash,
        criadoEm: datetime(),
        ultimoAcesso: datetime()
    })
    RETURN u {
        .id, .email, .primeiroNome, .sobrenome, .criadoEm
    } AS user
    """
    result = tx.run(query,
        email=email,
        primeiro_nome=primeiro_nome,
        sobrenome=sobrenome,
        senha_hash=senha_hash
    )
    return result.single()["user"]


def login_user(tx, email):
    query = """
    MATCH (u:Usuario {email: $email})
    SET u.ultimoAcesso = datetime()
    RETURN u {
        .id,
        .email,
        .primeiroNome,
        .sobrenome,
        .fotoUrl,
        .senhaHash
    } AS user
    """
    result = tx.run(query, email=email)
    record = result.single()

    return record["user"] if record else None


def set_recovery_token(tx, email, token):
    query = """
    MATCH (u:Usuario {email: $email})
    SET u.tokenRecuperacao = $token,
        u.tokenExpiracaoEm = datetime() + duration({minutes: 30})
    RETURN u.email AS email
    """
    result = tx.run(query, email=email, token=token)
    return result.single()


def reset_password(tx, token, nova_senha_hash):
    query = """
    MATCH (u:Usuario {tokenRecuperacao: $token})
    WHERE u.tokenExpiracaoEm > datetime()
    SET u.senhaHash = $novaSenhaHash,
        u.atualizadoEm = datetime()
    REMOVE u.tokenRecuperacao, u.tokenExpiracaoEm
    RETURN u.id AS id
    """
    result = tx.run(query, token=token, novaSenhaHash=nova_senha_hash)
    return result.single()