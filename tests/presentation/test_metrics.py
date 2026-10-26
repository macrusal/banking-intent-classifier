"""Testes da instrumentação Prometheus da API."""

from collections.abc import Iterator
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY

from banking_intent_classifier.presentation.api import app

LABELS = ["balance"] * 11 + ["card_arrival"]


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Cliente da API com modelo e mapeamento de classes falsos."""

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
        TestClient(app) as test_client,
    ):
        yield test_client


def requests_total(endpoint: str, status_code: str) -> float:
    """Lê o valor atual do Counter para uma combinação de labels."""

    value = REGISTRY.get_sample_value(
        "http_requests_total",
        {"endpoint": endpoint, "status_code": status_code},
    )

    return value or 0.0


def test_metrics_endpoint_exposes_metrics(client: TestClient) -> None:
    """Verifica o formato da resposta e a presença das métricas."""

    client.get("/health")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"] == CONTENT_TYPE_LATEST
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds_bucket" in response.text
    assert 'le="0.0025"' in response.text


def test_counter_increases_after_predict(client: TestClient) -> None:
    """Verifica que um POST /predict incrementa o Counter e o Histogram."""

    requests_before = requests_total("/predict", "200")
    observations_before = REGISTRY.get_sample_value(
        "http_request_duration_seconds_count",
        {"endpoint": "/predict"},
    ) or 0.0

    response = client.post("/predict", json={"text": "I am still waiting on my card"})

    assert response.status_code == 200
    assert requests_total("/predict", "200") == requests_before + 1
    assert REGISTRY.get_sample_value(
        "http_request_duration_seconds_count",
        {"endpoint": "/predict"},
    ) == observations_before + 1


def test_error_status_is_recorded_as_label(client: TestClient) -> None:
    """Verifica que a taxa de erro pode ser derivada do label status_code."""

    before = requests_total("/predict", "422")

    response = client.post("/predict", json={"text": ""})

    assert response.status_code == 422
    assert requests_total("/predict", "422") == before + 1


def test_unknown_path_and_scrape_do_not_create_labels(client: TestClient) -> None:
    """Verifica o label agregado para rotas inexistentes e a exclusão do scrape."""

    unmatched_before = requests_total("unmatched", "404")

    client.get("/rota-inexistente/123")
    client.get("/metrics")

    assert requests_total("unmatched", "404") == unmatched_before + 1
    assert requests_total("/metrics", "200") == 0.0
    assert REGISTRY.get_sample_value(
        "http_requests_total",
        {"endpoint": "/rota-inexistente/123", "status_code": "404"},
    ) is None
