"""Divisão dos dados para treinamento e validação."""

from sklearn.model_selection import train_test_split


class DatasetSplitter:
    """Responsável por criar conjuntos de treino e validação."""

    @staticmethod
    def split(
        texts: list[str],
        labels: list[int],
        validation_size: float = 0.2,
        random_state: int = 42,
    ) -> tuple[list[str], list[str], list[int], list[int]]:
        """Divide os dados preservando a distribuição das classes."""

        return train_test_split(
            texts,
            labels,
            test_size=validation_size,
            random_state=random_state,
            stratify=labels,
        )