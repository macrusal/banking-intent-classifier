from datasets import Dataset, DatasetDict

from banking_intent_classifier.application.text_length_analyzer import (
    TextLengthAnalyzer,
)

def test_should_summarize_text_length() -> None:
    dataset = DatasetDict(
        {
            "train": Dataset.from_dict(
                {
                    "text": [
                        "hello world",
                        "hello",
                        "hello beautiful world",
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

    analyzer = TextLengthAnalyzer()

    result = analyzer.summarize(
        dataset,
        "train",
    )

    assert result.minimum_characters == 5
    assert result.maximum_characters == 21
    assert result.mean_characters == 37 / 3
    assert result.median_characters == 11

    assert result.minimum_words == 1
    assert result.maximum_words == 3
    assert result.mean_words == 2
    assert result.median_words == 2

def test_should_summarize_text_length_distribution() -> None:
    dataset = DatasetDict(
        {
            "train": Dataset.from_dict(
                {
                    "text": [
                        "a",
                        "aa",
                        "aaa",
                        "aaaa",
                    ],
                    "label": [
                        0,
                        0,
                        1,
                        1,
                    ],
                }
            )
        }
    )

    analyzer = TextLengthAnalyzer()

    result = analyzer.summarize_distribution(
        dataset,
        "train",
    )

    assert result.characters.p25 == 1.25
    assert result.characters.p50 == 2.5
    assert result.characters.p75 == 3.75

    assert result.words.p25 == 1.0
    assert result.words.p50 == 1.0
    assert result.words.p75 == 1.0

def test_should_summarize_text_length_outliers() -> None:
    dataset = DatasetDict(
        {
            "train": Dataset.from_dict(
                {
                    "text": [
                        "a" * 10,
                        "a" * 10,
                        "a" * 11,
                        "a" * 11,
                        "a" * 12,
                        "a" * 12,
                        "a" * 13,
                        "a" * 100,
                    ],
                    "label": [
                        0,
                        0,
                        0,
                        0,
                        1,
                        1,
                        1,
                        1,
                    ],
                }
            )
        }
    )

    analyzer = TextLengthAnalyzer()

    result = analyzer.summarize_outliers(
        dataset,
        "train",
    )

    assert result.characters.outlier_count == 1
    assert result.characters.outlier_percentage == 12.5

    assert result.words.outlier_count == 0
    assert result.words.outlier_percentage == 0.0