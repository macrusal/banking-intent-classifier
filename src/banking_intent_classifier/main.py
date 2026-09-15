"""Ponto de entrada da aplicação."""

from banking_intent_classifier.application.dataset_service import DatasetService
from banking_intent_classifier.infrastructure.data.banking77_loader import (
    load_banking77,
)


def print_split_summary(name: str, summary) -> None:
    """Exibe o resumo de um split."""

    print(f"\n{name}")
    print("-" * 40)
    print(f"Registros: {summary.records}")
    print(f"Classes: {summary.classes}")
    print(f"Textos ausentes: {summary.missing_texts}")
    print(f"Labels ausentes: {summary.missing_labels}")
    print(f"Textos vazios: {summary.empty_texts}")
    print(f"Registros duplicados: {summary.duplicated_records}")


def main() -> None:
    """Carrega e valida informações básicas do BANKING77."""

    dataset = load_banking77()

    service = DatasetService()
    summary = service.summarize(dataset)

    print("BANKING77")
    print("=" * 40)
    print(f"Total de registros: {summary.total_records}")
    print(
        "Mesmas classes em treino e teste: "
        f"{summary.same_classes_in_splits}"
    )

    print_split_summary("TREINO", summary.train)
    print_split_summary("TESTE", summary.test)

    print(
        "Textos presentes em treino e teste: "
        f"{summary.overlapping_texts}"
    )

    distribution = service.class_distribution(dataset, "train")
    distribution_summary = service.summarize_class_distribution(distribution)

    print("\nDISTRIBUIÇÃO DAS CLASSES — TREINO")
    print("-" * 40)

    for intent, count in distribution.items():
        print(f" {intent}: {count}")

    print("\nRESUMO DA DISTRIBUIÇÃO")
    print("-" * 40)
    print(f"Mínimo: {distribution_summary.minimum}")
    print(f"Máximo: {distribution_summary.maximum}")
    print(f"Média: {distribution_summary.mean:.2f}")
    print(f"Mediana: {distribution_summary.median:.2f}")

if __name__ == "__main__":
    main()