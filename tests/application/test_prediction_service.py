
"""Testes do serviço de predição."""

from unittest.mock import Mock

import pytest

from banking_intent_classifier.application.prediction_service import (
    PredictionService,
)


def test_should_predict_intent() -> None:
    """Verifica se o serviço retorna a classe prevista."""

    model = Mock()
    model.predict.return_value = [11]

    service = PredictionService(model)

    result = service.predict("I am still waiting on my card")

    assert result == 11
    model.predict.assert_called_once_with(
        ["I am still waiting on my card"]
    )


@pytest.mark.parametrize(
    "text",
    ["", " ", "\n\t"],
)
def test_should_reject_empty_text(text: str) -> None:
    """Verifica a rejeição de mensagens vazias."""

    model = Mock()
    service = PredictionService(model)

    with pytest.raises(ValueError, match="O texto não pode estar vazio"):
        service.predict(text)

    model.predict.assert_not_called()
