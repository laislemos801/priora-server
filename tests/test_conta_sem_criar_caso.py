import pytest
from fastapi import HTTPException

from app.repositories import user_repository
from app.services import case_service


class _Tx:
    """Transação falsa: devolve sempre o mesmo registro."""

    def __init__(self, registro):
        self._registro = registro

    def run(self, *_args, **_kwargs):
        return self

    def single(self):
        return self._registro


class _Sessao:
    def __enter__(self):
        return object()

    def __exit__(self, *_args):
        return False


def test_conta_com_flag_false_nao_cria_caso():
    assert user_repository.can_create_case(_Tx({"podeCriarCaso": False}), "u1") is False


def test_conta_com_flag_true_ou_sem_flag_cria_caso():
    assert user_repository.can_create_case(_Tx({"podeCriarCaso": True}), "u1") is True
    # contas antigas não têm a propriedade
    assert user_repository.can_create_case(_Tx({"podeCriarCaso": None}), "u1") is True


def test_servico_recusa_criacao_para_conta_bloqueada(monkeypatch):
    criados = []
    monkeypatch.setattr(case_service, "get_session", lambda: _Sessao())
    monkeypatch.setattr(case_service, "can_create_case", lambda tx, uid: False)
    monkeypatch.setattr(case_service, "create_case", lambda tx, uid, data: criados.append(data))

    with pytest.raises(HTTPException) as erro:
        case_service.create_case_service("u1", {"nome": "x"})

    assert erro.value.status_code == 403
    assert criados == []


def test_servico_cria_caso_para_conta_liberada(monkeypatch):
    criados = []
    monkeypatch.setattr(case_service, "get_session", lambda: _Sessao())
    monkeypatch.setattr(case_service, "can_create_case", lambda tx, uid: True)
    monkeypatch.setattr(case_service, "create_case", lambda tx, uid, data: criados.append(data) or {"id": "c1"})

    assert case_service.create_case_service("u1", {"nome": "x"}) == {"id": "c1"}
    assert criados == [{"nome": "x"}]
