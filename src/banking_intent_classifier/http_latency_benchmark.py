"""Baseline de latência HTTP da API de classificação BANKING77."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from banking_intent_classifier.application.http_latency_benchmark import (
    HttpLatencyBenchmark,
)
from banking_intent_classifier.application.inference_benchmark import (
    collect_environment,
)
from banking_intent_classifier.infrastructure.data.banking77_loader import (
    DATASET_NAME,
    DATASET_REVISION,
    load_banking77,
)
from banking_intent_classifier.infrastructure.http_prediction_client import (
    HttpPredictionClient,
)

DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_NAME = "sklearn"
DATASET_SPLIT = "test"
WARMUP = 100
REPORT_DIRECTORY = Path("artifacts")


def parse_arguments(arguments: list[str] | None = None) -> argparse.Namespace:
    """Interpreta os argumentos da linha de comando."""

    parser = argparse.ArgumentParser(
        description="Mede a latência HTTP de POST /predict.",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--name",
        default=DEFAULT_NAME,
        help="Identificação do alvo medido, por exemplo o backend do modelo.",
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=None,
        help="Quantidade de requisições medidas (padrão: split test inteiro).",
    )
    parser.add_argument("--warmup", type=int, default=WARMUP)
    parser.add_argument("--output", type=Path, default=None)

    return parser.parse_args(arguments)


def save_report(report: dict, path: Path) -> None:
    """Persiste o relatório do benchmark em JSON."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)


def main(arguments: list[str] | None = None) -> None:
    """Envia o split de teste à API e registra as latências observadas."""

    options = parse_arguments(arguments)

    if options.requests is not None and options.requests < 1:
        raise ValueError("A quantidade de requisições deve ser positiva.")

    output = options.output or REPORT_DIRECTORY / f"http_latency_{options.name}.json"

    texts = list(load_banking77()[DATASET_SPLIT]["text"])[:options.requests]

    client = HttpPredictionClient(options.base_url)

    try:
        if not client.health():
            raise RuntimeError(
                f"A API não respondeu em {options.base_url}/health."
            )

        result = HttpLatencyBenchmark.measure(
            name=options.name,
            send_request=client.predict,
            texts=texts,
            warmup=options.warmup,
        )
    finally:
        client.close()

    report = {
        "environment": collect_environment(),
        "target": {
            "base_url": options.base_url,
            "endpoint": "POST /predict",
            "name": options.name,
        },
        "dataset": {
            "name": DATASET_NAME,
            "revision": DATASET_REVISION,
            "split": DATASET_SPLIT,
            "samples": len(texts),
        },
        "parameters": {
            "warmup": options.warmup,
            "concurrency": 1,
            "connection": "keep-alive",
        },
        "result": asdict(result),
    }

    save_report(report, output)

    print("BASELINE DE LATÊNCIA HTTP — BANKING77")
    print("=" * 50)
    print(f"Alvo: {options.name} ({options.base_url})")
    print(f"Requisições medidas: {result.samples} (aquecimento: {result.warmup})")
    print(f"  Latência média: {result.latency_mean_ms:.4f} ms")
    print(f"  Latência p50: {result.latency_p50_ms:.4f} ms")
    print(f"  Latência p95: {result.latency_p95_ms:.4f} ms")
    print(f"  Latência p99: {result.latency_p99_ms:.4f} ms")
    print(f"  Latência mín/máx: {result.latency_min_ms:.4f} / {result.latency_max_ms:.4f} ms")
    print(f"  Throughput sequencial: {result.throughput_rps:.1f} req/s")
    print(f"Relatório salvo em: {output}")


if __name__ == "__main__":
    main()
