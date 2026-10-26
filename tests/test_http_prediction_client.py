"""Testes do cliente HTTP da API, contra um servidor local efêmero."""

import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import ClassVar

import pytest

from banking_intent_classifier.infrastructure.http_prediction_client import (
    HttpPredictionClient,
)


class FakeApiHandler(BaseHTTPRequestHandler):
    """Imita /health e /predict; o texto "erro" provoca resposta 500."""

    protocol_version = "HTTP/1.1"
    connections: ClassVar[set[tuple[str, int]]] = set()

    def do_GET(self) -> None:
        self.connections.add(self.client_address)

        if self.path == "/health":
            self._respond(200, {"status": "ok"})
        else:
            self._respond(404, {"detail": "Not Found"})

    def do_POST(self) -> None:
        self.connections.add(self.client_address)
        length = int(self.headers["Content-Length"])
        payload = json.loads(self.rfile.read(length))

        if payload["text"] == "erro":
            self._respond(500, {"detail": "falha interna"})
        else:
            self._respond(200, {"intent_id": 1, "intent": payload["text"]})

    def _respond(self, status: int, body: dict) -> None:
        content = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args) -> None:
        """Silencia o log do servidor de teste."""


@pytest.fixture
def base_url() -> Iterator[str]:
    """Sobe o servidor falso em 127.0.0.1, numa porta livre."""

    FakeApiHandler.connections = set()
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeApiHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    yield f"http://127.0.0.1:{server.server_address[1]}"

    server.shutdown()
    server.server_close()


def test_should_predict_and_reuse_connection(base_url: str) -> None:
    """Verifica o corpo da resposta e o reaproveitamento da conexão."""

    client = HttpPredictionClient(base_url)

    try:
        first = client.predict("card_arrival")
        second = client.predict("balance")
    finally:
        client.close()

    assert first == {"intent_id": 1, "intent": "card_arrival"}
    assert second == {"intent_id": 1, "intent": "balance"}
    assert len(FakeApiHandler.connections) == 1


def test_should_raise_on_unexpected_status(base_url: str) -> None:
    """Verifica que status diferente de 200 vira erro com o código."""

    client = HttpPredictionClient(base_url)

    try:
        with pytest.raises(RuntimeError, match="500"):
            client.predict("erro")
    finally:
        client.close()


def test_should_report_health(base_url: str) -> None:
    """Verifica a consulta ao /health."""

    client = HttpPredictionClient(base_url)

    try:
        assert client.health() is True
    finally:
        client.close()


def test_should_report_unhealthy_when_api_is_unreachable() -> None:
    """Verifica que uma API inacessível é tratada como indisponível."""

    # Porta 9 (discard) em loopback: a conexão é recusada.
    client = HttpPredictionClient("http://127.0.0.1:9", timeout=1.0)

    try:
        assert client.health() is False
    finally:
        client.close()


@pytest.mark.parametrize("base_url", ["https://localhost:8000", "localhost:8000"])
def test_should_reject_invalid_base_url(base_url: str) -> None:
    """Verifica a rejeição de URLs que não são HTTP."""

    with pytest.raises(ValueError, match="URL base inválida"):
        HttpPredictionClient(base_url)
