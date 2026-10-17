"""Execução reproduzível do baseline de classificação textual."""

from banking_intent_classifier.application.dataset_splitter import (
    DatasetSplitter,
)
from banking_intent_classifier.application.model_evaluator import (
    ModelEvaluator,
)
from banking_intent_classifier.application.model_trainer import (
    ModelTrainer,
)
from banking_intent_classifier.infrastructure.data.banking77_loader import (
    load_banking77,
)


def main() -> None:
    """Treina e avalia o baseline utilizando validação interna."""

    dataset = load_banking77()

    # O conjunto oficial de teste permanece intocado.
    train_split = dataset["train"]

    (
        train_texts,
        validation_texts,
        train_labels,
        validation_labels,
    ) = DatasetSplitter.split(
        texts=train_split["text"],
        labels=train_split["label"],
    )

    pipeline = ModelTrainer.create_baseline_pipeline()

    pipeline.fit(train_texts, train_labels)

    predictions = pipeline.predict(validation_texts)

    result = ModelEvaluator.evaluate(
        configuration="TF-IDF + Logistic Regression | stop_words=None",
        labels=validation_labels,
        predictions=predictions,
    )

    print("BASELINE FORMAL — BANKING77")
    print("=" * 50)
    print(f"Treino interno: {len(train_texts)}")
    print(f"Validação interna: {len(validation_texts)}")
    print(f"Configuração: {result.configuration}")
    print(f"Accuracy: {result.accuracy:.4f}")
    print(f"Macro F1: {result.macro_f1:.4f}")
    print(f"Weighted F1: {result.weighted_f1:.4f}")


if __name__ == "__main__":
    main()