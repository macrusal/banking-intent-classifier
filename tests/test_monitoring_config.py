"""Testes de consistência da stack de observabilidade versionada."""

import json
import re
from pathlib import Path

import yaml

from banking_intent_classifier.presentation.metrics import (
    REQUEST_DURATION_SECONDS,
    REQUESTS_TOTAL,
)

ROOT = Path(__file__).resolve().parents[1]
MONITORING = ROOT / "monitoring"
COMPOSE_PATH = ROOT / "compose.monitoring.yaml"
PROMETHEUS_PATH = MONITORING / "prometheus.yml"
DATASOURCE_PATH = MONITORING / "grafana/provisioning/datasources/prometheus.yml"
DASHBOARD_PATH = MONITORING / "grafana/dashboards/api.json"


def load_yaml(path: Path) -> dict:
    """Lê um arquivo YAML do repositório."""

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_dashboard() -> dict:
    """Lê o dashboard provisionado."""

    return json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))


def exported_series() -> set[str]:
    """Nomes de série que a API realmente expõe no /metrics."""

    counter = REQUESTS_TOTAL.describe()[0].name
    histogram = REQUEST_DURATION_SECONDS.describe()[0].name

    return {
        f"{counter}_total",
        f"{histogram}_bucket",
        f"{histogram}_sum",
        f"{histogram}_count",
    }


def test_compose_has_three_services_and_mounts_artifacts() -> None:
    """Verifica os serviços e o volume de artefatos da API."""

    compose = load_yaml(COMPOSE_PATH)

    assert set(compose["services"]) == {"api", "prometheus", "grafana"}
    assert "./artifacts:/app/artifacts:ro" in compose["services"]["api"]["volumes"]


def test_prometheus_scrapes_api_by_service_name_every_5s() -> None:
    """Verifica o alvo pelo nome do serviço e o intervalo de coleta."""

    config = load_yaml(PROMETHEUS_PATH)
    targets = [
        target
        for job in config["scrape_configs"]
        for static in job["static_configs"]
        for target in static["targets"]
    ]

    assert config["global"]["scrape_interval"] == "5s"
    assert targets == ["api:8000"]


def test_dashboard_references_provisioned_datasource_uid() -> None:
    """Verifica que painéis e consultas usam o uid fixo do datasource."""

    datasource_uid = load_yaml(DATASOURCE_PATH)["datasources"][0]["uid"]
    dashboard = load_dashboard()

    uids = {panel["datasource"]["uid"] for panel in dashboard["panels"]}
    uids |= {
        target["datasource"]["uid"]
        for panel in dashboard["panels"]
        for target in panel["targets"]
    }

    assert uids == {datasource_uid}


def test_dashboard_queries_use_only_exported_metrics() -> None:
    """Verifica que as consultas não usam métricas inexistentes na API."""

    expressions = [
        target["expr"]
        for panel in load_dashboard()["panels"]
        for target in panel["targets"]
    ]
    referenced = {
        name
        for expression in expressions
        for name in re.findall(r"\bhttp_[a-z_]+", expression)
    }

    assert referenced
    assert referenced <= exported_series()


def test_dashboard_panels_and_units() -> None:
    """Verifica os três painéis e a unidade em segundos da latência."""

    panels = {panel["title"]: panel for panel in load_dashboard()["panels"]}
    units = {
        title: panel["fieldConfig"]["defaults"]["unit"]
        for title, panel in panels.items()
    }

    assert len(panels) == 3
    assert units == {
        "Taxa de requisições": "reqps",
        "Latência p95 — POST /predict": "s",
        "Taxa de erro (5xx)": "percentunit",
    }
