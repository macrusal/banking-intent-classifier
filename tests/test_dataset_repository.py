
"""Testes da persistência intermediária do BANKING77."""

from datasets import ClassLabel, Dataset, DatasetDict, Features, Value

from banking_intent_classifier.infrastructure.data.dataset_repository import (
    DatasetRepository,
)


def test_should_save_and_load_dataset(tmp_path):
    features = Features(
        {
            "text": Value("string"),
            "label": ClassLabel(names=["card_arrival", "card_not_working"]),
        }
    )

    train = Dataset.from_dict(
        {
            "text": ["Where is my card?", "My card does not work"],
            "label": [0, 1],
        },
        features=features,
    )

    test = Dataset.from_dict(
        {
            "text": ["I am waiting for my card"],
            "label": [0],
        },
        features=features,
    )

    dataset = DatasetDict({"train": train, "test": test})
    path = tmp_path / "banking77"

    DatasetRepository.save(dataset, path)
    restored = DatasetRepository.load(path)

    assert len(restored["train"]) == 2
    assert len(restored["test"]) == 1
    assert restored["train"]["text"][0] == "Where is my card?"
    assert restored["train"].features["label"].names == [
        "card_arrival",
        "card_not_working",
    ]
