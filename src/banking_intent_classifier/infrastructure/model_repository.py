
"""Persistência do Pipeline de classificação."""

from pathlib import Path

import joblib
from sklearn.pipeline import Pipeline


class ModelRepository:
    """Responsável por salvar e carregar modelos treinados."""

    @staticmethod
    def save(model: Pipeline, path: Path) -> None:
        """Persiste um Pipeline treinado."""

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(model, path)

    @staticmethod
    def load(path: Path) -> Pipeline:
        """Carrega um Pipeline previamente persistido."""

        path = Path(path)

        model = joblib.load(path)

        if not isinstance(model, Pipeline):
            raise TypeError(
                "O artefato carregado não é um Pipeline."
            )

        return model
