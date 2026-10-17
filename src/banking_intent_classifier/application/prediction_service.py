
"""Serviço de aplicação para classificação de intenções bancárias."""

from sklearn.pipeline import Pipeline


class PredictionService:
    """Executa inferências utilizando um Pipeline treinado."""

    def __init__(self, model: Pipeline) -> None:
        self._model = model

    def predict(self, text: str) -> int:
        """Retorna o identificador da intenção prevista."""
        if not text or not text.strip():
            raise ValueError("O texto não pode estar vazio.")

        prediction = self._model.predict([text])

        return int(prediction[0])
