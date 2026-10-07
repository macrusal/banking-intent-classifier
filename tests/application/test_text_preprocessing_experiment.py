from sklearn.feature_extraction.text import TfidfVectorizer
from banking_intent_classifier.application.text_preprocessing_experiment import (
    TextPreprocessingExperiment,
)

def test_should_remove_english_stopwords_when_configured() -> None:
    texts = [
        "I want to transfer money",
        "How can I transfer the money",
    ]

    vectorizer = TextPreprocessingExperiment.create_vectorizer(
        remove_stopwords=True,
    )

    vectorizer.fit(texts)

    vocabulary = vectorizer.get_feature_names_out()

    assert "transfer" in vocabulary
    assert "money" in vocabulary

    assert "the" not in vocabulary
    assert "how" not in vocabulary
    assert "can" not in vocabulary

def test_should_keep_english_stopwords_when_not_configured() -> None:
    texts = [
        "I want to transfer money",
        "How can I transfer the money",
    ]

    vectorizer = TextPreprocessingExperiment.create_vectorizer(
        remove_stopwords=False,
    )

    vectorizer.fit(texts)

    vocabulary = vectorizer.get_feature_names_out()

    assert "transfer" in vocabulary
    assert "money" in vocabulary

    assert "the" in vocabulary
    assert "how" in vocabulary
    assert "can" in vocabulary

    def test_should_prepare_stratified_train_and_validation_data() -> None:
        dataset = {
            "train": {
                "text": [f"text-{index}" for index in range(20)],
                "label": [0] * 10 + [1] * 10,
            }
        }

        train_texts, validation_texts, train_labels, validation_labels = (
            TextPreprocessingExperiment.prepare_data(dataset)
        )

        assert len(train_texts) == 16
        assert len(validation_texts) == 4

        assert train_labels.count(0) == 8
        assert train_labels.count(1) == 8

        assert validation_labels.count(0) == 2
        assert validation_labels.count(1) == 2

def test_should_prepare_stratified_train_and_validation_data() -> None:
    dataset = {
        "train": {
            "text": [f"text-{index}" for index in range(20)],
            "label": [0] * 10 + [1] * 10,
        }
    }

    train_texts, validation_texts, train_labels, validation_labels = (
        TextPreprocessingExperiment.prepare_data(dataset)
    )

    assert len(train_texts) == 16
    assert len(validation_texts) == 4

    assert train_labels.count(0) == 8
    assert train_labels.count(1) == 8

    assert validation_labels.count(0) == 2
    assert validation_labels.count(1) == 2

def test_should_run_preprocessing_experiment() -> None:
    train_texts = [
        "transfer money",
        "send money",
        "make transfer",
        "card payment",
        "pay with card",
        "card purchase",
    ]
    train_labels = [0, 0, 0, 1, 1, 1]

    validation_texts = [
        "transfer money",
        "card payment",
    ]
    validation_labels = [0, 1]

    result = TextPreprocessingExperiment.run(
        train_texts=train_texts,
        validation_texts=validation_texts,
        train_labels=train_labels,
        validation_labels=validation_labels,
        remove_stopwords=False,
    )

    assert result.configuration == "stop_words=None"
    assert 0.0 <= result.accuracy <= 1.0
    assert 0.0 <= result.macro_f1 <= 1.0
    assert 0.0 <= result.weighted_f1 <= 1.0

def test_should_compare_stopword_configurations() -> None:
    train_texts = [
        "transfer money",
        "send money",
        "make transfer",
        "card payment",
        "pay with card",
        "card purchase",
    ]
    train_labels = [0, 0, 0, 1, 1, 1]

    validation_texts = [
        "transfer money",
        "card payment",
    ]
    validation_labels = [0, 1]

    results = TextPreprocessingExperiment.compare(
        train_texts=train_texts,
        validation_texts=validation_texts,
        train_labels=train_labels,
        validation_labels=validation_labels,
    )

    assert len(results) == 2

    assert results[0].configuration == "stop_words=None"
    assert results[1].configuration == "stop_words=english"

def test_should_compare_stopword_configurations() -> None:
    train_texts = [
        "transfer money",
        "send money",
        "make transfer",
        "card payment",
        "pay with card",
        "card purchase",
    ]
    train_labels = [0, 0, 0, 1, 1, 1]

    validation_texts = [
        "transfer money",
        "card payment",
    ]
    validation_labels = [0, 1]

    results = TextPreprocessingExperiment.compare(
        train_texts=train_texts,
        validation_texts=validation_texts,
        train_labels=train_labels,
        validation_labels=validation_labels,
    )

    assert len(results) == 2
    assert results[0].configuration == "stop_words=None"
    assert results[1].configuration == "stop_words=english"