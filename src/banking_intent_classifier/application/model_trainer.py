"""Treinamento do modelo de classificação."""

from sklearn.linear_model import LogisticRegression


class ModelTrainer:
    """Responsável pelo treinamento do classificador."""

    @staticmethod
    def create_classifier() -> LogisticRegression:
        """Cria o classificador utilizado no baseline."""

        return LogisticRegression(
            max_iter=1000,
        )

    @staticmethod
    def train(
        classifier: LogisticRegression,
        features,
        labels: list[int],
    ) -> LogisticRegression:
        """Treina o classificador com as features e labels fornecidas."""

        classifier.fit(features, labels)

        return classifier