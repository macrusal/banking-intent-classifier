"""Análise do corpus textual do dataset."""

from collections import Counter
import string

from datasets import DatasetDict

from banking_intent_classifier.domain.dataset_summary import (
    CorpusSummary,
    TokenFrequency,
)


class CorpusAnalyzer:
    """Responsável pela análise do corpus textual."""

    def summarize(
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