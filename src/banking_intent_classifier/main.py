"""Ponto de entrada da aplicação."""

from banking_intent_classifier.data.loader import load_banking77


def main() -> None:
    """Carrega o BANKING77 e exibe informações básicas do dataset."""

    dataset = load_banking77()

    print(dataset)
    print(dataset["train"][0])


if __name__ == "__main__":
    main()