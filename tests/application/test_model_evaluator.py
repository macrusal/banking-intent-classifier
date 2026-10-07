import pytest

from banking_intent_classifier.application.model_evaluator import (
    ModelEvaluator,
)


def test_should_calculate_classification_metrics() -> None:
    labels = [0, 0, 1, 1]
    predictions = [0, 0, 1, 0]

    result = ModelEvaluator.evaluate(
        configuration="test-configuration",
        labels=labels,
        predictions=predictions,
    )

    assert result.configuration == "test-configuration"
    assert result.accuracy == pytest.approx(0.75)
    assert result.macro_f1 == pytest.approx(0.733333, rel=1e-5)
    assert result.weighted_f1 == pytest.approx(0.733333, rel=1e-5)