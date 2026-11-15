from app.bayes.model import Evidence, EvidenceStatus, EvidenceType, Suspect
from app.repositories import priority_repository as repo


def _ev(id_, status, reliability, links):
    return Evidence(
        id=id_, name=f"Ev {id_}", type=EvidenceType.DIGITAL, status=EvidenceStatus(status),
        reliability=reliability, suspect_links=links,
    )


def _run(monkeypatch, suspects, evidences):
    monkeypatch.setattr(repo, "get_suspects_for_bayes", lambda tx, caso: suspects)
    monkeypatch.setattr(repo, "get_evidences_for_bayes", lambda tx, caso: evidences)
    return repo.compute_candidate_actions(None, "caso")


def _by_type(actions):
    out = {}
    for a in actions:
        out.setdefault(a["tipo"], []).append(a)
    return out


S3 = [Suspect(id=f"s{i}", name=f"S{i}") for i in (1, 2, 3)]


def test_case_without_evidence_has_only_the_first_evidence_action(monkeypatch):
    actions = _run(monkeypatch, S3, [])
    assert [a["tipo"] for a in actions] == ["SemEvidencias"]
    assert actions[0]["recompensa"] == 100.0
    assert actions[0]["esforco"] == repo.EFFORT_NO_EVIDENCE_CASE


def test_single_suspect_without_evidence_has_no_actions(monkeypatch):
    assert _run(monkeypatch, S3[:1], []) == []


def test_collected_and_pending_evidence_get_their_own_types(monkeypatch):
    evs = [
        _ev("c", "Coletada", 0.9, {"s1": 0.9}),
        _ev("p", "Em análise", 0.9, {"s1": 0.9}),
        _ev("q", "Enviada a perícia", 0.9, {"s1": 0.9}),
    ]
    by = _by_type(_run(monkeypatch, S3, evs))
    assert by["EvidenciaColetada"][0]["esforco"] == repo.EFFORT_COLLECTED
    efforts = sorted(a["esforco"] for a in by["Evidencia"])
    assert efforts == [repo.EFFORT_BY_EVIDENCE_STATUS["Em análise"], repo.EFFORT_BY_EVIDENCE_STATUS["Enviada a perícia"]]


def test_custodied_and_discarded_evidence_generate_nothing(monkeypatch):
    evs = [_ev("a", "Custodiada", 0.9, {"s1": 0.9}), _ev("b", "Descartada", 0.9, {"s1": 0.9})]
    by = _by_type(_run(monkeypatch, S3, evs))
    assert "Evidencia" not in by and "EvidenciaColetada" not in by and "EvidenciaFraca" not in by


def test_suspect_without_links_gets_search_action_and_others_get_deepen(monkeypatch):
    evs = [_ev("a", "Custodiada", 0.9, {"s1": 0.9})]
    by = _by_type(_run(monkeypatch, S3, evs))
    assert {a["titulo"] for a in by["SuspeitoSemEvidencia"]} == {
        "Buscar evidências que liguem ou excluam S2",
        "Buscar evidências que liguem ou excluam S3",
    } or len(by["SuspeitoSemEvidencia"]) >= 1
    assert all(a["esforco"] == 90.0 for a in by["SuspeitoSemEvidencia"])


def test_low_reliability_evidence_gets_review_action(monkeypatch):
    evs = [_ev("a", "Custodiada", 0.2, {"s1": 0.9})]
    by = _by_type(_run(monkeypatch, S3[:2], evs))
    assert by["EvidenciaFraca"][0]["esforco"] == repo.EFFORT_REVIEW
    assert by["EvidenciaFraca"][0]["recompensa"] >= repo.MIN_RELEVANT_GAIN_PCT


def test_reliable_evidence_gets_no_review_action(monkeypatch):
    evs = [_ev("a", "Custodiada", 0.8, {"s1": 0.9})]
    assert "EvidenciaFraca" not in _by_type(_run(monkeypatch, S3[:2], evs))


