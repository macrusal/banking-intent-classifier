"""Testes da comparação de predições entre Scikit-learn e ONNX."""

import numpy as np
import pytest

from banking_intent_classifier.application.model_equivalence import (
    ModelEquivalenceChecker,
    PredictionMismatch,
)

LABEL_NAMES = ["balance", "card_arrival", "lost_card"]


def test_should_report_full_agreement() -> None:
    """Verifica o resultado quando os modelos concordam em tudo."""

    labels = [0, 1, 2, 1]

    result = ModelEquivalenceChecker.compare(
        texts=["a", "b", "c", "d"],
        true_labels=labels,
        sklearn_predictions=labels,
        onnx_predictions=labels,
        label_names=LABEL_NAMES,
    )

    assert result.total == 4
    assert result.agreements == 4
    assert result.agreement_rate == 1.0
    assert result.mismatch_count == 0
    assert result.mismatches == []
    assert result.sklearn_metrics.accuracy == result.onnx_metrics.accuracy
    assert result.sklearn_metrics.macro_f1 == result.onnx_metrics.macro_f1


def test_should_report_mismatch_details() -> None:
    """Verifica as contagens e os detalhes de uma divergência."""

    result = ModelEquivalenceChecker.compare(
        texts=["a", "b", "c", "d"],
        true_labels=[0, 1, 2, 1],
        sklearn_predictions=[0, 1, 2, 1],
        onnx_predictions=[0, 2, 2, 1],
        label_names=LABEL_NAMES,
    )

    assert result.agreements == 3
    assert result.agreement_rate == 0.75
    assert result.mismatch_count == 1
    assert result.mismatches == [
        PredictionMismatch(
            index=1,
            text="b",
            sklearn_label_id=1,
            sklearn_label="card_arrival",
            onnx_label_id=2,
            onnx_label="lost_card",
        )
    ]
    assert result.sklearn_metrics.accuracy == 1.0
    assert result.onnx_metrics.accuracy == 0.75


def test_should_limit_listed_mismatches_but_keep_exact_count() -> None:
    """Verifica o limite da lista de divergências."""

    result = ModelEquivalenceChecker.compare(
        texts=["a", "b", "c", "d", "e"],
        true_labels=[0, 0, 0, 0, 0],
        sklearn_predictions=[0, 0, 0, 0, 0],
        onnx_predictions=[1, 1, 1, 1, 1],
        label_names=LABEL_NAMES,
        max_mismatches=2,
    )

    assert result.mismatch_count == 5
    assert [mismatch.index for mismatch in result.mismatches] == [0, 1]


def test_should_convert_numpy_labels_to_int() -> None:
    """Verifica a conversão de rótulos NumPy para int."""

    result = ModelEquivalenceChecker.compare(
        texts=["a", "b"],
        true_labels=np.array([0, 1], dtype=np.int64),
        sklearn_predictions=np.array([0, 1], dtype=np.int64),
        onnx_predictions=np.array([0, 2], dtype=np.int64),
        label_names=LABEL_NAMES,
    )

    mismatch = result.mismatches[0]

    assert type(mismatch.sklearn_label_id) is int
    assert type(mismatch.onnx_label_id) is int


@pytest.mark.parametrize(
    ("texts", "true_labels", "sklearn_predictions", "onnx_predictions"),
    [
        (["a", "b"], [0, 1], [0, 1], [0]),
        ([], [], [], []),
        (["a"], [0], [3], [0]),
        (["a"], [0], [0], [3]),
        (["a"], [0], [0], [-1]),
    ],
    ids=[
        "tamanhos_diferentes",
        "lista_vazia",
        "sklearn_fora_do_mapeamento",
        "onnx_fora_do_mapeamento",
        "predicao_negativa",
    ],
)
def test_should_reject_invalid_inputs(
    texts,
    true_labels,
    sklearn_predictions,
    onnx_predictions,
) -> None:
    """Verifica a rejeição de entradas inválidas."""

    with pytest.raises(ValueError):
        ModelEquivalenceChecker.compare(
            texts=texts,
            true_labels=true_labels,
            sklearn_predictions=sklearn_predictions,
            onnx_predictions=onnx_predictions,
            label_names=LABEL_NAMES,
        )


def test_should_accept_valid_label_mapping() -> None:
    """Verifica a aceitação de classes 0..N-1."""

    ModelEquivalenceChecker.check_label_mapping(
        np.arange(len(LABEL_NAMES)),
        LABEL_NAMES,
    )


@pytest.mark.parametrize(
    "classes",
    [[0, 2, 1], [0, 1], [0, 1, 2, 3]],
    ids=["ordem_trocada", "classe_faltando", "classe_a_mais"],
)
def test_should_reject_invalid_label_mapping(classes: list[int]) -> None:
    """Verifica a rejeição de classes incompatíveis com o mapeamento."""

    with pytest.raises(ValueError):
        ModelEquivalenceChecker.check_label_mapping(classes, LABEL_NAMES)
