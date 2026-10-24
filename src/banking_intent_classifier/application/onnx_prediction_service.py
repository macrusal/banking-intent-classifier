"""Serviço de aplicação para classificação com modelos ONNX."""

import numpy as np


class OnnxPredictionService:
    """Executa inferências utilizando uma sessão ONNX Runtime."""

    def __init__(self, session) -> None:
        self._session = session
        self._input_name = session.get_inputs()[0].name
        # A primeira saída do modelo exportado contém os rótulos previstos.
        self._label_name = session.get_outputs()[0].name

    def predict(self, text: str) -> int:
        """Retorna o identificador da intenção prevista."""
        if not text or not text.strip():
            raise ValueError("O texto não pode estar vazio.")

        return self._run([text])[0]

    def predict_batch(self, texts: list[str]) -> list[int]:
        """Retorna os identificadores das intenções previstas em lote."""
        if not texts:
            raise ValueError("A lista de textos não pode estar vazia.")

        if any(not text or not text.strip() for text in texts):
            raise ValueError("O texto não pode estar vazio.")

        return self._run(texts)

    def _run(self, texts: list[str]) -> list[int]:
        """Executa a sessão com textos no formato [N, 1]."""
        inputs = np.array(texts, dtype=object).reshape(-1, 1)

        labels = self._session.run(
            [self._label_name],
            {self._input_name: inputs},
        )[0]

        return [int(label) for label in labels]
