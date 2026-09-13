"""Objetos de domínio relacionados ao resumo do dataset."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SplitSummary:
    """Representa o resumo de um split do dataset."""

    records: int
    classes: int


@dataclass(frozen=True)
class DatasetSummary:
    """Representa o resumo geral do dataset."""

    train: SplitSummary
    test: SplitSummary
    total_records: int