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

if __name__ == "__main__":
    main()