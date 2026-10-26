"""Testes da orquestração da baseline de latência HTTP."""

import json
from pathlib import Path
from typing import ClassVar
from unittest.mock import patch

import pytest
from datasets import ClassLabel, Dataset, DatasetDict, Features, Value

from banking_intent_classifier import http_latency_benchmark

LABEL_NAMES = ["balance", "card_arrival"]
TEST_TEXTS = ["show my balance", "I am waiting for my card", "balance please"]


def create_dataset() -> DatasetDict:
    """Cria um dataset pequeno com a estrutura do BANKING77."""

    features = Features(
        {"text": Value("string"), "label": ClassLabel(names=LABEL_NAMES)}
    )

    return DatasetDict(
        {
            "test": Dataset.from_dict(
                {"text": TEST_TEXTS, "label": [0, 1, 0]},
                features=features,
            ),
        }
    )


class FakeClient:
    """Cliente falso que registra as requisições recebidas."""

    instances: ClassVar[list["FakeClient"]] = []

    def __init__(self, base_url: str, healthy: bool = True) -> None:
        self.base_url = base_url
        self.healthy = healthy
        self.texts: list[str] = []
        self.closed = False
        FakeClient.instances.append(self)

    def health(self) -> bool:
        return self.healthy

    def predict(self, text: str) -> dict:
        self.texts.append(text)
        return {"intent_id": 0, "intent": "balance"}

    def close(self) -> None:
        self.closed = True


def run_main(arguments: list[str], client_class=FakeClient) -> None:
    """Executa a CLI com dataset e cliente falsos."""

    FakeClient.instances = []

    with (
        patch.object(
            http_latency_benchmark,
            "load_banking77",
            return_value=create_dataset(),
        ),
        patch.object(http_latency_benchmark, "HttpPredictionClient", client_class),
    ):
        http_latency_benchmark.main(arguments)


def test_should_measure_and_save_report(tmp_path: Path, capsys) -> None:
    """Valida o fluxo completo da CLI e o conteúdo do relatório."""

    output = tmp_path / "reports" / "http_latency.json"

    run_main(
        ["--name", "onnx", "--warmup", "2", "--requests", "2", "--output", str(output)]
    )

    client = FakeClient.instances[0]

    assert client.base_url == "http://localhost:8000"
    assert client.texts == TEST_TEXTS[:2] + TEST_TEXTS[:2]
    assert client.closed

    report = json.loads(output.read_text(encoding="utf-8"))

    assert set(report) == {"environment", "target", "dataset", "parameters", "result"}
    assert report["target"]["name"] == "onnx"
    assert report["dataset"]["split"] == "test"
    assert report["dataset"]["samples"] == 2
    assert report["parameters"] == {
        "warmup": 2,
        "concurrency": 1,
        "connection": "keep-alive",
    }
    assert report["result"]["name"] == "onnx"
    assert report["result"]["samples"] == 2

    output_text = capsys.readouterr().out

    assert "BASELINE DE LATÊNCIA HTTP — BANKING77" in output_text
    assert "Latência p95" in output_text


def test_should_use_whole_split_and_default_report_path(tmp_path: Path) -> None:
    """Verifica o split inteiro e o caminho padrão do relatório."""

    with patch.object(http_latency_benchmark, "REPORT_DIRECTORY", tmp_path):
        run_main(["--warmup", "0"])

    assert FakeClient.instances[0].texts == TEST_TEXTS
    assert (tmp_path / "http_latency_sklearn.json").is_file()


def test_should_stop_when_api_is_unhealthy(tmp_path: Path) -> None:
    """Verifica a interrupção quando /health não responde."""

    def unhealthy_client(base_url: str) -> FakeClient:
        return FakeClient(base_url, healthy=False)

    output = tmp_path / "http_latency.json"

    with pytest.raises(RuntimeError, match="/health"):
        run_main(["--output", str(output)], client_class=unhealthy_client)

    assert FakeClient.instances[0].closed
    assert FakeClient.instances[0].texts == []
    assert not output.exists()


def test_should_reject_non_positive_requests() -> None:
    """Verifica a rejeição de quantidade de requisições inválida."""

    with pytest.raises(ValueError, match="requisições"):
        run_main(["--requests", "0"])
