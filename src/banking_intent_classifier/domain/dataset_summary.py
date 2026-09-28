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


@dataclass(frozen=True)
class TextLengthSummary:
    """Representa estatísticas de comprimento dos textos."""

    minimum_characters: int
    maximum_characters: int
    mean_characters: float
    median_characters: float

    minimum_words: int
    maximum_words: int
    mean_words: float
    median_words: float

@dataclass(frozen=True)
class TextLengthPercentiles:
    """Representa os percentis de comprimento dos textos."""

    p25: float
    p50: float
    p75: float
    p90: float
    p95: float
    p99: float

@dataclass(frozen=True)
class TextLengthDistributionSummary:
    """Representa a distribuição do comprimento dos textos."""

    characters: TextLengthPercentiles
    words: TextLengthPercentiles

@dataclass(frozen=True)
class TextLengthOutlierSummary:
    """Representa possíveis valores extremos no comprimento dos textos."""

    lower_bound: float
    upper_bound: float
    outlier_count: int
    outlier_percentage: float

@dataclass(frozen=True)
class TextLengthOutliersSummary:
    """Representa possíveis outliers de comprimento dos textos."""

    characters: TextLengthOutlierSummary
    words: TextLengthOutlierSummary