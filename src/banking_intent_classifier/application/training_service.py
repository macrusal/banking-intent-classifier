"""Serviço de treinamento e avaliação do classificador BANKING77."""

from datasets import DatasetDict

from banking_intent_classifier.application.model_evaluator import ModelEvaluator
from banking_intent_classifier.application.model_trainer import ModelTrainer


def train_and_evaluate(dataset: DatasetDict):
    """Treina no conjunto oficial e avalia no teste reservado."""

    train_split = dataset["train"]
    test_split = dataset["test"]

    pipeline = ModelTrainer.create_baseline_pipeline()

    pipeline.fit(
        train_split["text"],
        train_split["label"],
    )

    predictions = pipeline.predict(test_split["text"])

    result = ModelEvaluator.evaluate(
        configuration="TF-IDF + Logistic Regression | avaliação oficial",
        labels=test_split["label"],
        predictions=predictions,
    )

    labels = train_split.features["label"].names

    return pipeline, labels, result