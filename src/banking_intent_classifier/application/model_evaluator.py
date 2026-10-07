"""Avaliação do modelo de classificação."""

from sklearn.metrics import accuracy_score, f1_score

from banking_intent_classifier.domain.experiment_result import (
    ExperimentResult,
)


class ModelEvaluator:
    """Responsável por avaliar as predições do classificador."""

    @staticmethod
    def evaluate(
        configuration: str,
        labels: list[int],
        predictions: list[int],
    ) -> ExperimentResult:
        """Calcula as métricas utilizadas no experimento."""

        return ExperimentResult(
            configuration=configuration,
            accuracy=accuracy_score(labels, predictions),
            macro_f1=f1_score(
                labels,
                predictions,
                average="macro",
            ),
            weighted_f1=f1_score(
                labels,
                predictions,
                average="weighted",
            ),
        )