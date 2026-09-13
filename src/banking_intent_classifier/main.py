"""Ponto de entrada da aplicação."""

from banking_intent_classifier.data.loader import load_banking77


def main() -> None:
    """Carrega o BANKING77 e exibe informações básicas do dataset."""

    dataset = load_banking77()

    print(dataset)
    print(dataset["train"][0])

    print("BANKING77")
    print("-" * 40)
    print(f"Registros de treino: {len(dataset['train'])}")
    print(f"Registros de teste: {len(dataset['test'])}")
    print(f"Total de registros: {len(dataset['train']) + len(dataset['test'])}")

    train_labels = set(dataset["train"]["label"])
    test_labels = set(dataset["test"]["label"])

    print(f"Classes no treino: {len(train_labels)}")
    print(f"Classes no teste: {len(test_labels)}")

if __name__ == "__main__":
    main()