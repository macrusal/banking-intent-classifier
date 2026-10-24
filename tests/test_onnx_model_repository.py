"""Testes de exportação e carregamento do Pipeline em ONNX."""

from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("onnxruntime")
pytest.importorskip("skl2onnx")

from onnx import TensorProto, helper

from banking_intent_classifier.application.model_trainer import (
    ModelTrainer,
)
from banking_intent_classifier.infrastructure.onnx_model_repository import (
    INPUT_NAME,
    OnnxModelRepository,
)

TEXTS = [
    "I want to check my balance",
    "My card has been stolen",
    "How much money do I have",
    "I need to block my stolen card",
]

LABELS = [0, 1, 0, 1]


def create_trained_pipeline():
    """Cria um Pipeline pequeno treinado em memória."""

    pipeline = ModelTrainer.create_baseline_pipeline()
    pipeline.fit(TEXTS, LABELS)

    return pipeline


def test_should_export_and_load_pipeline_with_same_predictions(
    tmp_path: Path,
) -> None:
    """Verifica se o modelo ONNX reproduz as predições do Scikit-learn."""

    pipeline = create_trained_pipeline()
    artifact_path = tmp_path / "baseline_pipeline.onnx"

    OnnxModelRepository.export(pipeline, artifact_path)

    assert artifact_path.is_file()

    session = OnnxModelRepository.load(artifact_path)

    inputs = np.array(TEXTS, dtype=object).reshape(-1, 1)
    onnx_labels = session.run(None, {INPUT_NAME: inputs})[0]

    assert onnx_labels.tolist() == pipeline.predict(TEXTS).tolist()


def test_should_create_parent_directory_on_export(tmp_path: Path) -> None:
    """Verifica a criação do diretório de destino do artefato."""

    artifact_path = tmp_path / "models" / "onnx" / "baseline_pipeline.onnx"

    OnnxModelRepository.export(create_trained_pipeline(), artifact_path)

    assert artifact_path.is_file()


def test_should_reject_export_of_non_pipeline(tmp_path: Path) -> None:
    """Verifica que apenas Pipelines podem ser exportados."""

    classifier = ModelTrainer.create_classifier()

    with pytest.raises(TypeError):
        OnnxModelRepository.export(classifier, tmp_path / "model.onnx")


def test_should_reject_onnx_model_without_text_input(tmp_path: Path) -> None:
    """Verifica que modelos com entrada não textual são recusados."""

    graph = helper.make_graph(
        nodes=[helper.make_node("Identity", ["x"], ["y"])],
        name="float_identity",
        inputs=[helper.make_tensor_value_info("x", TensorProto.FLOAT, [None])],
        outputs=[helper.make_tensor_value_info("y", TensorProto.FLOAT, [None])],
    )
    model = helper.make_model(
        graph,
        opset_imports=[helper.make_opsetid("", 13)],
        ir_version=8,
    )

    artifact_path = tmp_path / "float_identity.onnx"
    artifact_path.write_bytes(model.SerializeToString())

    with pytest.raises(TypeError):
        OnnxModelRepository.load(artifact_path)
