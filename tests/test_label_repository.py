
"""Testes da persistência dos nomes das classes."""

from pathlib import Path

from banking_intent_classifier.infrastructure.label_repository import (
    LabelRepository,
)


def test_should_save_and_load_labels(tmp_path: Path) -> None:
    """Verifica a persistência do mapeamento de classes."""

    labels = [
        "activate_my_card",
        "age_limit",
        "card_arrival",
    ]

    artifact_path = tmp_path / "models" / "label_mapping.json"

    LabelRepository.save(labels, artifact_path)

    assert artifact_path.is_file()

    restored_labels = LabelRepository.load(artifact_path)

    assert restored_labels == labels
    assert restored_labels[2] == "card_arrival"
