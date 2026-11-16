import asyncio

import pytest
from fastapi import HTTPException

import app.services.user_service as us


def test_sem_variavel_cadastro_aberto(monkeypatch):
    monkeypatch.delenv("REGISTRATION_CODE", raising=False)
    assert us.registration_code_ok(None)


def test_com_variavel_exige_codigo(monkeypatch):
    monkeypatch.setenv("REGISTRATION_CODE", "segredo")
    assert us.registration_code_ok(" segredo ")
    assert not us.registration_code_ok("errado")
    assert not us.registration_code_ok(None)


def test_cadastro_bloqueado_sem_codigo(monkeypatch):
    monkeypatch.setenv("REGISTRATION_CODE", "segredo")
    monkeypatch.setattr(us, "get_session", lambda: (_ for _ in ()).throw(AssertionError("não deve tocar no banco")))
    with pytest.raises(HTTPException) as e:
        asyncio.run(us.create_user_service("a@b.com", "A", "B", "Senha#123", "errado"))
    assert e.value.status_code == 403
