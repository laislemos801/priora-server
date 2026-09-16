from fastapi import HTTPException, status

from app.repositories.access_repository import get_user_role_for_case

READ_ROLES = {"Responsavel", "Editor", "Leitor"}
WRITE_ROLES = {"Responsavel", "Editor"}
OWNER_ROLES = {"Responsavel"}


def require_case_role(tx, user_id: str, caso_id: str, allowed_roles: set[str] = WRITE_ROLES) -> str:
    """
    Garante que `user_id` possui um dos papéis em `allowed_roles` no caso
    `caso_id`. Levanta 403 se não tiver acesso suficiente, 404 se o caso/
    vínculo não existir. Retorna o papel do usuário quando autorizado.

    Uso padrão:
      - leitura (qualquer papel):        allowed_roles=READ_ROLES
      - escrita (Editor/Responsavel):    allowed_roles=WRITE_ROLES (default)
      - ações restritas ao dono do caso: allowed_roles=OWNER_ROLES
    """
    role = get_user_role_for_case(tx, user_id, caso_id)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a este caso",
        )

    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seu papel neste caso não permite esta ação",
        )

    return role
