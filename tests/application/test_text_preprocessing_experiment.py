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