"""Apresentação dos resultados das análises no console."""

from banking_intent_classifier.domain.dataset_summary import (
    ClassDistributionSummary,
    DatasetSummary,
    SplitSummary,
    TextLengthSummary,
)


class ConsoleReporter:
    """Responsável pela apresentação dos resultados no console."""

    def print_dataset_summary(self, summary: DatasetSummary) -> None:
        """Exibe o resumo geral do dataset."""

        print("BANKING77")
        print("=" * 40)
        print(f"Total de registros: {summary.total_records}")
        print(
            "Mesmas classes em treino e teste: "
            f"{summary.same_classes_in_splits}"
        )

        self._print_split_summary("TREINO", summary.train)
        self._print_split_summary("TESTE", summary.test)

        print(
            "Textos presentes em treino e teste: "
            f"{summary.overlapping_texts}"
        )

    def print_class_distribution(
        self,
        distribution: dict[str, int],
    ) -> None:
        """Exibe a distribuição das classes."""

        print("\nDISTRIBUIÇÃO DAS CLASSES — TREINO")
        print("-" * 40)

        for intent, count in distribution.items():
            print(f"{intent}: {count}")

    def print_class_distribution_summary(
        self,
        summary: ClassDistributionSummary,
    ) -> None:
        """Exibe as estatísticas da distribuição das classes."""

        print("\nRESUMO DA DISTRIBUIÇÃO")
        print("-" * 40)
        print(f"Mínimo: {summary.minimum}")
        print(f"Máximo: {summary.maximum}")
        print(f"Média: {summary.mean:.2f}")
        print(f"Mediana: {summary.median:.2f}")

    def print_text_length_summary(
        self,
        summary: TextLengthSummary,
    ) -> None:
        """Exibe as estatísticas de comprimento dos textos."""

        print("\nCOMPRIMENTO DOS TEXTOS — TREINO")
        print("-" * 40)

        print("Caracteres")
        print(f"Mínimo: {summary.minimum_characters}")
        print(f"Máximo: {summary.maximum_characters}")
        print(f"Média: {summary.mean_characters:.2f}")
        print(f"Mediana: {summary.median_characters:.2f}")

        print("\nPalavras")
        print(f"Mínimo: {summary.minimum_words}")
        print(f"Máximo: {summary.maximum_words}")
        print(f"Média: {summary.mean_words:.2f}")
        print(f"Mediana: {summary.median_words:.2f}")

    def _print_split_summary(
        self,
        name: str,
        summary: SplitSummary,
    ) -> None:
        """Exibe o resumo de um split."""

        print(f"\n{name}")
        print("-" * 40)
        print(f"Registros: {summary.records}")
        print(f"Classes: {summary.classes}")
        print(f"Textos ausentes: {summary.missing_texts}")
        print(f"Labels ausentes: {summary.missing_labels}")
        print(f"Textos vazios: {summary.empty_texts}")
        print(f"Registros duplicados: {summary.duplicated_records}")