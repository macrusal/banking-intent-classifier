
"""Persistência intermediária de datasets para pipelines."""

from pathlib import Path

from datasets import DatasetDict, load_from_disk

from banking_intent_classifier.infrastructure.data.banking77_loader import (
    validate_dataset,
)


class DatasetRepository:
    """Salva e recupera datasets entre etapas do pipeline."""

    @staticmethod
    def save(dataset: DatasetDict, path: Path) -> None:
        """Persiste os splits do dataset em disco."""
        validate_dataset(dataset)

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        dataset.save_to_disk(str(path))

    @staticmethod
    def load(path: Path) -> DatasetDict:
        """Carrega e valida um dataset persistido."""
        path = Path(path)

        dataset = load_from_disk(str(path))

        if not isinstance(dataset, DatasetDict):
            raise TypeError(
                "O artefato carregado não é um DatasetDict."
            )

        validate_dataset(dataset)

        return dataset
