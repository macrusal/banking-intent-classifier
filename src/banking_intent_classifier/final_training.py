
"""Treinamento final e avaliação oficial do classificador BANKING77."""

from pathlib import Path

from banking_intent_classifier.application.model_evaluator import ModelEvaluator
from banking_intent_classifier.application.model_trainer import ModelTrainer
from banking_intent_classifier.infrastructure.data.banking77_loader import (
    load_banking77,
)
from banking_intent_classifier.infrastructure.model_repository import (
    ModelRepository,
)


ARTIFACT_PATH = Path("artifacts/baseline_pipeline.joblib")


def main() -> None:
    """Treina no conjunto oficial e avalia no teste reservado."""

    dataset = load_banking77()

    train_split = dataset["train"]
    test_split = dataset["test"]

    pipeline = ModelTrainer.create_baseline_pipeline()

    pipeline.fit(
        train_split["text"],
        train_split["label"],
    )

    predictions = pipeline.predict(test_split["text"])

    result = ModelEvaluator.evaluate(
        configuration="TF-IDF + Logistic Regression | avaliação oficial",
        labels=test_split["label"],
        predictions=predictions,
    )

    ModelRepository.save(pipeline, ARTIFACT_PATH)

    print("AVALIAÇÃO FINAL — BANKING77")
    print("=" * 50)
    print(f"Treinamento oficial: {len(train_split)}")
    print(f"Teste oficial: {len(test_split)}")
    print(f"Accuracy: {result.accuracy:.4f}")
    print(f"Macro F1: {result.macro_f1:.4f}")
    print(f"Weighted F1: {result.weighted_f1:.4f}")
    print(f"Artefato salvo em: {ARTIFACT_PATH}")


if __name__ == "__main__":
    main()
