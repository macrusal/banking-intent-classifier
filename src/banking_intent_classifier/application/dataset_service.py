"""Serviços de análise do dataset."""

from datasets import Dataset, DatasetDict
from statistics import mean, median,  quantiles
from collections import Counter
import string

from banking_intent_classifier.domain.dataset_summary import (
    ClassDistributionSummary,
    DatasetSummary,
    SplitSummary,
    TextLengthSummary,
    TextLengthDistributionSummary,
    TextLengthPercentiles,
    TextLengthOutlierSummary,
    TextLengthOutliersSummary,
    CorpusSummary,
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

    def summarize_text_length(
            self,
            dataset: DatasetDict,
            split: str,
    ) -> TextLengthSummary:
        """Calcula estatísticas de comprimento dos textos."""

        texts = dataset[split]["text"]

        character_lengths = [len(text) for text in texts]
        word_lengths = [len(text.split()) for text in texts]

        return TextLengthSummary(
            minimum_characters=min(character_lengths),
            maximum_characters=max(character_lengths),
            mean_characters=mean(character_lengths),
            median_characters=median(character_lengths),
            minimum_words=min(word_lengths),
            maximum_words=max(word_lengths),
            mean_words=mean(word_lengths),
            median_words=median(word_lengths),
        )

    def class_distribution(
            self,
            dataset: DatasetDict,
            split: str,
    ) -> dict[str, int]:
        """Calcula a distribuição das classes de um split do dataset."""

        split_dataset = dataset[split]
        labels = split_dataset["label"]
        label_features = split_dataset.features["label"]

        return {
            label_features.int2str(label): labels.count(label)
            for label in sorted(set(labels))
        }

    def summarize_class_distribution(
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

    def summarize_text_length(
            self,
            dataset: DatasetDict,
            split: str,
    ) -> TextLengthSummary:
        """Calcula estatísticas de comprimento dos textos."""

        texts = dataset[split]["text"]

        character_lengths = [len(text) for text in texts]
        word_lengths = [len(text.split()) for text in texts]

        return TextLengthSummary(
            minimum_characters=min(character_lengths),
            maximum_characters=max(character_lengths),
            mean_characters=mean(character_lengths),
            median_characters=median(character_lengths),
            minimum_words=min(word_lengths),
            maximum_words=max(word_lengths),
            mean_words=mean(word_lengths),
            median_words=median(word_lengths),
        )

    def summarize_text_length_distribution(
        self,
        dataset: DatasetDict,
        split: str,
    ) -> TextLengthDistributionSummary:
        """Calcula os percentis do comprimento dos textos."""

        texts = dataset[split]["text"]

        character_lengths = [len(text) for text in texts]
        word_lengths = [len(text.split()) for text in texts]

        return TextLengthDistributionSummary(
            characters=self._calculate_percentiles(character_lengths),
            words=self._calculate_percentiles(word_lengths),
        )

    @staticmethod
    def _calculate_percentiles(
            values: list[int],
    ) -> TextLengthPercentiles:
        """Calcula os principais percentis de uma distribuição."""

        percentiles = quantiles(values, n=100)

        return TextLengthPercentiles(
            p25=percentiles[24],
            p50=percentiles[49],
            p75=percentiles[74],
            p90=percentiles[89],
            p95=percentiles[94],
            p99=percentiles[98],
        )

    def summarize_text_length_outliers(
            self,
            dataset: DatasetDict,
            split: str,
    ) -> TextLengthOutliersSummary:
        """Identifica possíveis outliers no comprimento dos textos usando IQR."""

        texts = dataset[split]["text"]

        character_lengths = [len(text) for text in texts]
        word_lengths = [len(text.split()) for text in texts]

        return TextLengthOutliersSummary(
            characters=self._calculate_outliers(character_lengths),
            words=self._calculate_outliers(word_lengths),
        )

    @staticmethod
    def _calculate_outliers(
            values: list[int],
    ) -> TextLengthOutlierSummary:
        """Calcula possíveis outliers utilizando o intervalo interquartil."""

        quartiles = quantiles(values, n=4)

        q1 = quartiles[0]
        q3 = quartiles[2]

        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outlier_count = sum(
            value < lower_bound or value > upper_bound
            for value in values
        )

        outlier_percentage = (outlier_count / len(values)) * 100

        return TextLengthOutlierSummary(
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            outlier_count=outlier_count,
            outlier_percentage=outlier_percentage,
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
