from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from functools import reduce
from operator import mul
from typing import Optional


# ─── Enums ────────────────────────────────────────────────────────────────────

class EvidenceType(str, Enum):
    DIGITAL     = "Digital"
    DNA         = "DNA"
    DEPOIMENTO  = "Depoimento"
    DOCUMENTAL  = "Documental"
    FISICA      = "Física"
    AUDIOVISUAL = "Audiovisual"
    BIOLOGICA   = "Biológica"


class EvidenceStatus(str, Enum):
    COLETADA    = "Coletada"
    EM_ANALISE  = "Em análise"
    CUSTODIADA  = "Custodiada"
    DESCARTADA  = "Descartada"
    PERICIA = "Enviada a perícia"


class Trend(str, Enum):
    UP     = "Alta"
    DOWN   = "Baixa"
    STABLE = "Estável"


# ─── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class Evidence:
    """
    Representa uma evidência vinculada a um ou mais suspeitos.

    Attributes:
        weight: P(E|H) ∈ (0.0, 1.0) — quão incriminatória é esta evidência
                se o suspeito FOR culpado. Não pode ser 0 nem 1 exatos
                (evita colapso do produto).
    """
    id:           str
    name:         str
    type:         EvidenceType
    status:       EvidenceStatus
    weight:       float          # P(E|H) ∈ (0.0, 1.0)
    suspect_ids:  list[str]
    date:         str            = ""
    description:  str            = ""

    def __post_init__(self):
        if not (0.0 < self.weight < 1.0):
            raise ValueError(
                f"Evidência '{self.name}': weight deve estar em (0.0, 1.0) exclusivo, "
                f"recebido {self.weight}."
            )


@dataclass
class Suspect:
    id:                 str
    name:               str
    age:                int                 = 0
    behavior:           float               = 50.0
    aggressiveness:     float               = 50.0
    proximity:          float               = 50.0
    social_connections: float               = 50.0
    confession_level:   float               = 50.0
    crime_before:       str                 = "Não sei"
    non_compliance:     str                 = "Não sei"
    photo_url:          Optional[str]       = None


@dataclass
class SuspectResult:
    """
    Resultado bayesiano para um suspeito.

    Attributes:
        p_e_given_h:     P(E|Hᵢ) — verossimilhança (produto dos pesos).
                         Será 1.0 se o suspeito não tiver evidências vinculadas.
        numerator:       P(E|Hᵢ) · P(Hᵢ) — antes da normalização global.
        p_h_given_e:     P(Hᵢ|E) — posterior normalizado globalmente ∈ [0,1].
                         Garante Σ = 1.0 entre todos os suspeitos.
    """
    suspect:             Suspect
    prior:               float
    p_e_given_h:         float
    numerator:           float
    p_h_given_e:         float
    probability_pct:     float
    uncertainty_pct:     float
    position:            int                = 0
    trend:               Trend              = Trend.STABLE
    linked_evidences:    list[Evidence]     = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "suspect_id":          self.suspect.id,
            "suspect_name":        self.suspect.name,
            "position":            self.position,
            "prior":               round(self.prior, 6),
            "p_e_given_h":         round(self.p_e_given_h, 6),
            "numerator":           round(self.numerator, 6),
            "p_h_given_e":         round(self.p_h_given_e, 6),
            "probability_pct":     round(self.probability_pct, 2),
            "uncertainty_pct":     round(self.uncertainty_pct, 2),
            "trend":               self.trend.value,
            "linked_evidence_ids": [e.id for e in self.linked_evidences],
        }


@dataclass
class BayesianAnalysisResult:
    case_id:           str
    version:           int
    n_suspects:        int
    n_evidences:       int
    ranking:           list[SuspectResult]
    case_uncertainty:  float
    avg_uncertainty:   float

    def sum_check(self) -> float:
        """Deve retornar 1.0 (ou muito próximo). Use para validação."""
        return sum(r.p_h_given_e for r in self.ranking)

    def to_dict(self) -> dict:
        return {
            "case_id":          self.case_id,
            "version":          self.version,
            "n_suspects":       self.n_suspects,
            "n_evidences":      self.n_evidences,
            "case_uncertainty": round(self.case_uncertainty, 2),
            "avg_uncertainty":  round(self.avg_uncertainty, 2),
            "sum_check":        round(self.sum_check(), 8),   # deve ser 1.0
            "ranking":          [r.to_dict() for r in self.ranking],
        }


