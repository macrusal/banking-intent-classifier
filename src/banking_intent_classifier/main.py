"""Ponto de entrada da aplicação."""

from banking_intent_classifier.application.dataset_service import DatasetService
from banking_intent_classifier.infrastructure.data.banking77_loader import (
    load_banking77,
)


def main() -> None:
    dataset = load_banking77()

    service = DatasetService()
    summary = service.summarize(dataset)

    print("BANKING77")
    print("-" * 40)
    print(f"Registros de treino: {summary.train.records}")
    print(f"Registros de teste: {summary.test.records}")
    print(f"Total de registros: {summary.total_records}")
    print(f"Classes no treino: {summary.train.classes}")
    print(f"Classes no teste: {summary.test.classes}")


if __name__ == "__main__":
    main()