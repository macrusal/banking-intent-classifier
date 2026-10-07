"""Experimentos de pré-processamento para representação textual."""

from sklearn.feature_extraction.text import TfidfVectorizer


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