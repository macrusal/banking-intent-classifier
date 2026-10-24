"""Comparação de predições entre o modelo Scikit-learn e o ONNX."""

from dataclasses import dataclass

from banking_intent_classifier.application.model_evaluator import ModelEvaluator
from banking_intent_classifier.domain.experiment_result import (
    ExperimentResult,
)

MAX_MISMATCHES = 50


@dataclass(frozen=True)
class PredictionMismatch:
    """Representa um texto classificado de forma diferente pelos modelos."""

    index: int
    text: str
    sklearn_label_id: int
    sklearn_label: str
    onnx_label_id: int
    onnx_label: str


@dataclass(frozen=True)
class EquivalenceResult:
    """Representa a comparação entre as predições dos dois modelos."""

    total: int
    agreements: int
    agreement_rate: float
    mismatch_count: int
    mismatches: list[PredictionMismatch]
    sklearn_metrics: ExperimentResult
    onnx_metrics: ExperimentResult


class ModelEquivalenceChecker:
    """Responsável por verificar a equivalência entre os modelos."""

    @staticmethod
    def check_label_mapping(classes, label_names: list[str]) -> None:
        """Garante que os identificadores das classes são 0..N-1."""

        expected = list(range(len(label_names)))
        actual = [int(label) for label in classes]

        if actual != expected:
            raise ValueError(
                "As classes do modelo não correspondem ao mapeamento "
                f"de {len(label_names)} intenções."
            )

    @staticmethod
    def compare(
        texts: list[str],
        true_labels: list[int],
        sklearn_predictions: list[int],
        onnx_predictions: list[int],
        label_names: list[str],
        max_mismatches: int = MAX_MISMATCHES,
    ) -> EquivalenceResult:
        """Compara as predições e calcula as métricas de cada modelo."""

        sizes = {
            len(texts),
            len(true_labels),
            len(sklearn_predictions),
            len(onnx_predictions),
        }

        if len(sizes) != 1:
            raise ValueError(
                "Textos, rótulos e predições devem ter o mesmo tamanho."
            )

        if not texts:
            raise ValueError("A lista de textos não pode estar vazia.")

        true_labels = [int(label) for label in true_labels]
        sklearn_predictions = [int(label) for label in sklearn_predictions]
        onnx_predictions = [int(label) for label in onnx_predictions]

        valid_ids = range(len(label_names))

        if any(
            label not in valid_ids
            for label in sklearn_predictions + onnx_predictions
        ):
            raise ValueError(
                "Há predições fora do mapeamento de classes."
            )

        mismatch_indexes = [
            index
            for index, (sklearn_label, onnx_label) in enumerate(
                zip(sklearn_predictions, onnx_predictions)
            )
            if sklearn_label != onnx_label
        ]

        mismatches = [
            PredictionMismatch(
                index=index,
                text=texts[index],
                sklearn_label_id=sklearn_predictions[index],
                sklearn_label=label_names[sklearn_predictions[index]],
                onnx_label_id=onnx_predictions[index],
                onnx_label=label_names[onnx_predictions[index]],
            )
            for index in mismatch_indexes[:max_mismatches]
        ]

        total = len(texts)
        agreements = total - len(mismatch_indexes)

        return EquivalenceResult(
            total=total,
            agreements=agreements,
            agreement_rate=agreements / total,
            mismatch_count=len(mismatch_indexes),
            mismatches=mismatches,
            sklearn_metrics=ModelEvaluator.evaluate(
                configuration="Scikit-learn",
                labels=true_labels,
                predictions=sklearn_predictions,
            ),
            onnx_metrics=ModelEvaluator.evaluate(
                configuration="ONNX Runtime",
                labels=true_labels,
                predictions=onnx_predictions,
            ),
        )
