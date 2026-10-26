"""Cliente HTTP da API de classificação de intenções."""

import json
from http.client import HTTPConnection
from urllib.parse import urlsplit

PREDICT_PATH = "/predict"
HEALTH_PATH = "/health"
JSON_HEADERS = {"Content-Type": "application/json"}


class HttpPredictionClient:
    """Envia requisições à API mantendo uma conexão persistente."""

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        url = urlsplit(base_url)

        if url.scheme != "http" or not url.hostname:
            raise ValueError(f"URL base inválida: {base_url}")

        self.base_url = base_url
        # Keep-alive: a conexão TCP é reaproveitada entre as requisições.
        self._connection = HTTPConnection(
            url.hostname,
            url.port or 80,
            timeout=timeout,
        )

    def predict(self, text: str) -> dict:
        """Classifica um texto via POST /predict."""

        body = json.dumps({"text": text})

        return self._request("POST", PREDICT_PATH, body, JSON_HEADERS)

    def health(self) -> bool:
        """Indica se a API responde ao GET /health."""

        try:
            return self._request("GET", HEALTH_PATH) == {"status": "ok"}
        except (OSError, RuntimeError):
            return False

    def close(self) -> None:
        """Encerra a conexão com a API."""

        self._connection.close()

    def _request(
        self,
        method: str,
        path: str,
        body: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict:
        """Executa uma requisição e devolve o corpo JSON da resposta."""

        self._connection.request(method, path, body=body, headers=headers or {})
        response = self._connection.getresponse()
        # A leitura completa libera a conexão para a próxima requisição.
        content = response.read()

        if response.status != 200:
            raise RuntimeError(
                f"{method} {path} respondeu {response.status}: "
                f"{content.decode('utf-8', errors='replace')}"
            )

        return json.loads(content)
