"""Serviços de análise do dataset."""

from datasets import DatasetDict

from banking_intent_classifier.domain.dataset_summary import (
    DatasetSummary,
    SplitSummary,
)


class DatasetService:
    """Responsável por realizar análises básicas sobre o dataset."""

    def summarize(self, dataset: DatasetDict) -> DatasetSummary:
        """Gera um resumo básico dos splits do dataset."""

        train = dataset["train"]
        test = dataset["test"]

        return DatasetSummary(
            train=SplitSummary(
                records=len(train),
                classes=len(set(train["label"])),
            ),
            test=SplitSummary(
                records=len(test),
                classes=len(set(test["label"])),
            ),
            total_records=len(train) + len(test),
        )