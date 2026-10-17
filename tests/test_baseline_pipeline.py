from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from banking_intent_classifier.application.model_trainer import (
    ModelTrainer,
)


def test_create_baseline_pipeline():
    """Verifica a estrutura e a configuração do baseline."""

    pipeline = ModelTrainer.create_baseline_pipeline()

    assert isinstance(pipeline, Pipeline)

    vectorizer = pipeline.named_steps["tfidf"]
    classifier = pipeline.named_steps["classifier"]

    assert isinstance(vectorizer, TfidfVectorizer)
    assert vectorizer.stop_words is None

    assert isinstance(classifier, LogisticRegression)
    assert classifier.max_iter == 1000