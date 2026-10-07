"""Análise da distribuição das classes do dataset."""

from statistics import mean, median

from datasets import DatasetDict

from banking_intent_classifier.domain.dataset_summary import (
    ClassDistributionSummary,
)


class ClassDistributionAnalyzer:
    """Responsável pela análise da distribuição das classes."""

    def distribution(
        self,
        dataset: DatasetDict,
        split: str,
    ) -> dict[str, int]:
        """Calcula a distribuição das classes de um split."""

        split_dataset = dataset[split]
        labels = split_dataset["label"]
        label_features = split_dataset.features["label"]

        return {
            label_features.int2str(label): labels.count(label)
            for label in sorted(set(labels))
        }

    def summarize(
        self,
        distribution: dict[str, int],
    ) -> ClassDistributionSummary:
        """Calcula estatísticas da distribuição das classes."""

        counts = list(distribution.values())

        return ClassDistributionSummary(
            minimum=min(counts),
            maximum=max(counts),
            mean=mean(counts),
            median=median(counts),
        )