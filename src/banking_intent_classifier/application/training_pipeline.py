
"""Operações reutilizáveis do pipeline de treinamento."""
import json
import shutil
from pathlib import Path

from banking_intent_classifier.application.training_service import (
    train_and_evaluate,
)
from banking_intent_classifier.infrastructure.data.banking77_loader import (
    load_banking77,
)
from banking_intent_classifier.infrastructure.data.dataset_repository import (
    DatasetRepository,
)
from banking_intent_classifier.infrastructure.label_repository import (
    LabelRepository,
)
from banking_intent_classifier.infrastructure.model_repository import (
    ModelRepository,
)


def ingest_data(dataset_path: Path) -> Path:
    """Carrega, valida e persiste o BANKING77 para treinamento."""

    dataset_path = Path(dataset_path)

    dataset = load_banking77()

    DatasetRepository.save(dataset, dataset_path)

    return dataset_path

def train_model(dataset_path: Path, output_path: Path) -> Path:
    """Treina, avalia e persiste os resultados intermediários."""

    dataset = DatasetRepository.load(dataset_path)

    pipeline, labels, result = train_and_evaluate(dataset)

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    ModelRepository.save(
        pipeline,
        output_path / "pipeline.joblib",
    )

    LabelRepository.save(
        labels,
        output_path / "label_mapping.json",
    )

    metrics = {
        "accuracy": result.accuracy,
        "macro_f1": result.macro_f1,
        "weighted_f1": result.weighted_f1,
    }

    with (output_path / "metrics.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(metrics, file, indent=2)

    return output_path


def save_artifacts(
    training_path: Path,
    artifact_path: Path,
    label_mapping_path: Path,
) -> None:
    """Publica os artefatos treinados nos caminhos finais."""

    training_path = Path(training_path)
    artifact_path = Path(artifact_path)
    label_mapping_path = Path(label_mapping_path)

    source_model = training_path / "pipeline.joblib"
    source_labels = training_path / "label_mapping.json"
    source_metrics = training_path / "metrics.json"

    if not all(
        path.is_file()
        for path in (source_model, source_labels, source_metrics)
    ):
        raise FileNotFoundError(
            "Artefatos intermediários de treinamento incompletos."
        )

    # Valida os arquivos antes da publicação.
    ModelRepository.load(source_model)
    LabelRepository.load(source_labels)

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    label_mapping_path.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(source_model, artifact_path)
    shutil.copy2(source_labels, label_mapping_path)
