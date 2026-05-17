"""
PRIORA — Rede Bayesiana para Priorização de Suspeitos
======================================================
Implementa inferência bayesiana (Naive Bayes) para calcular
P(H|E): a probabilidade de um suspeito ser o culpado dado
o conjunto de evidências vinculadas a ele.

Fórmula (Teorema de Bayes):
    P(H|E) = P(E|H) · P(H)
             ─────────────────────────────────────────
             P(E|H) · P(H)  +  P(E|¬H) · P(¬H)

Onde:
    P(H)      = prior uniforme = 1 / n_suspeitos
    P(E|H)    = produto dos pesos condicionais das evidências vinculadas
    P(E|¬H)   = produto dos complementos (1 - peso) das mesmas evidências
    P(H|E)    = probabilidade posterior (resultado final)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from functools import reduce
from operator import mul
from typing import Optional
import math


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
        id:             Identificador único (UUID).
        name:           Nome descritivo da evidência.
        type:           Tipo (Digital, DNA, Depoimento, etc.).
        status:         Status atual da evidência.
        weight:         Peso condicional P(E|H) ∈ [0.0, 1.0].
                        Representa o quão incriminatória é esta evidência
                        quando o suspeito É culpado.
        suspect_ids:    Lista de IDs dos suspeitos vinculados.
        date:           Data de coleta (ISO 8601: "YYYY-MM-DD").
        description:    Descrição livre.
    """
    id:           str
    name:         str
    type:         EvidenceType
    status:       EvidenceStatus
    weight:       float          # P(E|H) ∈ [0.0, 1.0]
    suspect_ids:  list[str]
    date:         str            = ""
    description:  str            = ""

    def __post_init__(self):
        if not (0.0 <= self.weight <= 1.0):
            raise ValueError(
                f"Evidência '{self.name}': weight deve estar em [0.0, 1.0], "
                f"recebido {self.weight}."
            )


@dataclass
class Suspect:
    """
    Representa um suspeito com perfil comportamental.

    Attributes:
        id:                  Identificador único (UUID).
        name:                Nome completo.
        age:                 Idade em anos.
        behavior:            Comportamento [0–100].
        aggressiveness:      Agressividade [0–100].
        proximity:           Proximidade com vítima/local [0–100].
        social_connections:  Conexões sociais suspeitas [0–100].
        confession_level:    Nível de indício de confissão [0–100].
        crime_before:        Crime similar anterior ("Sim"/"Não sei"/"Não").
        non_compliance:      Histórico de descumprimento ("Sim"/"Não sei"/"Não").
        photo_url:           URL opcional da foto.
    """
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
    Resultado bayesiano para um suspeito após a inferência.

    Attributes:
        suspect:            Dados originais do suspeito.
        prior:              P(H) — probabilidade a priori.
        p_e_given_h:        P(E|H) — verossimilhança das evidências.
        p_e_given_not_h:    P(E|¬H) — complemento normalizado.
        numerator:          P(E|H) · P(H).
        denominator:        P(E|H)·P(H) + P(E|¬H)·P(¬H).
        p_h_given_e:        P(H|E) — probabilidade posterior ∈ [0, 1].
        probability_pct:    P(H|E) × 100 — exibição em percentual.
        uncertainty_pct:    100 − probability_pct — incerteza.
        position:           Posição no ranking (1 = mais provável).
        trend:              Tendência vs. análise anterior.
        linked_evidences:   Evidências vinculadas a este suspeito.
    """
    suspect:             Suspect
    prior:               float
    p_e_given_h:         float
    p_e_given_not_h:     float
    numerator:           float
    denominator:         float
    p_h_given_e:         float
    probability_pct:     float
    uncertainty_pct:     float
    position:            int                = 0
    trend:               Trend              = Trend.STABLE
    linked_evidences:    list[Evidence]     = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serializa para dict (pronto para JSON / Neo4j)."""
        return {
            "suspect_id":        self.suspect.id,
            "suspect_name":      self.suspect.name,
            "position":          self.position,
            "prior":             round(self.prior, 6),
            "p_e_given_h":       round(self.p_e_given_h, 6),
            "p_e_given_not_h":   round(self.p_e_given_not_h, 6),
            "numerator":         round(self.numerator, 6),
            "denominator":       round(self.denominator, 6),
            "p_h_given_e":       round(self.p_h_given_e, 6),
            "probability_pct":   round(self.probability_pct, 2),
            "uncertainty_pct":   round(self.uncertainty_pct, 2),
            "trend":             self.trend.value,
            "linked_evidence_ids": [e.id for e in self.linked_evidences],
        }


