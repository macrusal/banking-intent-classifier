"""Testes do fluxo de treinamento final."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from datasets import Dataset, DatasetDict

from banking_intent_classifier import final_training


def test_should_train_evaluate_and_save_final_model(tmp_path, capsys) -> None:
    """Valida a orquestração do treinamento oficial e seus artefatos."""
    dataset = DatasetDict(
        {
            "train": Dataset.from_dict(
                {
                    "text": ["balance", "stolen card"],
                    "label": [0, 1],
                }
            ),
            "test": Dataset.from_dict(
                {
                    "text": ["check balance"],
                    "label": [0],
                }
            ),
        }
    )
    pipeline = MagicMock()
    evaluation = SimpleNamespace(
        accuracy=0.9,
        macro_f1=0.85,
        weighted_f1=0.88,
    )
    labels = ["balance", "stolen_card"]
    artifact_path = tmp_path / "baseline_pipeline.joblib"
    label_mapping_path = tmp_path / "label_mapping.json"

    with (
        patch.object(final_training, "load_banking77", return_value=dataset) as load,
        patch.object(
            final_training,
            "train_and_evaluate",
            return_value=(pipeline, labels, evaluation),
        ) as train_and_evaluate,
        patch.object(final_training.ModelRepository, "save") as save,
        patch.object(final_training.LabelRepository, "save") as save_labels,
        patch.object(final_training, "ARTIFACT_PATH", artifact_path),
        patch.object(final_training, "LABEL_MAPPING_PATH", label_mapping_path),
    ):
        final_training.main()

    load.assert_called_once_with()
    train_and_evaluate.assert_called_once_with(dataset)
    save.assert_called_once_with(pipeline, artifact_path)
    save_labels.assert_called_once_with(labels, label_mapping_path)

    output = capsys.readouterr().out
    assert "AVALIAÇÃO FINAL" in output
    assert "Treinamento oficial: 2" in output
    assert "Teste oficial: 1" in output
    assert "Accuracy: 0.9000" in output
    assert "Macro F1: 0.8500" in output
    assert "Weighted F1: 0.8800" in output
    assert f"Artefato salvo em: {artifact_path}" in output
    assert "Classes persistidas: 2" in output
    assert f"Mapeamento salvo em: {label_mapping_path}" in output