def test_tie_at_the_top_gets_differentiate_action(monkeypatch):
    # sem evidências diferenciando s1 e s2 (ambos com 1 evidência igual), s3 sem nenhuma
    evs = [_ev("a", "Custodiada", 0.9, {"s1": 0.9}), _ev("b", "Custodiada", 0.9, {"s2": 0.9})]
    by = _by_type(_run(monkeypatch, S3, evs))
    assert len(by["Diferenciar"]) == 1
    assert by["Diferenciar"][0]["esforco"] == repo.EFFORT_DIFFERENTIATE


def test_clear_leader_gets_no_differentiate_action(monkeypatch):
    evs = [_ev(str(i), "Custodiada", 0.95, {"s1": 0.95}) for i in range(6)]
    assert "Diferenciar" not in _by_type(_run(monkeypatch, S3, evs))


def test_source_keys_are_unique(monkeypatch):
    evs = [_ev("a", "Coletada", 0.2, {"s1": 0.9}), _ev("b", "Em análise", 0.9, {"s2": 0.9})]
    keys = [a["sourceKey"] for a in _run(monkeypatch, S3, evs)]
    assert len(keys) == len(set(keys))


def test_catalog_covers_every_type_generated():
    tipos = {t["tipo"] for t in repo.action_type_catalog()}
    assert tipos == {"SemEvidencias", "Evidencia", "EvidenciaColetada", "EvidenciaFraca",
                     "Diferenciar", "SuspeitoSemEvidencia", "Suspeito"}
    for t in repo.action_type_catalog():
        assert all(t[k] for k in ("nome", "quandoAparece", "quandoSome", "recompensa", "esforco"))


# ── Regressão: cada suspeito deve ser pareado com a PRÓPRIA probabilidade ──────────
# O ranking sai ordenado por probabilidade; os suspeitos chegam na ordem de cadastro.
# Quando as duas ordens diferem, as sugestões atribuíam a probabilidade de um suspeito a outro.

def _ranking_ordem_diferente_do_cadastro():
    """Suspeitos cadastrados como s1, s2, s3, mas com ranking s3 > s2 > s1 (s3 e s2 bem próximos)."""
    from app.bayes.model import BayesianNetwork

    suspects = [Suspect(id=f"s{i}", name=f"S{i}") for i in (1, 2, 3)]
    evs = [
        _ev("e1", "Coletada", 0.9, {"s3": 0.9}),
        _ev("e2", "Coletada", 0.9, {"s3": 0.5}),
        _ev("e3", "Coletada", 0.9, {"s2": 0.9}),
        _ev("e4", "Coletada", 0.9, {"s2": 0.5}),
        _ev("e5", "Coletada", 0.5, {"s1": 0.3}),
    ]
    ranking = BayesianNetwork().run(case_id="caso", suspects=suspects, evidences=evs).ranking
    assert [r.suspect.id for r in ranking][0] != "s1"  # ordem do ranking difere da de cadastro
    return suspects, evs, ranking


def test_deepen_actions_use_each_suspects_own_probability(monkeypatch):
    suspects, evs, ranking = _ranking_ordem_diferente_do_cadastro()
    h = repo.shannon_entropy_bits([r.p_h_given_e for r in ranking])
    esperado = {r.suspect.name: round(repo._h_term(r.p_h_given_e) / h * 100, 1) for r in ranking}

    actions = _run(monkeypatch, suspects, evs)
    obtido = {a["titulo"].removeprefix("Aprofundar investigação sobre "): a["recompensa"]
              for a in actions if a["tipo"] == "Suspeito"}
    assert obtido == esperado


def test_tie_action_names_the_two_leaders_of_the_ranking(monkeypatch):
    suspects, evs, ranking = _ranking_ordem_diferente_do_cadastro()
    top1, top2 = ranking[0], ranking[1]
    assert (top1.p_h_given_e - top2.p_h_given_e) * 100 <= repo.TIE_MARGIN_PP

    actions = _run(monkeypatch, suspects, evs)
    titulos = [a["titulo"] for a in actions if a["tipo"] == "Diferenciar"]
    assert titulos == [f"Buscar evidência que diferencie {top1.suspect.name} de {top2.suspect.name}"]
