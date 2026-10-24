"""Testes da orquestração do benchmark ONNX."""

import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest

pytest.importorskip("onnxruntime")
pytest.importorskip("skl2onnx")

from datasets import ClassLabel, Dataset, DatasetDict, Features, Value

from banking_intent_classifier import onnx_benchmark
from banking_intent_classifier.application.model_trainer import ModelTrainer
from banking_intent_classifier.infrastructure.label_repository import (
    LabelRepository,
)
from banking_intent_classifier.infrastructure.model_repository import (
    ModelRepository,
)

LABEL_NAMES = ["balance", "card_arrival"]

TRAIN_TEXTS = [
    "check my account balance",
    "what is my current balance",
    "how much money is in my account",
    "my card has not arrived",
    "where is my new card",
    "when will my card arrive",
]

TRAIN_LABELS = [0, 0, 0, 1, 1, 1]

TEST_TEXTS = [
    "show my balance",
    "I am waiting for my card",
    "balance please",
]

TEST_LABELS = [0, 1, 0]


def create_dataset(label_names: list[str]) -> DatasetDict:
    """Cria um dataset pequeno com a estrutura do BANKING77."""

    features = Features(
        {"text": Value("string"), "label": ClassLabel(names=label_names)}
    )

    return DatasetDict(
        {
            "train": Dataset.from_dict(
                {"text": TRAIN_TEXTS, "label": TRAIN_LABELS},
                features=features,
            ),
            "test": Dataset.from_dict(
                {"text": TEST_TEXTS, "label": TEST_LABELS},
                features=features,
            ),
        }
    )


def prepare_artifacts(tmp_path: Path) -> tuple[Path, Path]:
    """Treina e persiste um modelo pequeno com seu mapeamento."""

    pipeline = ModelTrainer.create_baseline_pipeline()
    pipeline.fit(TRAIN_TEXTS, TRAIN_LABELS)

    artifact_path = tmp_path / "baseline_pipeline.joblib"
    label_mapping_path = tmp_path / "label_mapping.json"

    ModelRepository.save(pipeline, artifact_path)
    LabelRepository.save(LABEL_NAMES, label_mapping_path)

    return artifact_path, label_mapping_path


def run_main(tmp_path: Path, dataset: DatasetDict) -> tuple[Path, Path]:
    """Executa a CLI com caminhos temporários e parâmetros reduzidos."""

    artifact_path, label_mapping_path = prepare_artifacts(tmp_path)
    onnx_path = tmp_path / "baseline_pipeline.onnx"
    report_path = tmp_path / "reports" / "onnx_benchmark.json"

    with (
        patch.object(onnx_benchmark, "load_banking77", return_value=dataset),
        patch.object(onnx_benchmark, "ARTIFACT_PATH", artifact_path),
        patch.object(onnx_benchmark, "LABEL_MAPPING_PATH", label_mapping_path),
        patch.object(onnx_benchmark, "ONNX_ARTIFACT_PATH", onnx_path),
        patch.object(onnx_benchmark, "REPORT_PATH", report_path),
        patch.object(onnx_benchmark, "WARMUP", 2),
        patch.object(onnx_benchmark, "BATCH_SIZE", 2),
        patch.object(onnx_benchmark, "BATCH_REPEATS", 1),
    ):
        onnx_benchmark.main()

    return onnx_path, report_path


def test_should_export_compare_benchmark_and_save_report(
    tmp_path: Path,
    capsys,
) -> None:
    """Valida o fluxo completo da CLI e o conteúdo do relatório."""

    onnx_path, report_path = run_main(tmp_path, create_dataset(LABEL_NAMES))

    assert onnx_path.is_file()
    assert report_path.is_file()

    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert set(report) == {
        "environment",
        "dataset",
        "artifacts",
        "parameters",
        "equivalence",
        "benchmarks",
    }
    assert report["dataset"]["split"] == "test"
    assert report["dataset"]["samples"] == len(TEST_TEXTS)
    assert report["equivalence"]["agreement_rate"] == 1.0
    assert report["equivalence"]["mismatch_count"] == 0
    assert report["parameters"] == {
        "warmup": 2,
        "batch_size": 2,
        "batch_repeats": 1,
        "execution_order": ["Scikit-learn", "ONNX Runtime"],
    }
    assert [benchmark["name"] for benchmark in report["benchmarks"]] == [
        "Scikit-learn",
        "ONNX Runtime",
    ]
    assert all(
        benchmark["samples"] == len(TEST_TEXTS)
        for benchmark in report["benchmarks"]
    )

    onnx_artifact = report["artifacts"]["onnx"]

    assert onnx_artifact["size_bytes"] == onnx_path.stat().st_size
    assert onnx_artifact["sha256"] == hashlib.sha256(
        onnx_path.read_bytes()
    ).hexdigest()

    output = capsys.readouterr().out

    assert "BENCHMARK ONNX — BANKING77" in output
    assert "Concordância: 100.0000%" in output
    assert "Aviso" not in output


def test_should_reject_dataset_with_different_classes(tmp_path: Path) -> None:
    """Verifica a interrupção quando o dataset diverge do mapeamento."""

    dataset = create_dataset(["card_arrival", "balance"])

    with pytest.raises(ValueError, match="mapeamento de classes"):
        run_main(tmp_path, dataset)

    assert not (tmp_path / "baseline_pipeline.onnx").exists()


def test_should_describe_artifact(tmp_path: Path) -> None:
    """Verifica tamanho e hash SHA-256 de um artefato."""

    path = tmp_path / "artifact.bin"
    path.write_bytes(b"banking77")

    description = onnx_benchmark.describe_artifact(path)

    assert description == {
        "path": str(path),
        "size_bytes": 9,
        "sha256": hashlib.sha256(b"banking77").hexdigest(),
    }


def test_should_save_report_with_readable_accents(tmp_path: Path) -> None:
    """Verifica a criação do diretório e o JSON em UTF-8."""

    path = tmp_path / "reports" / "onnx_benchmark.json"

    onnx_benchmark.save_report({"status": "não instalado"}, path)

    content = path.read_text(encoding="utf-8")

    assert "não instalado" in content
    assert json.loads(content) == {"status": "não instalado"}
