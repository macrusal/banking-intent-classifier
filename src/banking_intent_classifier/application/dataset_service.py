"""Serviços de análise do dataset."""

from collections import Counter
import string

from datasets import Dataset, DatasetDict

from banking_intent_classifier.domain.dataset_summary import (
    CorpusSummary,
    DatasetSummary,
    SplitSummary,
    TokenFrequency,
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

    def summarize_corpus(
        self,
        dataset: DatasetDict,
        split: str,
    ) -> CorpusSummary:
        """Calcula características gerais do corpus textual."""

        texts = dataset[split]["text"]

        words = [
            word
            for text in texts
            for word in text.split()
        ]

        lowercase_words = [
            word.lower()
            for word in words
        ]

        normalized_words = [
            word.strip(string.punctuation)
            for word in lowercase_words
            if word.strip(string.punctuation)
        ]

        return CorpusSummary(
            total_documents=len(texts),
            total_words=len(words),
            unique_words=len(set(words)),
            unique_words_lowercase=len(set(lowercase_words)),
            unique_words_normalized=len(set(normalized_words)),
        )

    def most_frequent_tokens(
        self,
        dataset: DatasetDict,
        split: str,
        limit: int = 20,
    ) -> list[TokenFrequency]:
        """Retorna os tokens normalizados mais frequentes do corpus."""

        texts = dataset[split]["text"]

        tokens = [
            normalized_token
            for text in texts
            for word in text.split()
            if (
                normalized_token := word
                .lower()
                .strip(string.punctuation)
            )
        ]

        frequencies = Counter(tokens)

        return [
            TokenFrequency(
                token=token,
                frequency=frequency,
            )
            for token, frequency in frequencies.most_common(limit)
        ]