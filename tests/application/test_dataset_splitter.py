from collections import Counter

from banking_intent_classifier.application.dataset_splitter import (
    DatasetSplitter,
)


def test_should_create_stratified_train_and_validation_sets() -> None:
    texts = [f"text-{index}" for index in range(20)]
    labels = [0] * 10 + [1] * 10

    train_texts, validation_texts, train_labels, validation_labels = (
        DatasetSplitter.split(
            texts=texts,
            labels=labels,
            validation_size=0.2,
        )
    )

    assert len(train_texts) == 16
    assert len(validation_texts) == 4

    assert Counter(train_labels) == {0: 8, 1: 8}
    assert Counter(validation_labels) == {0: 2, 1: 2}


def test_should_create_reproducible_split() -> None:
    texts = [f"text-{index}" for index in range(20)]
    labels = [0] * 10 + [1] * 10

    first_split = DatasetSplitter.split(
        texts=texts,
        labels=labels,
        validation_size=0.2,
        random_state=42,
    )

    second_split = DatasetSplitter.split(
        texts=texts,
        labels=labels,
        validation_size=0.2,
        random_state=42,
    )

    assert first_split == second_split