
"""Testes do fluxo de treinamento final."""

from unittest.mock import MagicMock, patch

from banking_intent_classifier import final_training


def test_should_train_evaluate_and_save_final_model(
    tmp_path,
    capsys,
) -> None:
    """Valida a orquestração do treinamento oficial."""

    dataset = {
        "train": {
            "text": ["balance", "stolen card"],
            "label": [0, 1],
        },
        "test": {
            "text": ["check balance"],
            "label": [0],
        },
    }

    pipeline = MagicMock()
    pipeline.predict.return_value = [0]

    evaluation = MagicMock(
        accuracy=0.9,
        macro_f1=0.85,
        weighted_f1=0.88,
    )

    artifact_path = tmp_path / "baseline_pipeline.joblib"

    with (
        patch.object(
            final_training,
            "load_banking77",
            return_value=dataset,
        ),
        patch.object(
            final_training.ModelTrainer,
            "create_baseline_pipeline",
            return_value=pipeline,
        ),
        patch.object(
            final_training.ModelEvaluator,
            "evaluate",
            return_value=evaluation,
        ) as evaluate,
        patch.object(
            final_training.ModelRepository,
            "save",
        ) as save,
        patch.object(
            final_training,
            "ARTIFACT_PATH",
            artifact_path,
        ),
    ):
        final_training.main()

    pipeline.fit.assert_called_once_with(
        dataset["train"]["text"],
        dataset["train"]["label"],
    )

    pipeline.predict.assert_called_once_with(
        dataset["test"]["text"],
    )

    evaluate.assert_called_once_with(
        configuration="TF-IDF + Logistic Regression | avaliação oficial",
        labels=[0],
        predictions=[0],
    )

    save.assert_called_once_with(
        pipeline,
        artifact_path,
    )

    output = capsys.readouterr().out

    assert "AVALIAÇÃO FINAL" in output
    assert "Accuracy: 0.9000" in output
    assert "Macro F1: 0.8500" in output
    assert "Weighted F1: 0.8800" in output
