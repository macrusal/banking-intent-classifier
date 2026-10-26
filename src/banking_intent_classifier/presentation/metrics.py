"""Instrumentação Prometheus da API HTTP."""

import time

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

METRICS_PATH = "/metrics"
UNMATCHED_ENDPOINT = "unmatched"

# Fronteiras em segundos, calibradas pela latência medida do lado servidor
# (docs/prometheus-instrumentation.md): passos de 0,25 ms entre 1 e 3 ms,
# onde ficam a média e o p95, e 0,5 ms como piso para um backend mais rápido.
LATENCY_BUCKETS = (
    0.0005,
    0.001,
    0.00125,
    0.0015,
    0.00175,
    0.002,
    0.00225,
    0.0025,
    0.00275,
    0.003,
    0.004,
    0.005,
    0.0075,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
)

REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total de requisições HTTP atendidas.",
    ["endpoint", "status_code"],
)

REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "Duração das requisições HTTP, do recebimento ao fim do corpo da resposta.",
    ["endpoint"],
    buckets=LATENCY_BUCKETS,
)


class PrometheusMiddleware:
    """Middleware ASGI que registra contagem e duração de cada requisição."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # O próprio scrape não entra nas métricas do serviço.
        if scope["type"] != "http" or scope["path"] == METRICS_PATH:
            await self.app(scope, receive, send)
            return

        status_code = 500
        start = time.perf_counter()

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code

            if message["type"] == "http.response.start":
                status_code = message["status"]

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # A duração inclui validação, inferência e serialização JSON.
            duration = time.perf_counter() - start
            endpoint = self._endpoint(scope)

            REQUESTS_TOTAL.labels(endpoint, str(status_code)).inc()
            REQUEST_DURATION_SECONDS.labels(endpoint).observe(duration)

    @staticmethod
    def _endpoint(scope: Scope) -> str:
        """Retorna o template da rota, evitando um label por path arbitrário."""

        route = scope.get("route")

        return getattr(route, "path", UNMATCHED_ENDPOINT)


def metrics(request: Request) -> Response:
    """Expõe as métricas no formato de texto do Prometheus."""

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
