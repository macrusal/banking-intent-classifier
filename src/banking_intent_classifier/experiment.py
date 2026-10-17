"""Ponto de entrada para execução dos experimentos de pré-processamento."""

from banking_intent_classifier.application.text_preprocessing_experiment import (
    TextPreprocessingExperiment,
)
from banking_intent_classifier.infrastructure.data.banking77_loader import (
    load_banking77,
)


def main() -> None:
    """Executa o experimento comparativo de remoção de stopwords."""

    dataset = load_banking77()

    (
        train_texts,
        validation_texts,
        train_labels,
        validation_labels,
    ) = TextPreprocessingExperiment.prepare_data(dataset)

    results = TextPreprocessingExperiment.compare(
        train_texts=train_texts,
        validation_texts=validation_texts,
        train_labels=train_labels,
        validation_labels=validation_labels,
    )

    print("EXPERIMENTO DE STOPWORDS")
    print("=" * 50)

    for result in results:
        print()
        print(f"Configuração: {result.configuration}")
        print(f"Accuracy: {result.accuracy:.4f}")
        print(f"Macro F1: {result.macro_f1:.4f}")
        print(f"Weighted F1: {result.weighted_f1:.4f}")


if __name__ == "__main__":
    main()