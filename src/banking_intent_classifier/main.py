"""Ponto de entrada da aplicação."""

from banking_intent_classifier.application.dataset_service import DatasetService
from banking_intent_classifier.infrastructure.data.banking77_loader import (
    load_banking77,
)
from banking_intent_classifier.presentation.console_reporter import (
    ConsoleReporter,
)


def main() -> None:
    """Executa as análises do dataset BANKING77."""

    dataset = load_banking77()

    service = DatasetService()
    reporter = ConsoleReporter()

    summary = service.summarize(dataset)
    reporter.print_dataset_summary(summary)

    distribution = service.class_distribution(dataset, "train")
    distribution_summary = service.summarize_class_distribution(distribution)

    reporter.print_class_distribution(distribution)
    reporter.print_class_distribution_summary(distribution_summary)

    text_length_summary = service.summarize_text_length(dataset, "train")
    reporter.print_text_length_summary(text_length_summary)


if __name__ == "__main__":
    main()