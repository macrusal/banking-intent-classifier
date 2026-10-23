
"""Treinamento final e avaliação oficial do classificador BANKING77."""

from pathlib import Path

from banking_intent_classifier.application.training_service import (
    train_and_evaluate,
)
from banking_intent_classifier.infrastructure.data.banking77_loader import (
    load_banking77,
)
from banking_intent_classifier.infrastructure.label_repository import (
    LabelRepository,
)
from banking_intent_classifier.infrastructure.model_repository import (
    ModelRepository,
)

ARTIFACT_PATH = Path("artifacts/baseline_pipeline.joblib")
LABEL_MAPPING_PATH = Path("artifacts/label_mapping.json")


def load_dataset():
    """Carrega os splits oficiais do BANKING77."""
    return load_banking77()


def save_artifacts(pipeline, labels) -> None:
    """Persiste o modelo e o mapeamento oficial de classes."""
    ModelRepository.save(pipeline, ARTIFACT_PATH)
    LabelRepository.save(labels, LABEL_MAPPING_PATH)


def main() -> None:
    """Executa o fluxo completo de treinamento oficial."""
    dataset = load_dataset()

    pipeline, labels, result = train_and_evaluate(dataset)

    save_artifacts(pipeline, labels)

    print("AVALIAÇÃO FINAL — BANKING77")
    print("=" * 50)
    print(f"Treinamento oficial: {len(dataset['train']['text'])}")
    print(f"Teste oficial: {len(dataset['test']['text'])}")
    print(f"Accuracy: {result.accuracy:.4f}")
    print(f"Macro F1: {result.macro_f1:.4f}")
    print(f"Weighted F1: {result.weighted_f1:.4f}")
    print(f"Artefato salvo em: {ARTIFACT_PATH}")
    print(f"Classes persistidas: {len(labels)}")
    print(f"Mapeamento salvo em: {LABEL_MAPPING_PATH}")


if __name__ == "__main__":
    main()
