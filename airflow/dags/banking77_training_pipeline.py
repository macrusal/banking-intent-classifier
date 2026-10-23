"""DAG de treinamento do classificador BANKING77."""

from pathlib import Path

from airflow.sdk import dag, task

from banking_intent_classifier.application.training_pipeline import (
    ingest_data,
    save_artifacts,
    train_model,
)

DATA_DIR = Path("/opt/airflow/data")
ARTIFACT_DIR = Path("/opt/project/artifacts")


@dag(
    dag_id="banking77_training_pipeline",
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["banking77", "machine-learning", "training"],
)
def banking77_training_pipeline():
    """Orquestra ingestão, treinamento e publicação do modelo."""

    @task
    def ingest() -> str:
        """Carrega e persiste o dataset BANKING77."""
        from airflow.sdk import get_current_context

        context = get_current_context()
        run_id = context["run_id"]
        safe_run_id = "".join(
            char if char.isalnum() or char in "-_" else "_"
            for char in run_id
        )

        dataset_path = DATA_DIR / "runs" / safe_run_id / "dataset"
        return str(ingest_data(dataset_path))

    @task
    def train(dataset_path: str) -> str:
        """Treina e avalia o classificador."""
        path = Path(dataset_path)
        training_path = path.parent / "training"

        return str(train_model(path, training_path))

    @task
    def publish(training_path: str) -> None:
        """Publica o modelo e o mapeamento de classes."""
        save_artifacts(
            training_path=Path(training_path),
            artifact_path=ARTIFACT_DIR / "baseline_pipeline.joblib",
            label_mapping_path=ARTIFACT_DIR / "label_mapping.json",
        )

    publish(train(ingest()))


banking77_training_pipeline()