
from unittest.mock import MagicMock, patch

from banking_intent_classifier import baseline


@patch("banking_intent_classifier.baseline.ModelEvaluator.evaluate")
@patch("banking_intent_classifier.baseline.ModelTrainer.create_baseline_pipeline")
@patch("banking_intent_classifier.baseline.DatasetSplitter.split")
@patch("banking_intent_classifier.baseline.load_banking77")
def test_baseline_main(
    mock_loader,
    mock_split,
    mock_pipeline_factory,
    mock_evaluate,
    capsys,
):
    """Verifica a orquestração reproduzível do baseline."""

    mock_loader.return_value = {
        "train": {
            "text": ["texto 1", "texto 2"],
            "label": [0, 1],
        }
    }

    mock_split.return_value = (
        ["texto 1"],
        ["texto 2"],
        [0],
        [1],
    )

    pipeline = MagicMock()
    pipeline.predict.return_value = [1]
    mock_pipeline_factory.return_value = pipeline

    mock_evaluate.return_value = MagicMock(
        configuration="TF-IDF + Logistic Regression | stop_words=None",
        accuracy=0.8491,
        macro_f1=0.8412,
        weighted_f1=0.8482,
    )

    baseline.main()

    mock_split.assert_called_once_with(
        texts=["texto 1", "texto 2"],
        labels=[0, 1],
    )
    pipeline.fit.assert_called_once_with(["texto 1"], [0])
    pipeline.predict.assert_called_once_with(["texto 2"])

    mock_evaluate.assert_called_once_with(
        configuration="TF-IDF + Logistic Regression | stop_words=None",
        labels=[1],
        predictions=[1],
    )

    output = capsys.readouterr().out

    assert "BASELINE FORMAL" in output
    assert "Accuracy: 0.8491" in output
    assert "Macro F1: 0.8412" in output
    assert "Weighted F1: 0.8482" in output
