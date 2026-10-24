"""Testes do benchmark de latência e throughput."""

from importlib import metadata

import numpy as np
import pytest

from banking_intent_classifier.application import inference_benchmark
from banking_intent_classifier.application.inference_benchmark import (
    BENCHMARKED_PACKAGES,
    InferenceBenchmark,
    collect_environment,
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


class RecordingPredictor:
    """Preditor falso que registra as chamadas recebidas."""

    def __init__(self) -> None:
        self.single_calls: list[str] = []
        self.batch_sizes: list[int] = []

    def predict_one(self, text: str) -> int:
        self.single_calls.append(text)
        return 0

    def predict_batch(self, texts: list[str]) -> list[int]:
        self.batch_sizes.append(len(texts))
        return [0] * len(texts)


def run_benchmark(predictor: RecordingPredictor, timer: FakeTimer, **options):
    """Executa o benchmark com preditor e timer falsos."""

    return InferenceBenchmark.measure(
        name="fake",
        predict_one=predictor.predict_one,
        predict_batch=predictor.predict_batch,
        texts=TEXTS,
        timer=timer,
        **options,
    )


def test_should_call_predictors_expected_number_of_times() -> None:
    """Verifica aquecimento circular e tamanhos dos lotes."""

    predictor = RecordingPredictor()

    run_benchmark(
        predictor,
        FakeTimer([]),
        warmup=13,
        batch_size=4,
        batch_repeats=2,
    )

    warmup_calls = predictor.single_calls[:13]

    assert warmup_calls == TEXTS + TEXTS[:3]
    assert predictor.single_calls[13:] == TEXTS
    assert predictor.batch_sizes == [4, 4, 2, 4, 4, 2]


def test_should_compute_metrics_with_constant_latency() -> None:
    """Verifica os cálculos com latência constante de 2 ms."""

    result = run_benchmark(
        RecordingPredictor(),
        FakeTimer([], default=0.002),
        warmup=3,
        batch_size=4,
        batch_repeats=2,
    )

    assert result.name == "fake"
    assert result.samples == 10
    assert result.warmup == 3
    assert result.latency_mean_ms == pytest.approx(2.0)
    assert result.latency_p50_ms == pytest.approx(2.0)
    assert result.latency_p95_ms == pytest.approx(2.0)
    assert result.latency_p99_ms == pytest.approx(2.0)
    assert result.latency_min_ms == pytest.approx(2.0)
    assert result.latency_max_ms == pytest.approx(2.0)
    assert result.single_throughput_rps == pytest.approx(500.0)
    assert result.batch_size == 4
    assert result.batch_repeats == 2
    # 20 textos processados em 6 lotes de 2 ms.
    assert result.batch_throughput_tps == pytest.approx(20 / 0.012)


def test_should_compute_percentiles_with_variable_latency() -> None:
    """Verifica os percentis com latências de 1 a 100 ms."""

    latencies_ms = list(range(1, 101))
    texts = [f"text {index}" for index in range(100)]

    result = InferenceBenchmark.measure(
        name="fake",
        predict_one=lambda text: 0,
        predict_batch=lambda batch: [0] * len(batch),
        texts=texts,
        warmup=0,
        timer=FakeTimer([latency / 1000 for latency in latencies_ms]),
    )

    assert result.latency_p50_ms == pytest.approx(np.percentile(latencies_ms, 50))
    assert result.latency_p95_ms == pytest.approx(np.percentile(latencies_ms, 95))
    assert result.latency_p99_ms == pytest.approx(np.percentile(latencies_ms, 99))
    assert result.latency_min_ms == pytest.approx(1.0)
    assert result.latency_max_ms == pytest.approx(100.0)
    assert result.latency_mean_ms == pytest.approx(50.5)


@pytest.mark.parametrize("warmup", [0, 5, 50])
def test_should_not_measure_warmup_calls(warmup: int) -> None:
    """Verifica que o aquecimento não altera a quantidade medida."""

    predictor = RecordingPredictor()

    result = run_benchmark(predictor, FakeTimer([]), warmup=warmup)

    assert result.samples == len(TEXTS)
    assert len(predictor.single_calls) == warmup + len(TEXTS)


@pytest.mark.parametrize(
    ("texts", "options"),
    [
        ([], {}),
        (TEXTS, {"warmup": -1}),
        (TEXTS, {"batch_size": 0}),
        (TEXTS, {"batch_repeats": 0}),
    ],
    ids=["lista_vazia", "warmup_negativo", "lote_zero", "repeticoes_zero"],
)
def test_should_reject_invalid_parameters(texts: list[str], options: dict) -> None:
    """Verifica a rejeição de parâmetros inválidos."""

    with pytest.raises(ValueError):
        InferenceBenchmark.measure(
            name="fake",
            predict_one=lambda text: 0,
            predict_batch=lambda batch: [0] * len(batch),
            texts=texts,
            timer=FakeTimer([]),
            **options,
        )


def test_should_collect_environment() -> None:
    """Verifica as informações coletadas do ambiente."""

    environment = collect_environment()

    assert set(environment) == {
        "timestamp_utc",
        "platform",
        "machine",
        "processor",
        "cpu_count",
        "python_version",
        "packages",
        "thread_variables",
    }
    assert set(environment["packages"]) == set(BENCHMARKED_PACKAGES)


def test_should_mark_missing_packages(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifica a indicação de pacotes não instalados."""

    def missing_version(package: str) -> str:
        raise metadata.PackageNotFoundError(package)

    monkeypatch.setattr(inference_benchmark.metadata, "version", missing_version)

    environment = collect_environment()

    assert set(environment["packages"].values()) == {"não instalado"}


def test_should_collect_thread_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifica o registro das variáveis de threads definidas."""

    monkeypatch.setenv("OMP_NUM_THREADS", "1")
    monkeypatch.delenv("MKL_NUM_THREADS", raising=False)

    environment = collect_environment()

    assert environment["thread_variables"] == {"OMP_NUM_THREADS": "1"}