# ─── Engine ───────────────────────────────────────────────────────────────────

import math
from typing import List, Optional


class BayesianNetwork:
    """
    PRIORA v2 — Log-Bayes com Likelihood Ratio (LR)

    Melhorias:
    - estabilidade numérica (log-space)
    - evidência comparativa (LR)
    - elimina viés de "suspeito vazio"
    """

    def __init__(self, epsilon: float = 1e-6):
        """
        epsilon evita log(0) e define piso mínimo para probabilidades.
        """
        self.epsilon = epsilon

    # ──────────────────────────────────────────────────────────────
    # CORE
    # ──────────────────────────────────────────────────────────────

    def run(
      self,
      case_id: str,
      suspects: List[Suspect],
      evidences: List[Evidence],
      version: int = 2,
      previous_results: Optional[List[SuspectResult]] = None,
    ) -> BayesianAnalysisResult:

        if not suspects:
            raise ValueError("A lista de suspeitos não pode estar vazia.")

        n = len(suspects)
        prior = 1.0 / n

        prev_index = {}
        if previous_results:
            prev_index = {r.suspect.id: r.probability_pct for r in previous_results}

        intermediates = []

        for suspect in suspects:
            linked = [e for e in evidences if suspect.id in e.suspect_ids]

            log_score = self._log_likelihood_ratio(suspect, evidences, suspects)

            intermediates.append((suspect, linked, log_score))

        max_log = max(score for _, _, score in intermediates)

        weights = []
        for suspect, linked, log_score in intermediates:
            weight = math.exp(log_score - max_log) * prior
            weights.append((suspect, linked, log_score, weight))

        denominator = sum(w for _, _, _, w in weights) or 1.0

        results = []

        for suspect, linked, log_score, weight in weights:
            posterior = weight / denominator
            pct = posterior * 100
            uncertainty = 100 - pct

            trend = self._compute_trend(suspect.id, pct, prev_index)

            bayes_numerator = math.exp(log_score) * prior

            results.append(SuspectResult(
                suspect=suspect,
                prior=prior,
                p_e_given_h=math.exp(log_score),
                numerator=bayes_numerator,
                p_h_given_e=posterior,
                probability_pct=pct,
                uncertainty_pct=uncertainty,
                trend=trend,
                linked_evidences=linked,
            ))

        results.sort(key=lambda r: r.p_h_given_e, reverse=True)

        for i, r in enumerate(results):
            r.position = i + 1

        top = results[0]
        avg_uncertainty = sum(r.uncertainty_pct for r in results) / n

        return BayesianAnalysisResult(
            case_id=case_id,
            version=version,
            n_suspects=n,
            n_evidences=len(evidences),
            ranking=results,
            case_uncertainty=top.uncertainty_pct,
            avg_uncertainty=avg_uncertainty,
        )
    
    def _evidence_contribution(self, suspect: Suspect, evidence: Evidence, all_suspects: list[Suspect]) -> float:
        """
        Mede quanto a evidência suporta ESTE suspeito em relação aos outros.
        """

        if suspect.id not in evidence.suspect_ids:
            # não favorecido diretamente → ainda pode ser levemente afetado
            return 1.0 - (evidence.weight * 0.2)

        # suspeitos que também recebem essa evidência
        competitors = len(evidence.suspect_ids)

        # quanto mais compartilhada a evidência, menor o impacto
        share_factor = 1.0 / competitors

        return 1.0 + (evidence.weight * share_factor)

    # ──────────────────────────────────────────────────────────────
    # LIKELIHOOD RATIO MODEL
    # ──────────────────────────────────────────────────────────────

    def _log_likelihood_ratio(self, suspect, evidences, all_suspects):
        score = 0.0

        for e in evidences:
            contrib = self._evidence_contribution(suspect, e, all_suspects)
            score += math.log(self._clamp(contrib))

        return score

    def _baseline_probability(self, evidence: Evidence) -> float:
        """
        P(E|¬H)

        IMPORTANTE:
        isso define o quanto a evidência é "comum no mundo".

        Ajuste simples e seguro:
        - evidências fortes são raras no não-crime
        """

        # heurística simples e estável
        return self._clamp(1.0 - evidence.weight)

    def _clamp(self, x: float) -> float:
        return min(max(x, self.epsilon), 1.0 - self.epsilon)

    # ──────────────────────────────────────────────────────────────
    # TREND (inalterado)
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _compute_trend(
        suspect_id: str,
        current_pct: float,
        prev_index: dict[str, float],
        threshold: float = 0.5,
    ) -> Trend:

        if suspect_id not in prev_index:
            return Trend.STABLE

        delta = current_pct - prev_index[suspect_id]

        if delta > threshold:
            return Trend.UP
        if delta < -threshold:
            return Trend.DOWN
        return Trend.STABLE


