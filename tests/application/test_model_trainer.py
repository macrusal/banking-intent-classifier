from banking_intent_classifier.application.model_trainer import (
    ModelTrainer,
)


def test_should_create_logistic_regression_classifier() -> None:
    classifier = ModelTrainer.create_classifier()

    assert classifier.max_iter == 1000

def test_should_train_classifier() -> None:
    features = [
        [1.0, 0.0],
        [0.9, 0.1],
        [0.0, 1.0],
        [0.1, 0.9],
    ]
    labels = [0, 0, 1, 1]

    classifier = ModelTrainer.create_classifier()

    trained_classifier = ModelTrainer.train(
        classifier=classifier,
        features=features,
        labels=labels,
    )

    assert trained_classifier is classifier
    assert hasattr(trained_classifier, "classes_")