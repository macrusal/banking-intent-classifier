"""Testes do benchmark de latência HTTP."""

import numpy as np
import pytest

from banking_intent_classifier.application.http_latency_benchmark import (
    HttpLatencyBenchmark,
)

TEXTS = [f"text {index}" for index in range(10)]


class FakeTimer:
    """Timer determinístico: cada par início/fim consome uma duração."""

    def __init__(self, durations: list[float], default: float = 0.002) -> None:
        self._durations = iter(durations)
        self._default = default
        self._calls = 0
        self._now = 0.0

    def __call__(self) -> float:
        if self._calls % 2 == 1:
            self._now += next(self._durations, self._default)

        self._calls += 1

        return self._now


class RecordingSender:
    """Envio falso que registra os textos recebidos."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def __call__(self, text: str) -> dict:
        self.calls.append(text)
        return {"intent_id": 0, "intent": "fake"}


def test_should_send_warmup_and_measured_requests() -> None:
    """Verifica o aquecimento circular e uma requisição medida por texto."""

    sender = RecordingSender()

    result = HttpLatencyBenchmark.measure(
        name="fake",
        send_request=sender,
        texts=TEXTS,
        warmup=13,
        timer=FakeTimer([]),
    )

    assert sender.calls[:13] == TEXTS + TEXTS[:3]
    assert sender.calls[13:] == TEXTS
    assert result.samples == len(TEXTS)
    assert result.warmup == 13


def test_should_compute_metrics_with_constant_latency() -> None:
    """Verifica os cálculos com latência constante de 2 ms."""

    result = HttpLatencyBenchmark.measure(
        name="fake",
        send_request=RecordingSender(),
        texts=TEXTS,
        warmup=0,
        timer=FakeTimer([], default=0.002),
    )

    assert result.name == "fake"
    assert result.latency_mean_ms == pytest.approx(2.0)
    assert result.latency_p50_ms == pytest.approx(2.0)
    assert result.latency_p99_ms == pytest.approx(2.0)
    assert result.wall_time_s == pytest.approx(0.02)
    assert result.throughput_rps == pytest.approx(500.0)


def test_should_compute_percentiles_with_variable_latency() -> None:
    """Verifica os percentis com latências de 1 a 100 ms."""

    latencies_ms = list(range(1, 101))
    texts = [f"text {index}" for index in range(100)]

    result = HttpLatencyBenchmark.measure(
        name="fake",
        send_request=RecordingSender(),
        texts=texts,
        warmup=0,
        timer=FakeTimer([latency / 1000 for latency in latencies_ms]),
    )

    assert result.latency_p50_ms == pytest.approx(np.percentile(latencies_ms, 50))
    assert result.latency_p95_ms == pytest.approx(np.percentile(latencies_ms, 95))
    assert result.latency_p99_ms == pytest.approx(np.percentile(latencies_ms, 99))
    assert result.latency_min_ms == pytest.approx(1.0)
    assert result.latency_max_ms == pytest.approx(100.0)


def test_should_propagate_request_errors() -> None:
    """Verifica que uma falha da API interrompe a medição."""

    def failing_sender(text: str) -> dict:
        raise RuntimeError("POST /predict respondeu 500")

    with pytest.raises(RuntimeError, match="500"):
        HttpLatencyBenchmark.measure(
            name="fake",
            send_request=failing_sender,
            texts=TEXTS,
            warmup=0,
            timer=FakeTimer([]),
        )


@pytest.mark.parametrize(
    ("texts", "warmup"),
    [([], 0), (TEXTS, -1)],
    ids=["lista_vazia", "warmup_negativo"],
)
def test_should_reject_invalid_parameters(texts: list[str], warmup: int) -> None:
    """Verifica a rejeição de parâmetros inválidos."""

    with pytest.raises(ValueError):
        HttpLatencyBenchmark.measure(
            name="fake",
            send_request=RecordingSender(),
            texts=texts,
            warmup=warmup,
            timer=FakeTimer([]),
        )
