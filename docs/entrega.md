# Acompanhamento da entrega — Tech Challenge Fase 3

## Rubrica e situação técnica (checkpoint 26/10/2026)

| Critério | Peso | Situação | Evidência / pendência |
| :--- | ---: | :--- | :--- |
| Apache Airflow | 15% | Implementado e validado | DAG `ingest → train → publish` concluída em 22/10/2026, métricas e hashes conferidos; ver [`operacao-airflow.md`](operacao-airflow.md) |
| Prometheus + Grafana | 20% | Implementado e validado localmente | Instrumentação da API (`/metrics`, Counter e Histogram com buckets calibrados) integrada à `main` pelos PRs #46 e #47. A stack `compose.monitoring.yaml` (Prometheus + Grafana provisionado, 3 painéis) foi validada com carga real em `feature/observability-stack`, com o PR pendente. Ver [`prometheus-instrumentation.md`](prometheus-instrumentation.md) e [`operacao-monitoramento.md`](operacao-monitoramento.md). Pendente: gerador de carga dedicado (tarefa 1.6) |
| ONNX + benchmark | 20% | Implementado e medido (local) | Equivalência de 100% no teste oficial; latência individual do modelo 4–7× menor; ver [`onnx-benchmark.md`](onnx-benchmark.md). A baseline de latência HTTP da API (p50 de 2,47–2,48 ms no cliente) está na `main` pelos PRs #44 e #45; ver [`http-latency-baseline.md`](http-latency-baseline.md). Pendente: servir ONNX na API (2.2) e comparar os backends no HTTP (2.3) |
| Arquitetura Cloud | 15% | Pendente | A §13 de [`architecture.md`](architecture.md) decide só a inferência em tempo real; falta provedor, mapeamento de componentes, segurança e justificativa com as latências medidas |
| CI/CD | 15% | Implementado e validado | 4 jobs em `.github/workflows/ci.yml` (`lint`, `tests` com o grupo `onnx`, `docker-build`, `validate-gitflow`), aprovados nos PRs #38 e #40; política `feature/* → dev → main` aplicada nos PRs seguintes |
| Apresentação / vídeo STAR | 15% | Pendente | Para o fim, com a stack de monitoramento no ar |

**Atenção:** os percentuais são pesos da rubrica, não notas atribuídas. Validar os critérios na rubrica oficial integral.

## Checkpoints

- **21/10/2026:** preparação da lógica reutilizável para orquestração Airflow.
- **22/10/2026:** DAG Airflow 3.1.0 `ingest → train → publish` executada com sucesso.
- **23/10/2026:** inspeção pós-run confirmou métricas e hashes; Ruff aprovado, 36 testes aprovados (1 warning); `main` e `dev` com árvores idênticas no checkpoint. Airflow integrado por PR #34.
- **24/10/2026:** ambiente local alinhado ao CI (Python 3.12); grupo de dependências `onnx` (`skl2onnx`, `onnxruntime` 1.23.x); exportação ONNX determinística; 5 execuções do benchmark no split `test` com 100% de concordância; job `tests` do CI passa a instalar o grupo `onnx`; jobs `lint`, `tests`, `docker-build` e `validate-gitflow` aprovados no PR #38 (`feature/onnx-inference-benchmark → dev`), integrado à `dev`; registro do CI no PR #39; promoção para `main` no PR #40, com os jobs do GitHub Actions aprovados.
- **26/10/2026:**
  - **Baseline de latência HTTP de `POST /predict`:** medida contra o contêiner, com p50 de 2,47–2,48 ms e p95 de 3,08–3,19 ms no cliente. Integrada à `dev` pelo PR #44 e promovida para `main` pelo PR #45.
  - **Instrumentação Prometheus da API:** middleware ASGI, `http_requests_total` e `http_request_duration_seconds`, com buckets calibrados pela média do lado servidor (1,80–1,92 ms). Integrada pelo PR #46 e promovida pelo PR #47.
  - **Stack de observabilidade:** `compose.monitoring.yaml` com `api`, `prometheus` e `grafana`, dashboard e datasource provisionados como código e leitura anônima. Validada do zero com carga real: target `up`, e os painéis exibiram 265,40 req/s, p95 de 2,91 ms e 0,00% de erro. O PR de `feature/observability-stack` está pendente.
  - **Correção desta tabela:** ONNX e CI/CD já estavam concluídos desde 24/10, e o texto anterior os mostrava como "próxima atividade" e "parcial".

## Regras de trabalho e integração

- Fluxo GitFlow `feature/* → dev → main`, por Pull Requests; sem merge direto na `main` protegida.
- Documentação e mensagens de commit em PT-BR.
- Toda afirmação quantitativa usada na avaliação acompanha um comando reproduzível.
- Alterações validadas incrementalmente, com revisão de diff antes da integração.
- Segredos, `.env`, logs, caches, datasets intermediários e artefatos grandes ficam fora do versionamento.

## Próximos passos

1. ~~ONNX: exportação, equivalência de predições e benchmark reproduzível.~~ Concluído em 24/10/2026 ([`onnx-benchmark.md`](onnx-benchmark.md)).
2. ~~Baseline de latência HTTP e instrumentação Prometheus.~~ Concluídas em 26/10/2026 (PRs #44–#47).
3. ~~Stack Prometheus + Grafana provisionada.~~ Validada em 26/10/2026; integração pelo PR de `feature/observability-stack`.
4. Servir ONNX na API, com o locale corrigido no `Dockerfile` (2.2), e comparar os backends no HTTP (2.3).
5. Gerador de carga dedicado (1.6).
6. Arquitetura Cloud documentada, com destaque no README.
7. Vídeo STAR e fechamento (`entrega.md`, roadmap, trabalhos futuros, PR final para `main`).

## Referências

- [Operação Airflow](operacao-airflow.md)
- [Exportação ONNX e benchmark](onnx-benchmark.md)
- [Baseline de latência HTTP](http-latency-baseline.md)
- [Instrumentação Prometheus](prometheus-instrumentation.md)
- [Operação do monitoramento](operacao-monitoramento.md)
- [Arquitetura](architecture.md)
- [Notas de estudo](study-notes/README.md)
