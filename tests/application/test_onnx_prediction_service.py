"""Testes do serviço de predição com ONNX Runtime."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

from banking_intent_classifier.application.model_trainer import ModelTrainer
from banking_intent_classifier.application.onnx_prediction_service import (
    OnnxPredictionService,
)
from banking_intent_classifier.application.prediction_service import (
    PredictionService,
)


def create_fake_session(labels: list[int]) -> Mock:
    """Cria uma sessão falsa com a interface usada pelo serviço."""

    session = Mock()
    session.get_inputs.return_value = [SimpleNamespace(name="input_text")]
    session.get_outputs.return_value = [
        SimpleNamespace(name="output_label"),
        SimpleNamespace(name="output_probability"),
    ]
    session.run.return_value = [np.array(labels, dtype=np.int64)]

    return session


def test_should_predict_intent() -> None:
    """Verifica se o serviço retorna a classe prevista como int."""

    session = create_fake_session([11])
    service = OnnxPredictionService(session)

    result = service.predict("I am still waiting on my card")

    assert result == 11
    assert type(result) is int

    output_names, feeds = session.run.call_args.args

    assert output_names == ["output_label"]
    assert list(feeds) == ["input_text"]
    assert feeds["input_text"].shape == (1, 1)
    assert feeds["input_text"].tolist() == [["I am still waiting on my card"]]


def test_should_predict_batch_in_order() -> None:
    """Verifica a predição em lote, preservando a ordem dos textos."""

    texts = ["check my balance", "my card is lost", "where is my card"]
    session = create_fake_session([3, 41, 11])
    service = OnnxPredictionService(session)

    result = service.predict_batch(texts)

    assert result == [3, 41, 11]
    assert all(type(label) is int for label in result)

    _, feeds = session.run.call_args.args

    assert feeds["input_text"].shape == (3, 1)
    assert feeds["input_text"].ravel().tolist() == texts


@pytest.mark.parametrize(
    "text",
    ["", " ", "\n\t"],
)
def test_should_reject_empty_text(text: str) -> None:
    """Verifica a rejeição de mensagens vazias."""

    session = create_fake_session([0])
    service = OnnxPredictionService(session)

    with pytest.raises(ValueError, match="O texto não pode estar vazio"):
        service.predict(text)

    session.run.assert_not_called()


def test_should_reject_empty_batch() -> None:
    """Verifica a rejeição de lotes vazios."""

    session = create_fake_session([0])
    service = OnnxPredictionService(session)

    with pytest.raises(ValueError, match="A lista de textos não pode estar vazia"):
        service.predict_batch([])

    session.run.assert_not_called()


def test_should_reject_batch_with_empty_text() -> None:
    """Verifica a rejeição de lotes contendo mensagens vazias."""

    session = create_fake_session([0, 0])
    service = OnnxPredictionService(session)

    with pytest.raises(ValueError, match="O texto não pode estar vazio"):
        service.predict_batch(["check my balance", " "])

    session.run.assert_not_called()


def test_should_match_scikit_learn_predictions(tmp_path: Path) -> None:
    """Verifica a equivalência com o PredictionService em um modelo real."""

    pytest.importorskip("onnxruntime")
    pytest.importorskip("skl2onnx")

    from banking_intent_classifier.infrastructure.onnx_model_repository import (
        OnnxModelRepository,
    )

    texts = [
        "I want to check my balance",
        "My card has been stolen",
        "How much money do I have",
        "I need to block my stolen card",
    ]

    pipeline = ModelTrainer.create_baseline_pipeline()
    pipeline.fit(texts, [0, 1, 0, 1])

    artifact_path = tmp_path / "baseline_pipeline.onnx"
    OnnxModelRepository.export(pipeline, artifact_path)

    onnx_service = OnnxPredictionService(OnnxModelRepository.load(artifact_path))
    sklearn_service = PredictionService(pipeline)

    probe = "Where's my CARD?!"

    assert onnx_service.predict(probe) == sklearn_service.predict(probe)
    assert onnx_service.predict_batch(texts) == pipeline.predict(texts).tolist()
