"""Ponto de entrada da aplicação."""

from banking_intent_classifier.application.class_distribution_analyzer import (
    ClassDistributionAnalyzer,
)
from banking_intent_classifier.application.dataset_service import DatasetService
from banking_intent_classifier.infrastructure.data.banking77_loader import (
    load_banking77,
)
from banking_intent_classifier.presentation.console_reporter import (
    ConsoleReporter,
)
from banking_intent_classifier.application.text_length_analyzer import (
    TextLengthAnalyzer,
)
from banking_intent_classifier.application.corpus_analyzer import (
    CorpusAnalyzer,
)

def main() -> None:
    """Executa as análises do dataset BANKING77."""

    dataset = load_banking77()

    service = DatasetService()
    class_distribution_analyzer = ClassDistributionAnalyzer()
    text_length_analyzer = TextLengthAnalyzer()
    corpus_analyzer = CorpusAnalyzer()
    reporter = ConsoleReporter()

    summary = service.summarize(dataset)
    reporter.print_dataset_summary(summary)

    distribution = class_distribution_analyzer.distribution(
        dataset,
        "train",
    )
    distribution_summary = class_distribution_analyzer.summarize(
        distribution,
    )

    reporter.print_class_distribution(distribution)
    reporter.print_class_distribution_summary(distribution_summary)

    text_length_summary = text_length_analyzer.summarize(
        dataset,
        "train",
    )
    reporter.print_text_length_summary(text_length_summary)

    text_length_distribution = text_length_analyzer.summarize_distribution(
        dataset,
        "train",
    )
    reporter.print_text_length_distribution(text_length_distribution)

    text_length_outliers = text_length_analyzer.summarize_outliers(
        dataset,
        "train",
    )
    reporter.print_text_length_outliers(text_length_outliers)

    corpus_summary = corpus_analyzer.summarize(
        dataset,
        "train",
    )
    reporter.print_corpus_summary(corpus_summary)

    most_frequent_tokens = corpus_analyzer.most_frequent_tokens(
        dataset,
        "train",
    )
    reporter.print_most_frequent_tokens(
        most_frequent_tokens,
    )


if __name__ == "__main__":
    main()