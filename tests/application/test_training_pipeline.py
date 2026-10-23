
"""Testes das operações do pipeline de treinamento."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from banking_intent_classifier.application.training_pipeline import (
    ingest_data,
    save_artifacts,
    train_model,
)


def test_ingest_data_loads_and_persists_dataset(tmp_path):
    dataset_path = tmp_path / "banking77"

    with (
        patch(
            "banking_intent_classifier.application.training_pipeline.load_banking77"
        ) as loader,
        patch(
            "banking_intent_classifier.application.training_pipeline.DatasetRepository.save"
        ) as repository_save,
    ):
        result = ingest_data(dataset_path)

    loader.assert_called_once_with()
    repository_save.assert_called_once_with(
        loader.return_value,
        dataset_path,
    )

    assert result == Path(dataset_path)

def test_train_model_persists_intermediate_artifacts(tmp_path):
    dataset_path = tmp_path / "dataset"
    output_path = tmp_path / "training"

    metrics = SimpleNamespace(
        accuracy=0.87,
        macro_f1=0.86,
        weighted_f1=0.87,
    )

    with (
        patch(
            "banking_intent_classifier.application.training_pipeline.DatasetRepository.load"
        ) as repository_load,
        patch(
            "banking_intent_classifier.application.training_pipeline.train_and_evaluate"
        ) as training,
        patch(
            "banking_intent_classifier.application.training_pipeline.ModelRepository.save"
        ) as model_save,
        patch(
            "banking_intent_classifier.application.training_pipeline.LabelRepository.save"
        ) as label_save,
    ):
        training.return_value = (
            "pipeline_teste",
            ["card_arrival", "card_not_working"],
            metrics,
        )

        result = train_model(dataset_path, output_path)

    repository_load.assert_called_once_with(dataset_path)
    training.assert_called_once_with(repository_load.return_value)

    model_save.assert_called_once_with(
        "pipeline_teste",
        output_path / "pipeline.joblib",
    )

    label_save.assert_called_once_with(
        ["card_arrival", "card_not_working"],
        output_path / "label_mapping.json",
    )

    assert result == output_path
    assert (output_path / "metrics.json").exists()

def test_save_artifacts_publishes_model_and_labels(tmp_path):
    training_path = tmp_path / "training"
    training_path.mkdir()

    (training_path / "pipeline.joblib").write_bytes(b"modelo_teste")
    (training_path / "label_mapping.json").write_text(
        '["card_arrival"]',
        encoding="utf-8",
    )
    (training_path / "metrics.json").write_text(
        '{"accuracy": 0.87}',
        encoding="utf-8",
    )

    artifact_path = tmp_path / "artifacts" / "baseline_pipeline.joblib"
    label_path = tmp_path / "artifacts" / "label_mapping.json"

    with (
        patch(
            "banking_intent_classifier.application.training_pipeline.ModelRepository.load"
        ),
        patch(
            "banking_intent_classifier.application.training_pipeline.LabelRepository.load"
        ),
    ):
        save_artifacts(training_path, artifact_path, label_path)

    assert artifact_path.read_bytes() == b"modelo_teste"
    assert label_path.read_text(encoding="utf-8") == '["card_arrival"]'
