"""Benchmark de latência ponta a ponta de requisições HTTP."""

import time
from collections.abc import Callable
from dataclasses import dataclass

from banking_intent_classifier.application.inference_benchmark import (
    summarize_latencies,
)


@dataclass(frozen=True)
class HttpLatencyResult:
    """Representa as medições de latência de um serviço HTTP."""

    name: str
    samples: int
    warmup: int
    latency_mean_ms: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    latency_min_ms: float
    latency_max_ms: float
    throughput_rps: float
    wall_time_s: float


class HttpLatencyBenchmark:
    """Responsável por medir a latência de requisições sequenciais."""

    @staticmethod
    def measure(
        name: str,
        send_request: Callable[[str], object],
        texts: list[str],
        warmup: int = 100,
        timer: Callable[[], float] = time.perf_counter,
    ) -> HttpLatencyResult:
        """Mede a latência de uma requisição por texto, em sequência."""

        if not texts:
            raise ValueError("A lista de textos não pode estar vazia.")

        if warmup < 0:
            raise ValueError("O aquecimento não pode ser negativo.")

        # O aquecimento não entra nas medições.
        for index in range(warmup):
            send_request(texts[index % len(texts)])

        latencies = []
        started_at = None
        ended_at = None

        for text in texts:
            start = timer()
            send_request(text)
            end = timer()

            # O tempo de parede vai do início da primeira requisição ao fim da
            # última, incluindo o intervalo entre elas. Somar as latências
            # ignoraria esse intervalo e inflaria o throughput.
            if started_at is None:
                started_at = start

            ended_at = end
            latencies.append(end - start)

        summary = summarize_latencies(latencies)
        wall_time = ended_at - started_at

        return HttpLatencyResult(
            name=name,
            samples=len(texts),
            warmup=warmup,
            latency_mean_ms=summary.mean_ms,
            latency_p50_ms=summary.p50_ms,
            latency_p95_ms=summary.p95_ms,
            latency_p99_ms=summary.p99_ms,
            latency_min_ms=summary.min_ms,
            latency_max_ms=summary.max_ms,
            throughput_rps=len(texts) / wall_time,
            wall_time_s=wall_time,
        )
