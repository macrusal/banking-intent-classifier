
"""Testes de persistência do Pipeline de classificação."""

from pathlib import Path

from banking_intent_classifier.application.model_trainer import ModelTrainer
from banking_intent_classifier.infrastructure.model_repository import (
    ModelRepository,
)


def test_should_save_and_load_trained_pipeline(tmp_path: Path) -> None:
    """Verifica se o Pipeline mantém suas predições após persistência."""

    texts = [
        "I want to check my balance",
        "My card has been stolen",
        "How much money do I have",
        "I need to block my stolen card",
    ]

    labels = [0, 1, 0, 1]

    pipeline = ModelTrainer.create_baseline_pipeline()
    pipeline.fit(texts, labels)

    artifact_path = tmp_path / "models" / "baseline_pipeline.joblib"

    ModelRepository.save(pipeline, artifact_path)

    assert artifact_path.is_file()

    restored_pipeline = ModelRepository.load(artifact_path)

    original_predictions = pipeline.predict(texts)
    restored_predictions = restored_pipeline.predict(texts)

    assert original_predictions.tolist() == restored_predictions.tolist()
