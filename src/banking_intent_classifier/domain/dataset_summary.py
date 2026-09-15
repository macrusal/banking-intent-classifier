"""Objetos de domínio relacionados ao resumo do dataset."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SplitSummary:
    """Representa o resumo de um split do dataset."""

    records: int
    classes: int
    missing_texts: int
    missing_labels: int
    empty_texts: int
    duplicated_records: int


@dataclass(frozen=True)
class DatasetSummary:
    """Representa o resumo geral do dataset."""

    train: SplitSummary
    test: SplitSummary
    total_records: int
    same_classes_in_splits: bool
    overlapping_texts: int

@dataclass(frozen=True)
class ClassDistributionSummary:
    """Representa estatísticas da distribuição das classes."""

    minimum: int
    maximum: int
    mean: float
    median: float