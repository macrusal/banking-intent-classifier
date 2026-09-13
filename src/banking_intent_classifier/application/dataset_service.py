"""Serviços de análise do dataset."""

from datasets import Dataset, DatasetDict

from banking_intent_classifier.domain.dataset_summary import (
    DatasetSummary,
    SplitSummary,
)


class DatasetService:
    """Responsável por realizar análises básicas sobre o dataset."""

    def summarize(self, dataset: DatasetDict) -> DatasetSummary:
        """Gera um resumo da estrutura e qualidade básica do dataset."""

        train = dataset["train"]
        test = dataset["test"]

        train_summary = self._summarize_split(train)
        test_summary = self._summarize_split(test)

        train_labels = set(train["label"])
        test_labels = set(test["label"])

        train_texts = set(train["text"])
        test_texts = set(test["text"])
        overlapping_texts = len(train_texts & test_texts)

        return DatasetSummary(
            train=train_summary,
            test=test_summary,
            total_records=len(train) + len(test),
            same_classes_in_splits=train_labels == test_labels,
            overlapping_texts=overlapping_texts,
        )

    def _summarize_split(self, split: Dataset) -> SplitSummary:
        """Gera o resumo de um split do dataset."""

        dataframe = split.to_pandas()

        missing_texts = dataframe["text"].isna().sum()
        missing_labels = dataframe["label"].isna().sum()

        empty_texts = (
            dataframe["text"]
            .fillna("")
            .astype(str)
            .str.strip()
            .eq("")
            .sum()
        )

        duplicated_records = dataframe.duplicated().sum()

        return SplitSummary(
            records=len(split),
            classes=len(set(split["label"])),
            missing_texts=int(missing_texts),
            missing_labels=int(missing_labels),
            empty_texts=int(empty_texts),
            duplicated_records=int(duplicated_records),
        )