from datasets import Dataset, DatasetDict

from banking_intent_classifier.application.corpus_analyzer import (
    CorpusAnalyzer,
)


def test_should_summarize_corpus() -> None:
    dataset = DatasetDict(
        {
            "train": Dataset.from_dict(
                {
                    "text": [
                        "Hello world!",
                        "hello BANK",
                        "Bank world.",
                    ],
                    "label": [
                        0,
                        1,
                        0,
                    ],
                }
            )
        }
    )

    analyzer = CorpusAnalyzer()

    result = analyzer.summarize(
        dataset,
        "train",
    )

    assert result.total_documents == 3
    assert result.total_words == 6
    assert result.unique_words == 6
    assert result.unique_words_lowercase == 4
    assert result.unique_words_normalized == 3

def test_should_return_most_frequent_tokens() -> None:
    dataset = DatasetDict(
        {
            "train": Dataset.from_dict(
                {
                    "text": [
                        "Hello world!",
                        "hello BANK",
                        "Bank world.",
                    ],
                    "label": [
                        0,
                        1,
                        0,
                    ],
                }
            )
        }
    )

    analyzer = CorpusAnalyzer()

    result = analyzer.most_frequent_tokens(
        dataset,
        "train",
    )

    frequencies = {
        item.token: item.frequency
        for item in result
    }

    assert frequencies == {
        "hello": 2,
        "world": 2,
        "bank": 2,
    }