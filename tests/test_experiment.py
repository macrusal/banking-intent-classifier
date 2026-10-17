"""Testes do ponto de entrada dos experimentos."""

from unittest.mock import patch

from banking_intent_classifier.domain.experiment_result import ExperimentResult
from banking_intent_classifier.experiment import main


@patch("banking_intent_classifier.experiment.TextPreprocessingExperiment.compare")
@patch("banking_intent_classifier.experiment.TextPreprocessingExperiment.prepare_data")
@patch("banking_intent_classifier.experiment.load_banking77")
def test_main_executes_experiment_and_prints_results(
    mock_load_banking77,
    mock_prepare_data,
    mock_compare,
    capsys,
):
    """Deve executar o experimento e apresentar suas métricas."""

    dataset = object()

    mock_load_banking77.return_value = dataset

    mock_prepare_data.return_value = (
        ["train text"],
        ["validation text"],
        [0],
        [0],
    )

    mock_compare.return_value = [
        ExperimentResult(
            configuration="stop_words=None",
            accuracy=0.8491,
            macro_f1=0.8412,
            weighted_f1=0.8482,
        ),
        ExperimentResult(
            configuration="stop_words=english",
            accuracy=0.8206,
            macro_f1=0.8137,
            weighted_f1=0.8198,
        ),
    ]

    main()

    output = capsys.readouterr().out

    assert "EXPERIMENTO DE STOPWORDS" in output
    assert "Configuração: stop_words=None" in output
    assert "Accuracy: 0.8491" in output
    assert "Macro F1: 0.8412" in output
    assert "Weighted F1: 0.8482" in output

    assert "Configuração: stop_words=english" in output
    assert "Accuracy: 0.8206" in output
    assert "Macro F1: 0.8137" in output
    assert "Weighted F1: 0.8198" in output

    mock_load_banking77.assert_called_once_with()

    mock_prepare_data.assert_called_once_with(dataset)

    mock_compare.assert_called_once_with(
        train_texts=["train text"],
        validation_texts=["validation text"],
        train_labels=[0],
        validation_labels=[0],
    )