
"""Persistência dos nomes das classes do classificador."""

import json
from pathlib import Path


class LabelRepository:
    """Salva e recupera o mapeamento de identificadores para intenções."""

    @staticmethod
    def save(labels: list[str], path: Path) -> None:
        """Salva os nomes das classes na ordem oficial do dataset."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(labels, file, ensure_ascii=False, indent=2)

    @staticmethod
    def load(path: Path) -> list[str]:
        """Recupera os nomes das classes persistidos."""
        path = Path(path)

        with path.open(encoding="utf-8") as file:
            labels = json.load(file)

        if (
            not isinstance(labels, list)
            or not labels
            or not all(isinstance(label, str) and label for label in labels)
        ):
            raise ValueError("Mapeamento de classes inválido.")

        return labels