# ─── Testes / Demonstração ────────────────────────────────────────────────────

if __name__ == "__main__":

    network = BayesianNetwork()
    SEP = "─" * 76

    # ══════════════════════════════════════════════════════════════════════════
    # TESTE 1 — Caso base: 3 suspeitos SEM evidências → deve dar 33.3% cada
    # ══════════════════════════════════════════════════════════════════════════
    print(f"\n{'═' * 76}")
    print("  TESTE 1 — Caso base: 3 suspeitos sem evidências")
    print(f"{'═' * 76}")

    s_base = [
        Suspect(id="a", name="Alice"),
        Suspect(id="b", name="Bob"),
        Suspect(id="c", name="Carlos"),
    ]
    r_base = network.run("caso-base", s_base, [], version=1)

    for r in r_base.ranking:
        print(f"  {r.suspect.name:<10}  {r.probability_pct:>6.2f}%")
    print(f"  Soma total: {r_base.sum_check():.6f}  (deve ser 1.000000)")

    # ══════════════════════════════════════════════════════════════════════════
    # TESTE 2 — Uma evidência forte vincula só Alice → redistribui
    # ══════════════════════════════════════════════════════════════════════════
    print(f"\n{'═' * 76}")
    print("  TESTE 2 — Evidência forte (0.90) vinculada só a Alice")
    print(f"{'═' * 76}")

    ev_forte = [Evidence(id="e1", name="DNA forte", type=EvidenceType.DNA,
                         status=EvidenceStatus.COLETADA, weight=0.90,
                         suspect_ids=["a"])]
    r_ev = network.run("caso-ev", s_base, ev_forte, version=1)

    for r in r_ev.ranking:
        ev_names = ", ".join(e.name for e in r.linked_evidences) or "nenhuma"
        print(f"  {r.suspect.name:<10}  {r.probability_pct:>6.2f}%   [{ev_names}]")
    print(f"  Soma total: {r_ev.sum_check():.6f}  (deve ser 1.000000)")

    # ══════════════════════════════════════════════════════════════════════════
    # TESTE 3 — Caso Alpha original (7 suspeitos, 7 evidências)
    # ══════════════════════════════════════════════════════════════════════════
    print(f"\n{'═' * 76}")
    print("  TESTE 3 — Caso Alpha (7 suspeitos, 7 evidências)")
    print(f"{'═' * 76}")

    suspects = [
        Suspect(id="s1", name="Elvin Bond",    age=34),
        Suspect(id="s2", name="Emma Berger",   age=28),
        Suspect(id="s3", name="Koen Chegg",    age=41),
        Suspect(id="s4", name="Kay Finley",    age=25),
        Suspect(id="s5", name="Nicholas Roy",  age=37),
        Suspect(id="s6", name="Louis Mason",   age=30),
        Suspect(id="s7", name="Boston Thomas", age=45),
    ]

    evidences = [
        Evidence(id="e1", name="Digital no local", type=EvidenceType.DIGITAL,    status=EvidenceStatus.COLETADA,   weight=0.75, suspect_ids=["s1","s2"]),
        Evidence(id="e2", name="DNA amostra #1",   type=EvidenceType.DNA,        status=EvidenceStatus.EM_ANALISE, weight=0.80, suspect_ids=["s1","s3"]),
        Evidence(id="e3", name="Depoimento teste", type=EvidenceType.DEPOIMENTO, status=EvidenceStatus.CUSTODIADA, weight=0.32, suspect_ids=["s1"]),
        Evidence(id="e4", name="Digital entrada",  type=EvidenceType.DIGITAL,    status=EvidenceStatus.EM_ANALISE, weight=0.50, suspect_ids=["s2","s4"]),
        Evidence(id="e5", name="DNA amostra #2",   type=EvidenceType.DNA,        status=EvidenceStatus.CUSTODIADA, weight=0.60, suspect_ids=["s3"]),
        Evidence(id="e6", name="Depoimento B",     type=EvidenceType.DEPOIMENTO, status=EvidenceStatus.CUSTODIADA, weight=0.25, suspect_ids=["s5","s6"]),
        Evidence(id="e7", name="DNA amostra #3",   type=EvidenceType.DNA,        status=EvidenceStatus.COLETADA,   weight=0.15, suspect_ids=["s7"]),
    ]

    previous_mock = [
        SuspectResult(suspect=suspects[0], prior=1/7, p_e_given_h=0, numerator=0, p_h_given_e=0, probability_pct=66.0, uncertainty_pct=34.0),
        SuspectResult(suspect=suspects[1], prior=1/7, p_e_given_h=0, numerator=0, p_h_given_e=0, probability_pct=62.0, uncertainty_pct=38.0),
        SuspectResult(suspect=suspects[2], prior=1/7, p_e_given_h=0, numerator=0, p_h_given_e=0, probability_pct=40.0, uncertainty_pct=60.0),
        SuspectResult(suspect=suspects[3], prior=1/7, p_e_given_h=0, numerator=0, p_h_given_e=0, probability_pct=20.0, uncertainty_pct=80.0),
        SuspectResult(suspect=suspects[4], prior=1/7, p_e_given_h=0, numerator=0, p_h_given_e=0, probability_pct=15.0, uncertainty_pct=85.0),
        SuspectResult(suspect=suspects[5], prior=1/7, p_e_given_h=0, numerator=0, p_h_given_e=0, probability_pct=12.0, uncertainty_pct=88.0),
        SuspectResult(suspect=suspects[6], prior=1/7, p_e_given_h=0, numerator=0, p_h_given_e=0, probability_pct=3.0,  uncertainty_pct=97.0),
    ]

    result = network.run("caso-alpha", suspects, evidences, version=2, previous_results=previous_mock)

    print(f"\n  Suspeitos: {result.n_suspects}  |  Evidências: {result.n_evidences}")
    print(f"  Incerteza do caso : {result.case_uncertainty:.2f}%")
    print(f"  Incerteza média   : {result.avg_uncertainty:.2f}%")
    print(f"  Soma das posteriors: {result.sum_check():.6f}  (deve ser 1.000000)\n")

    print(f"  {'#':<4} {'Nome':<18} {'P(E|H)':>9} {'P(H|E)':>9} {'Prob%':>7} {'Tend.':>7}   Evidências")
    print(f"  {SEP}")

    for r in result.ranking:
        ev_names  = ", ".join(e.name for e in r.linked_evidences) or "nenhuma"
        trend_sym = {"Alta": "↑", "Baixa": "↓", "Estável": "—"}[r.trend.value]
        print(
            f"  {r.position:<4} {r.suspect.name:<18} "
            f"{r.p_e_given_h:>9.4f} {r.p_h_given_e:>9.4f} "
            f"{r.probability_pct:>6.1f}% {trend_sym:>7}   {ev_names}"
        )

    print(f"\n  Fórmula detalhada — {result.ranking[0].suspect.name} (#1):")
    top = result.ranking[0]
    denom = sum(r.numerator for r in result.ranking)
    print(f"    Prior P(H)       = 1/{result.n_suspects} = {top.prior:.6f}")
    print(f"    P(E|H)           = {top.p_e_given_h:.6f}  (produto dos pesos das evidências vinculadas)")
    print(f"    Numerador        = P(E|H) · P(H) = {top.numerator:.6f}")
    print(f"    Denominador      = Σⱼ[P(E|Hⱼ)·P(Hⱼ)] = {denom:.6f}  (soma global)")
    print(f"    P(H|E)           = {top.p_h_given_e:.6f}  ({top.probability_pct:.2f}%)")
    print()