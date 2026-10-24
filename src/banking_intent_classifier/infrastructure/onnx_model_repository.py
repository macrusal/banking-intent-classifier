"""Exportação e carregamento do Pipeline de classificação em ONNX."""

from pathlib import Path

from onnxruntime import InferenceSession
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import StringTensorType
from sklearn.pipeline import Pipeline

INPUT_NAME = "text"
# Nome fixo: sem ele, o skl2onnx gera um UUID por exportação e o hash muda.
GRAPH_NAME = "banking77_intent_classifier"
EXECUTION_PROVIDERS = ["CPUExecutionProvider"]


class OnnxModelRepository:
    """Responsável por exportar e carregar modelos no formato ONNX."""

    @staticmethod
    def export(model: Pipeline, path: Path) -> None:
        """Converte um Pipeline treinado e persiste o modelo ONNX."""

        if not isinstance(model, Pipeline):
            raise TypeError(
                "O modelo a exportar não é um Pipeline."
            )

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Sem ZipMap, as probabilidades saem como tensor, não como dicionários.
        onnx_model = convert_sklearn(
            model,
            initial_types=[(INPUT_NAME, StringTensorType([None, 1]))],
            options={id(model[-1]): {"zipmap": False}},
            name=GRAPH_NAME,
        )

        # A ordem dos opsets vem de um set e varia com o PYTHONHASHSEED.
        opsets = sorted(
            (opset.domain, opset.version)
            for opset in onnx_model.opset_import
        )
        del onnx_model.opset_import[:]

        for domain, version in opsets:
            onnx_model.opset_import.add(domain=domain, version=version)

        path.write_bytes(onnx_model.SerializeToString())

    @staticmethod
    def load(path: Path) -> InferenceSession:
        """Carrega um modelo ONNX que recebe textos como entrada."""

        path = Path(path)

        session = InferenceSession(
            str(path),
            providers=EXECUTION_PROVIDERS,
        )

        inputs = session.get_inputs()

        if len(inputs) != 1 or inputs[0].type != "tensor(string)":
            raise TypeError(
                "O artefato carregado não é um modelo ONNX de texto."
            )

        return session