@dataclass
class BayesianAnalysisResult:
    """
    Resultado completo de uma execução da rede bayesiana para um caso.

    Attributes:
        case_id:            ID do caso investigado.
        version:            Número sequencial da análise.
        n_suspects:         Total de suspeitos avaliados.
        n_evidences:        Total de evidências consideradas.
        ranking:            Lista ordenada de SuspectResult (posição 1 = topo).
        case_uncertainty:   Incerteza do caso = incerteza do suspeito #1.
        avg_uncertainty:    Média de incerteza entre todos os suspeitos.
    """
    case_id:           str
    version:           int
    n_suspects:        int
    n_evidences:       int
    ranking:           list[SuspectResult]
    case_uncertainty:  float
    avg_uncertainty:   float

    def to_dict(self) -> dict:
        return {
            "case_id":          self.case_id,
            "version":          self.version,
            "n_suspects":       self.n_suspects,
            "n_evidences":      self.n_evidences,
            "case_uncertainty": round(self.case_uncertainty, 2),
            "avg_uncertainty":  round(self.avg_uncertainty, 2),
            "ranking":          [r.to_dict() for r in self.ranking],
        }


# ─── Engine ───────────────────────────────────────────────────────────────────

class BayesianNetwork:
    """
    Motor de inferência bayesiana do sistema PRIORA.

    Modelo: Naive Bayes com prior uniforme.
    Cada evidência é tratada como condicionalmente independente dado H.

    Uso:
        network = BayesianNetwork()
        result  = network.run(case_id, version, suspects, evidences)
        print(result.to_dict())
    """

    # Peso fraco para suspeitos sem evidências vinculadas,
    # evitando P(E|H) = 0 absoluto (suavização de Laplace simplificada).
    _WEAK_PRIOR_WEIGHT: float = 0.001

    def run(
        self,
        case_id:            str,
        suspects:           list[Suspect],
        evidences:          list[Evidence],
        version:            int = 1,
        previous_results:   Optional[list[SuspectResult]] = None,
    ) -> BayesianAnalysisResult:
        """
        Executa a inferência bayesiana para todos os suspeitos do caso.

        Args:
            case_id:          ID do caso no Neo4j.
            suspects:         Lista de Suspect do caso.
            evidences:        Lista de Evidence do caso (todos os tipos).
            version:          Número sequencial desta análise.
            previous_results: Resultados da análise anterior (para calcular tendência).

        Returns:
            BayesianAnalysisResult com ranking completo e métricas do caso.

        Raises:
            ValueError: Se suspects ou evidences estiverem vazios.
        """
        if not suspects:
            raise ValueError("A lista de suspeitos não pode estar vazia.")

        n = len(suspects)
        prior = 1.0 / n

        # Índice de resultados anteriores para cálculo de tendência
        prev_index: dict[str, float] = {}
        if previous_results:
            prev_index = {r.suspect.id: r.probability_pct for r in previous_results}

        results: list[SuspectResult] = []

        for suspect in suspects:
            linked = [e for e in evidences if suspect.id in e.suspect_ids]
            result = self._compute_posterior(suspect, linked, prior)
            result.trend = self._compute_trend(
                suspect.id, result.probability_pct, prev_index
            )
            results.append(result)

        # Ordenar por P(H|E) decrescente e atribuir posições
        results.sort(key=lambda r: r.p_h_given_e, reverse=True)
        for i, r in enumerate(results):
            r.position = i + 1

        # Métricas do caso
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

    # ── Private ───────────────────────────────────────────────────────────────

    def _compute_posterior(
        self,
        suspect:  Suspect,
        linked:   list[Evidence],
        prior:    float,
    ) -> SuspectResult:
        """
        Calcula P(H|E) para um único suspeito.

        P(E|H)   = ∏ weight_i          para cada evidência vinculada
        P(E|¬H)  = ∏ (1 - weight_i)   para cada evidência vinculada
        """
        if linked:
            p_e_given_h     = reduce(mul, (e.weight for e in linked), 1.0)
            p_e_given_not_h = reduce(mul, (1.0 - e.weight for e in linked), 1.0)
        else:
            # Suavização: suspeito sem evidências recebe prior muito fraco
            p_e_given_h     = self._WEAK_PRIOR_WEIGHT
            p_e_given_not_h = 1.0 - self._WEAK_PRIOR_WEIGHT

        numerator   = p_e_given_h * prior
        denominator = numerator + p_e_given_not_h * (1.0 - prior)

        p_h_given_e = numerator / denominator if denominator > 0 else 0.0

        probability_pct = p_h_given_e * 100.0
        uncertainty_pct = 100.0 - probability_pct

        return SuspectResult(
            suspect=suspect,
            prior=prior,
            p_e_given_h=p_e_given_h,
            p_e_given_not_h=p_e_given_not_h,
            numerator=numerator,
            denominator=denominator,
            p_h_given_e=p_h_given_e,
            probability_pct=probability_pct,
            uncertainty_pct=uncertainty_pct,
            linked_evidences=linked,
        )

    @staticmethod
    def _compute_trend(
        suspect_id:      str,
        current_pct:     float,
        prev_index:      dict[str, float],
        threshold:       float = 0.5,
    ) -> Trend:
        """
        Compara probabilidade atual com a análise anterior.

        Args:
            threshold: Variação mínima (em p.p.) para considerar mudança.
        """
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

    # Suspeitos do Caso Alpha (baseado nos protótipos do PRIORA)
    suspects = [
        Suspect(id="s1", name="Elvin Bond",    age=34, behavior=76, aggressiveness=45, proximity=76, social_connections=45, confession_level=76, crime_before="Sim",     non_compliance="Sim"),
        Suspect(id="s2", name="Emma Berger",   age=28, behavior=55, aggressiveness=60, proximity=50, social_connections=70, confession_level=30, crime_before="Não sei", non_compliance="Não"),
        Suspect(id="s3", name="Koen Chegg",    age=41, behavior=40, aggressiveness=80, proximity=60, social_connections=30, confession_level=20, crime_before="Sim",     non_compliance="Sim"),
        Suspect(id="s4", name="Kay Finley",    age=25, behavior=30, aggressiveness=20, proximity=45, social_connections=55, confession_level=10, crime_before="Não",     non_compliance="Não"),
        Suspect(id="s5", name="Nicholas Roy",  age=37, behavior=60, aggressiveness=35, proximity=30, social_connections=40, confession_level=50, crime_before="Não sei", non_compliance="Não sei"),
        Suspect(id="s6", name="Louis Mason",   age=30, behavior=25, aggressiveness=15, proximity=20, social_connections=25, confession_level=15, crime_before="Não",     non_compliance="Não"),
        Suspect(id="s7", name="Boston Thomas", age=45, behavior=15, aggressiveness=10, proximity=10, social_connections=15, confession_level=5,  crime_before="Não",     non_compliance="Não"),
    ]

    # Evidências com pesos condicionais (peso = P(E|H) do protótipo)
    evidences = [
        Evidence(id="e1", name="Digital no local", type=EvidenceType.DIGITAL,    status=EvidenceStatus.COLETADA,   weight=0.75, suspect_ids=["s1", "s2"], date="2025-04-24"),
        Evidence(id="e2", name="DNA amostra #1",   type=EvidenceType.DNA,        status=EvidenceStatus.EM_ANALISE, weight=0.80, suspect_ids=["s1", "s3"], date="2025-04-24"),
        Evidence(id="e3", name="Depoimento teste", type=EvidenceType.DEPOIMENTO, status=EvidenceStatus.CUSTODIADA, weight=0.32, suspect_ids=["s1"],       date="2025-04-24"),
        Evidence(id="e4", name="Digital entrada",  type=EvidenceType.DIGITAL,    status=EvidenceStatus.EM_ANALISE, weight=0.50, suspect_ids=["s2", "s4"], date="2025-04-24"),
        Evidence(id="e5", name="DNA amostra #2",   type=EvidenceType.DNA,        status=EvidenceStatus.CUSTODIADA, weight=0.60, suspect_ids=["s3"],       date="2025-04-24"),
        Evidence(id="e6", name="Depoimento B",     type=EvidenceType.DEPOIMENTO, status=EvidenceStatus.CUSTODIADA, weight=0.25, suspect_ids=["s5", "s6"], date="2025-04-24"),
        Evidence(id="e7", name="DNA amostra #3",   type=EvidenceType.DNA,        status=EvidenceStatus.COLETADA,   weight=0.15, suspect_ids=["s7"],       date="2025-04-24"),
    ]

    # Simular análise anterior (para calcular tendência)
    previous_mock = [
        SuspectResult(suspect=suspects[0], prior=1/7, p_e_given_h=0, p_e_given_not_h=0, numerator=0, denominator=0, p_h_given_e=0, probability_pct=66.0, uncertainty_pct=34.0),
        SuspectResult(suspect=suspects[1], prior=1/7, p_e_given_h=0, p_e_given_not_h=0, numerator=0, denominator=0, p_h_given_e=0, probability_pct=62.0, uncertainty_pct=38.0),
        SuspectResult(suspect=suspects[2], prior=1/7, p_e_given_h=0, p_e_given_not_h=0, numerator=0, denominator=0, p_h_given_e=0, probability_pct=40.0, uncertainty_pct=60.0),
        SuspectResult(suspect=suspects[3], prior=1/7, p_e_given_h=0, p_e_given_not_h=0, numerator=0, denominator=0, p_h_given_e=0, probability_pct=20.0, uncertainty_pct=80.0),
        SuspectResult(suspect=suspects[4], prior=1/7, p_e_given_h=0, p_e_given_not_h=0, numerator=0, denominator=0, p_h_given_e=0, probability_pct=15.0, uncertainty_pct=85.0),
        SuspectResult(suspect=suspects[5], prior=1/7, p_e_given_h=0, p_e_given_not_h=0, numerator=0, denominator=0, p_h_given_e=0, probability_pct=12.0, uncertainty_pct=88.0),
        SuspectResult(suspect=suspects[6], prior=1/7, p_e_given_h=0, p_e_given_not_h=0, numerator=0, denominator=0, p_h_given_e=0, probability_pct=3.0,  uncertainty_pct=97.0),
    ]

    # ── Executar ──────────────────────────────────────────────────────────────
    network = BayesianNetwork()
    result  = network.run(
        case_id="caso-alpha-uuid",
        suspects=suspects,
        evidences=evidences,
        version=2,
        previous_results=previous_mock,
    )

    # ── Exibir resultado ──────────────────────────────────────────────────────
    SEP = "─" * 72

    print(f"\n{'═' * 72}")
    print(f"  PRIORA · Rede Bayesiana · Caso: {result.case_id}")
    print(f"  Versão da análise : {result.version}")
    print(f"  Suspeitos         : {result.n_suspects}")
    print(f"  Evidências        : {result.n_evidences}")
    print(f"  Incerteza do caso : {result.case_uncertainty:.2f}%")
    print(f"  Incerteza média   : {result.avg_uncertainty:.2f}%")
    print(f"{'═' * 72}\n")

    print(f"  {'#':<4} {'Nome':<18} {'P(H|E)':>8} {'Prob%':>7} {'Incert%':>8} {'Tend.':>8}   Evidências")
    print(f"  {SEP}")

    for r in result.ranking:
        ev_names = ", ".join(e.name for e in r.linked_evidences) or "nenhuma"
        trend_sym = {"Alta": "↑", "Baixa": "↓", "Estável": "—"}[r.trend.value]
        print(
            f"  {r.position:<4} {r.suspect.name:<18} "
            f"{r.p_h_given_e:>8.4f} {r.probability_pct:>6.1f}% "
            f"{r.uncertainty_pct:>7.1f}% {trend_sym:>8}   {ev_names}"
        )

    print(f"\n  {SEP}")
    print(f"\n  Fórmula detalhada — {result.ranking[0].suspect.name} (posição #1):")
    top = result.ranking[0]
    print(f"    Prior P(H)       = 1/{result.n_suspects} = {top.prior:.6f}")
    print(f"    P(E|H)           = {top.p_e_given_h:.6f}  (produto dos pesos)")
    print(f"    P(E|¬H)          = {top.p_e_given_not_h:.6f}  (produto dos complementos)")
    print(f"    Numerador        = {top.numerator:.6f}")
    print(f"    Denominador      = {top.denominator:.6f}")
    print(f"    P(H|E)           = {top.p_h_given_e:.6f}  ({top.probability_pct:.2f}%)")
    print()