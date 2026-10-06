"""Análise do comprimento dos textos do dataset."""

from statistics import mean, median, quantiles

from datasets import DatasetDict

from banking_intent_classifier.domain.dataset_summary import (
    TextLengthDistributionSummary,
    TextLengthOutlierSummary,
    TextLengthOutliersSummary,
    TextLengthPercentiles,
    TextLengthSummary,
)


class TextLengthAnalyzer:
    """Responsável pela análise do comprimento dos textos."""

    def summarize(
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

    def summarize_distribution(
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

    def summarize_outliers(
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