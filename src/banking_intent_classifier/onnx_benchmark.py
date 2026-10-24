"""Exportação ONNX, equivalência e benchmark do classificador BANKING77."""

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from banking_intent_classifier.application.inference_benchmark import (
    InferenceBenchmark,
    collect_environment,
)
from banking_intent_classifier.application.model_equivalence import (
    ModelEquivalenceChecker,
)
from banking_intent_classifier.application.onnx_prediction_service import (
    OnnxPredictionService,
)
from banking_intent_classifier.application.prediction_service import (
    PredictionService,
)
from banking_intent_classifier.infrastructure.data.banking77_loader import (
    DATASET_NAME,
    DATASET_REVISION,
    load_banking77,
)
from banking_intent_classifier.infrastructure.label_repository import (
    LabelRepository,
)
from banking_intent_classifier.infrastructure.model_repository import (
    ModelRepository,
)
from banking_intent_classifier.infrastructure.onnx_model_repository import (
    OnnxModelRepository,
)

ARTIFACT_PATH = Path("artifacts/baseline_pipeline.joblib")
LABEL_MAPPING_PATH = Path("artifacts/label_mapping.json")
ONNX_ARTIFACT_PATH = Path("artifacts/baseline_pipeline.onnx")
REPORT_PATH = Path("artifacts/onnx_benchmark.json")

DATASET_SPLIT = "test"
WARMUP = 100
BATCH_SIZE = 256
BATCH_REPEATS = 5


def describe_artifact(path: Path) -> dict:
    """Retorna caminho, tamanho e hash SHA-256 de um artefato."""

    path = Path(path)

    return {
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def save_report(report: dict, path: Path) -> None:
    """Persiste o relatório do benchmark em JSON."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)


def main() -> None:
    """Exporta o modelo, verifica a equivalência e mede o desempenho."""

    pipeline = ModelRepository.load(ARTIFACT_PATH)
    labels = LabelRepository.load(LABEL_MAPPING_PATH)

    ModelEquivalenceChecker.check_label_mapping(pipeline[-1].classes_, labels)

    dataset = load_banking77()
    test_split = dataset[DATASET_SPLIT]

    if test_split.features["label"].names != labels:
        raise ValueError(
            "O mapeamento de classes difere das classes do dataset."
        )

    OnnxModelRepository.export(pipeline, ONNX_ARTIFACT_PATH)

    onnx_service = OnnxPredictionService(
        OnnxModelRepository.load(ONNX_ARTIFACT_PATH)
    )
    sklearn_service = PredictionService(pipeline)

    texts = list(test_split["text"])
    true_labels = list(test_split["label"])

    equivalence = ModelEquivalenceChecker.compare(
        texts=texts,
        true_labels=true_labels,
        sklearn_predictions=pipeline.predict(texts),
        onnx_predictions=onnx_service.predict_batch(texts),
        label_names=labels,
    )

    # Ordem fixa e mesmos parâmetros para os dois modelos.
    benchmarks = [
        InferenceBenchmark.measure(
            name="Scikit-learn",
            predict_one=sklearn_service.predict,
            predict_batch=pipeline.predict,
            texts=texts,
            warmup=WARMUP,
            batch_size=BATCH_SIZE,
            batch_repeats=BATCH_REPEATS,
        ),
        InferenceBenchmark.measure(
            name="ONNX Runtime",
            predict_one=onnx_service.predict,
            predict_batch=onnx_service.predict_batch,
            texts=texts,
            warmup=WARMUP,
            batch_size=BATCH_SIZE,
            batch_repeats=BATCH_REPEATS,
        ),
    ]

    report = {
        "environment": collect_environment(),
        "dataset": {
            "name": DATASET_NAME,
            "revision": DATASET_REVISION,
            "split": DATASET_SPLIT,
            "samples": len(texts),
        },
        "artifacts": {
            "sklearn": describe_artifact(ARTIFACT_PATH),
            "onnx": describe_artifact(ONNX_ARTIFACT_PATH),
        },
        "parameters": {
            "warmup": WARMUP,
            "batch_size": BATCH_SIZE,
            "batch_repeats": BATCH_REPEATS,
            "execution_order": [benchmark.name for benchmark in benchmarks],
        },
        "equivalence": asdict(equivalence),
        "benchmarks": [asdict(benchmark) for benchmark in benchmarks],
    }

    save_report(report, REPORT_PATH)

    print("BENCHMARK ONNX — BANKING77")
    print("=" * 50)
    print(f"Amostras ({DATASET_SPLIT}): {equivalence.total}")
    print(f"Concordância: {equivalence.agreement_rate:.4%}")
    print(f"Divergências: {equivalence.mismatch_count}")
    print(f"Accuracy Scikit-learn: {equivalence.sklearn_metrics.accuracy:.4f}")
    print(f"Accuracy ONNX: {equivalence.onnx_metrics.accuracy:.4f}")

    if equivalence.mismatch_count:
        print("Aviso: há divergências entre os modelos; consulte o relatório.")

    for benchmark in benchmarks:
        print()
        print(f"{benchmark.name}")
        print(f"  Latência p50: {benchmark.latency_p50_ms:.4f} ms")
        print(f"  Latência p95: {benchmark.latency_p95_ms:.4f} ms")
        print(f"  Latência p99: {benchmark.latency_p99_ms:.4f} ms")
        print(f"  Throughput individual: {benchmark.single_throughput_rps:.1f} req/s")
        print(f"  Throughput em lote: {benchmark.batch_throughput_tps:.1f} textos/s")

    print()
    print(f"Tamanho Scikit-learn: {report['artifacts']['sklearn']['size_bytes']} bytes")
    print(f"Tamanho ONNX: {report['artifacts']['onnx']['size_bytes']} bytes")
    print(f"Relatório salvo em: {REPORT_PATH}")


if __name__ == "__main__":
    main()
