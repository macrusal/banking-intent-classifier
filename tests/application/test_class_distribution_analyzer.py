from datasets import ClassLabel, Dataset, DatasetDict

from banking_intent_classifier.application.class_distribution_analyzer import (
    ClassDistributionAnalyzer,
)

def test_should_calculate_class_distribution() -> None:
    dataset = DatasetDict(
        {
            "train": Dataset.from_dict(
                {
                    "text": [
                        "Where is my card?",
                        "My card has not arrived",
                        "I need to make a transfer",
                    ],
                    "label": [
                        0,
                        0,
                        1,
                    ],
                },
                features=None,
            )
        }
    )

    dataset["train"] = dataset["train"].cast_column(
        "label",
        ClassLabel(
            names=[
                "card_arrival",
                "bank_transfer",
            ]
        ),
    )

    analyzer = ClassDistributionAnalyzer()

    result = analyzer.distribution(
        dataset,
        "train",
    )

    assert result == {
        "card_arrival": 2,
        "bank_transfer": 1,
    }

def test_should_summarize_class_distribution() -> None:
    distribution = {
        "card_arrival": 35,
        "bank_transfer": 100,
        "cash_withdrawal": 187,
    }

    analyzer = ClassDistributionAnalyzer()

    result = analyzer.summarize(
        distribution
    )

    assert result.minimum == 35
    assert result.maximum == 187
    assert result.mean == 107.33333333333333
    assert result.median == 100