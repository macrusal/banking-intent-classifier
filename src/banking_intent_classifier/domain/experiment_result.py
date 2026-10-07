"""Resultados dos experimentos de classificação."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExperimentResult:
    """Representa as métricas obtidas por uma configuração experimental."""

    configuration: str
    accuracy: float
    macro_f1: float
    weighted_f1: float