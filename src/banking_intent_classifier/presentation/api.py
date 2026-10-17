
"""API HTTP para classificação de intenções bancárias."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from banking_intent_classifier.application.prediction_service import (
    PredictionService,
)
from banking_intent_classifier.infrastructure.model_repository import (
    ModelRepository,
)
from banking_intent_classifier.infrastructure.label_repository import LabelRepository


ARTIFACT_PATH = Path("artifacts/baseline_pipeline.joblib")
LABEL_MAPPING_PATH = Path("artifacts/label_mapping.json")

class PredictionRequest(BaseModel):
    """Mensagem recebida para classificação."""

    text: str = Field(min_length=1)


class PredictionResponse(BaseModel):
    """Resultado da classificação."""

    intent_id: int
    intent: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carrega o modelo uma única vez durante a inicialização."""

    model = ModelRepository.load(ARTIFACT_PATH)
    app.state.prediction_service = PredictionService(model)
    app.state.labels = LabelRepository.load(LABEL_MAPPING_PATH)

    yield
    del app.state.labels
    del app.state.prediction_service


app = FastAPI(
    title="Banking Intent Classifier",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    """Retorna o estado operacional da API."""

    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    """Classifica uma mensagem bancária."""

    try:
        intent_id = app.state.prediction_service.predict(request.text)
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    return PredictionResponse(
        intent_id=intent_id,
        intent=app.state.labels[intent_id],
    )
