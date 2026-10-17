"""Testes dos endpoints HTTP da API."""

from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from banking_intent_classifier.presentation.api import app


LABELS = ["balance"] * 11 + ["card_arrival"]


def test_health_endpoint() -> None:
    """Verifica o endpoint de saúde da API."""
    model = Mock()

    with (
        patch(
            "banking_intent_classifier.presentation.api.ModelRepository.load",
            return_value=model,
        ),
        patch(
            "banking_intent_classifier.presentation.api.LabelRepository.load",
            return_value=LABELS,
        ),
    ):
        with TestClient(app) as client:
            response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_endpoint() -> None:
    """Verifica a classificação de uma mensagem e o nome da intenção."""
    model = Mock()
    model.predict.return_value = [11]

    with (
        patch(
            "banking_intent_classifier.presentation.api.ModelRepository.load",
            return_value=model,
        ),
        patch(
            "banking_intent_classifier.presentation.api.LabelRepository.load",
            return_value=LABELS,
        ),
    ):
        with TestClient(app) as client:
            response = client.post(
                "/predict",
                json={"text": "I am still waiting on my card"},
            )

    assert response.status_code == 200
    assert response.json() == {
        "intent_id": 11,
        "intent": "card_arrival",
    }
    model.predict.assert_called_once_with(["I am still waiting on my card"])


def test_predict_rejects_empty_text() -> None:
    """Verifica a rejeição de mensagens vazias."""
    model = Mock()

    with (
        patch(
            "banking_intent_classifier.presentation.api.ModelRepository.load",
            return_value=model,
        ),
        patch(
            "banking_intent_classifier.presentation.api.LabelRepository.load",
            return_value=LABELS,
        ),
    ):
        with TestClient(app) as client:
            response = client.post("/predict", json={"text": ""})

    assert response.status_code == 422
    model.predict.assert_not_called()


def test_predict_rejects_blank_text() -> None:
    """Verifica a rejeição de mensagens contendo apenas espaços."""
    model = Mock()

    with (
        patch(
            "banking_intent_classifier.presentation.api.ModelRepository.load",
            return_value=model,
        ),
        patch(
            "banking_intent_classifier.presentation.api.LabelRepository.load",
            return_value=LABELS,
        ),
    ):
        with TestClient(app) as client:
            response = client.post("/predict", json={"text": "   "})

    assert response.status_code == 422
    model.predict.assert_not_called()
