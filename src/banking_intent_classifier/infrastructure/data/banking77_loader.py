"""Carregamento do dataset BANKING77."""

from datasets import DatasetDict, load_dataset

DATASET_NAME = "PolyAI/banking77"
DATASET_REVISION = "refs/pr/6"

EXPECTED_COLUMNS = {
    "text",
    "label",
}

EXPECTED_SPLITS = {
    "train",
    "test",
}

def load_banking77() -> DatasetDict:
    """
    Carrega o dataset BANKING77 a partir do Hugging Face Hub.

    Returns:
        DatasetDict: Dataset contendo os splits de treino e teste.

    Raises:
        ValueError: Caso a estrutura esperada do dataset não seja encontrada.
    """

    dataset = load_dataset(
        DATASET_NAME,
        revision=DATASET_REVISION,
    )
    validate_dataset(dataset)
    return dataset


def validate_dataset(dataset: DatasetDict) -> None:
    """Valida os splits e as colunas obrigatórias do BANKING77."""

    missing_splits = EXPECTED_SPLITS - set(dataset.keys())

    if missing_splits:
        raise ValueError(
            f"Splits obrigatórios ausentes: {sorted(missing_splits)}"
        )

    for split_name in sorted(EXPECTED_SPLITS):
        columns = set(dataset[split_name].column_names)
        missing_columns = EXPECTED_COLUMNS - columns

        if missing_columns:
            raise ValueError(
                f"Colunas obrigatórias ausentes no split "
                f"'{split_name}': {sorted(missing_columns)}"
            )
