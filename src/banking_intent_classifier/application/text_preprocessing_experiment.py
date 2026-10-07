"""Experimentos de pré-processamento para representação textual."""

from sklearn.feature_extraction.text import TfidfVectorizer
from banking_intent_classifier.application.dataset_splitter import (
    DatasetSplitter,
)
from banking_intent_classifier.application.model_evaluator import (
    ModelEvaluator,
)
from banking_intent_classifier.application.model_trainer import (
    ModelTrainer,
)
from banking_intent_classifier.domain.experiment_result import (
    ExperimentResult,
)

class TextPreprocessingExperiment:
    """Compara configurações de representação textual."""

    @staticmethod
    def create_vectorizer(
        remove_stopwords: bool,
    ) -> TfidfVectorizer:
        """Cria um TF-IDF com a configuração de stopwords desejada."""

        return TfidfVectorizer(
            stop_words="english" if remove_stopwords else None,
        )

    @staticmethod
    def prepare_data(dataset):
        """Prepara os dados de treino e validação para o experimento."""

        texts = dataset["train"]["text"]
        labels = dataset["train"]["label"]

        return DatasetSplitter.split(
            texts=texts,
            labels=labels,
        )

    @staticmethod
    def run(
            train_texts: list[str],
            validation_texts: list[str],
            train_labels: list[int],
            validation_labels: list[int],
            remove_stopwords: bool,
    ) -> ExperimentResult:
        """Executa uma configuração do experimento de pré-processamento."""

        vectorizer = TextPreprocessingExperiment.create_vectorizer(
            remove_stopwords=remove_stopwords,
        )

        train_features = vectorizer.fit_transform(train_texts)
        validation_features = vectorizer.transform(validation_texts)

        classifier = ModelTrainer.create_classifier()

        classifier = ModelTrainer.train(
            classifier=classifier,
            features=train_features,
            labels=train_labels,
        )

        predictions = classifier.predict(validation_features)

        configuration = (
            "stop_words=english"
            if remove_stopwords
            else "stop_words=None"
        )

        return ModelEvaluator.evaluate(
            configuration=configuration,
            labels=validation_labels,
            predictions=predictions,
        )

    @staticmethod
    def compare(
            train_texts: list[str],
            validation_texts: list[str],
            train_labels: list[int],
            validation_labels: list[int],
    ) -> list[ExperimentResult]:
        """Compara as configurações de pré-processamento textual."""

        return [
            TextPreprocessingExperiment.run(
                train_texts=train_texts,
                validation_texts=validation_texts,
                train_labels=train_labels,
                validation_labels=validation_labels,
                remove_stopwords=False,
            ),
            TextPreprocessingExperiment.run(
                train_texts=train_texts,
                validation_texts=validation_texts,
                train_labels=train_labels,
                validation_labels=validation_labels,
                remove_stopwords=True,
            ),
        ]