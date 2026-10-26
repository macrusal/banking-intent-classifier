"""Benchmark de latência e throughput de preditores de texto."""

import os
import platform
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib import metadata

import numpy as np

BENCHMARKED_PACKAGES = (
    "scikit-learn",
    "numpy",
    "onnxruntime",
    "skl2onnx",
    "onnx",
)

THREAD_VARIABLES = (
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
)


@dataclass(frozen=True)
class LatencySummary:
    """Representa as estatísticas de uma série de latências, em milissegundos."""

    mean_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    min_ms: float
    max_ms: float


def summarize_latencies(latencies_s: list[float]) -> LatencySummary:
    """Calcula média, percentis, mínimo e máximo de latências em segundos."""

    if not latencies_s:
        raise ValueError("A lista de latências não pode estar vazia.")

    latencies_ms = np.array(latencies_s) * 1000

    return LatencySummary(
        mean_ms=float(latencies_ms.mean()),
        p50_ms=float(np.percentile(latencies_ms, 50)),
        p95_ms=float(np.percentile(latencies_ms, 95)),
        p99_ms=float(np.percentile(latencies_ms, 99)),
        min_ms=float(latencies_ms.min()),
        max_ms=float(latencies_ms.max()),
    )


@dataclass(frozen=True)
class BenchmarkResult:
    """Representa as medições de desempenho de um preditor."""

    name: str
    samples: int
    warmup: int
    latency_mean_ms: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    latency_min_ms: float
    latency_max_ms: float
    single_throughput_rps: float
    batch_size: int
    batch_repeats: int
    batch_throughput_tps: float


class InferenceBenchmark:
    """Responsável por medir o desempenho de inferência."""

    @staticmethod
    def measure(
        name: str,
        predict_one: Callable[[str], object],
        predict_batch: Callable[[list[str]], object],
        texts: list[str],
        warmup: int = 100,
        batch_size: int = 256,
        batch_repeats: int = 5,
        timer: Callable[[], float] = time.perf_counter,
    ) -> BenchmarkResult:
        """Mede latência por requisição e throughput em lote."""

        if not texts:
            raise ValueError("A lista de textos não pode estar vazia.")

        if warmup < 0 or batch_size < 1 or batch_repeats < 1:
            raise ValueError("Parâmetros de benchmark inválidos.")

        # O aquecimento não entra nas medições.
        for index in range(warmup):
            predict_one(texts[index % len(texts)])

        latencies = []

        for text in texts:
            start = timer()
            predict_one(text)
            latencies.append(timer() - start)

        batch_elapsed = 0.0

        for _ in range(batch_repeats):
            for offset in range(0, len(texts), batch_size):
                batch = texts[offset:offset + batch_size]

                start = timer()
                predict_batch(batch)
                batch_elapsed += timer() - start

        summary = summarize_latencies(latencies)

        return BenchmarkResult(
            name=name,
            samples=len(texts),
            warmup=warmup,
            latency_mean_ms=summary.mean_ms,
            latency_p50_ms=summary.p50_ms,
            latency_p95_ms=summary.p95_ms,
            latency_p99_ms=summary.p99_ms,
            latency_min_ms=summary.min_ms,
            latency_max_ms=summary.max_ms,
            single_throughput_rps=len(texts) / sum(latencies),
            batch_size=batch_size,
            batch_repeats=batch_repeats,
            batch_throughput_tps=len(texts) * batch_repeats / batch_elapsed,
        )


def collect_environment() -> dict:
    """Coleta as condições do ambiente em que o benchmark foi executado."""

    packages = {}

    for package in BENCHMARKED_PACKAGES:
        try:
            packages[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            packages[package] = "não instalado"

    return {
        "timestamp_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "python_version": platform.python_version(),
        "packages": packages,
        "thread_variables": {
            variable: os.environ[variable]
            for variable in THREAD_VARIABLES
            if variable in os.environ
        },
    }
