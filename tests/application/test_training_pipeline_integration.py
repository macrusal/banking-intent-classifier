"""Teste de integração local das três etapas do pipeline de treinamento."""

import json
from unittest.mock import patch

from datasets import ClassLabel, Dataset, DatasetDict, Features, Value

from banking_intent_classifier.application import training_pipeline
from banking_intent_classifier.infrastructure.label_repository import LabelRepository
from banking_intent_classifier.infrastructure.model_repository import ModelRepository


def test_should_ingest_train_and_publish_artifacts(tmp_path) -> None:
    """Executa o fluxo completo com dataset pequeno, sem acessar a rede."""
    features = Features(
        {"text": Value("string"), "label": ClassLabel(names=["balance", "card_arrival"])}
    )
    dataset = DatasetDict(
        {
            "train": Dataset.from_dict(
                {
                    "text": [
                        "check my account balance",
                        "what is my current balance",
                        "show my available balance",
                        "how much money is in my account",
                        "my card has not arrived",
                        "where is my new card",
                        "I am waiting for my card",
                        "when will my card arrive",
                    ],
                    "label": [0, 0, 0, 0, 1, 1, 1, 1],
                },
                features=features,
            ),
            "test": Dataset.from_dict(
                {
                    "text": ["show my balance", "my card did not arrive"],
                    "label": [0, 1],
                },
                features=features,
            ),
        }
    )
    dataset_path = tmp_path / "data" / "banking77"
    training_path = tmp_path / "training"
    artifact_path = tmp_path / "artifacts" / "baseline_pipeline.joblib"
    label_path = tmp_path / "artifacts" / "label_mapping.json"

    with patch.object(training_pipeline, "load_banking77", return_value=dataset) as loader:
        ingested_path = training_pipeline.ingest_data(dataset_path)

    loader.assert_called_once_with()
    assert ingested_path == dataset_path
    assert dataset_path.is_dir()

    result_path = training_pipeline.train_model(ingested_path, training_path)
    assert result_path == training_path
    assert (training_path / "pipeline.joblib").is_file()
    assert (training_path / "label_mapping.json").is_file()
    metrics_path = training_path / "metrics.json"
    assert metrics_path.is_file()
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert set(metrics) == {"accuracy", "macro_f1", "weighted_f1"}
    assert all(0.0 <= value <= 1.0 for value in metrics.values())

    training_pipeline.save_artifacts(result_path, artifact_path, label_path)
    assert artifact_path.is_file()
    assert label_path.is_file()
    assert LabelRepository.load(label_path) == ["balance", "card_arrival"]

    published_model = ModelRepository.load(artifact_path)
    predictions = published_model.predict(["check my balance", "where is my card"])
    assert len(predictions) == 2
    assert set(predictions).issubset({0, 1})
