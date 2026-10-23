# Study Notes — Banking Intent Classifier

Este diretório reúne notas de estudo produzidas a partir da evolução real do projeto **Banking Intent Classifier**, desenvolvido para o Tech Challenge — Fase 3 da Pós-Tech FIAP em Machine Learning Engineering.

O objetivo é registrar não apenas **o que foi implementado**, mas também:

- qual problema estava sendo investigado;
- o que os dados mostraram;
- como interpretar os resultados;
- quais decisões foram tomadas;
- quais decisões foram adiadas até existirem evidências;
- quais conceitos de Machine Learning, NLP e Engenharia de Software foram aprendidos.

## Notas

1. [Dataset e validação estrutural](01-dataset-e-validacao-estrutural.md)
2. [Distribuição das classes e balanceamento](02-distribuicao-classes-e-balanceamento.md)
3. [Comprimento dos textos e percentis](03-comprimento-textos-e-percentis.md)
4. [IQR, outliers e decisões sobre remoção](04-iqr-outliers-e-decisoes.md)
5. [Corpus, vocabulário e normalização](05-corpus-vocabulario-e-normalizacao.md)
6. [Tokens frequentes e stopwords](06-tokens-frequentes-e-stopwords.md)
7. [Data leakage e separação treino/teste](07-data-leakage-e-splits.md)
8. [SRP e evolução da arquitetura](08-srp-e-evolucao-arquitetural.md)
9. [EDA orientando o baseline](09-da-eda-ao-baseline.md)
10. [Decisões adiadas e experimentação](10-decisoes-orientadas-por-evidencias.md)
11. [GitFlow como diário técnico](11-gitflow-e-aprendizado-incremental.md)
12. [Roteiro de revisão e apresentação](12-roteiro-revisao-e-video.md)
13. [TF-IDF, pré-processamento e stopwords](13-tfidf-preprocessamento-e-stopwords.md)
14. [Split estratificado e validação](14-split-estratificado-e-validacao.md)
15. [Reprodutibilidade de experimentos](15-reprodutibilidade-de-experimentos.md)
16. [Baseline formal](16-baseline-formal.md)
17. [Avaliação final e persistência](17-avaliacao-final-persistencia.md)
18. [Preparação do pipeline de treinamento para o Apache Airflow](airflow-training-pipeline.md)

## Princípio adotado

> Cada feature deve deixar dois resultados: **código funcionando** e **conhecimento registrado**.

As notas podem futuramente servir de base para artigos, posts, apresentações, vídeos, mapas mentais, sketchnotes, flashcards, cheatsheets e comics educacionais.

## Checkpoint de engenharia — 21/10/2026

A preparação do pipeline para o Airflow foi registrada na nota 18, incluindo extração do serviço de treinamento, persistência de `DatasetDict`, três operações independentes e correção dos testes após a refatoração.

**Validação local informada:** `uv run ruff check .` aprovado e `uv run pytest` com **35 testes aprovados**, sem falhas, e um aviso de depreciação Starlette/httpx.

Para reproduzir:

```bash
uv run ruff check .
uv run pytest tests/test_final_training.py -v
uv run pytest
```

**Pendente:** teste de integração ponta a ponta (`ingest_data → train_model → save_artifacts`), criação da DAG e execução no Airflow. Não confundir a preparação validada por testes unitários com a entrega da orquestração funcional.

Consulte também o [README geral do projeto](../../README.md) para setup, treinamento oficial, API, Docker e CI/CD.


## Checkpoint — 22/10/2026: DAG Airflow executada

**Atualização do registro histórico de 21/10:** o teste de integração ponta a ponta foi acrescentado e a DAG `banking77_training_pipeline` foi executada com sucesso na UI do Airflow 3.1.0 (`ingest → train → publish`, cerca de 30 segundos). A validação local relatada após o teste de integração foi de **36 testes aprovados**. As pendências descritas no checkpoint anterior foram resolvidas quanto à criação e execução da DAG, mas **a conferência dos artefatos e métricas pós-execução ainda está pendente**.

A nota [Pipeline de treinamento com Airflow](airflow-training-pipeline.md) contém arquitetura, incidentes e reprodução. O [README geral](../../README.md) reúne o procedimento operacional e o status da rubrica. Não editar retrospectivamente os resultados históricos das notas 1–17 sem nova evidência.


## Checkpoint de decisões — 23/10/2026: operação e segurança do Airflow

A execução bem-sucedida confirmou as decisões da nota 18: **separação da lógica de ML da DAG**, etapas TaskFlow `ingest → train → publish`, persistência do dataset em disco, passagem de caminhos entre tarefas, isolamento por `run_id` e publicação dos artefatos usados pela API. A DAG é manual (`schedule=None`), sem catchup, com `max_active_runs=1`.

A infraestrutura utiliza **Airflow 3.1.0, LocalExecutor e PostgreSQL 16**, em `compose.airflow.yaml`, separada da imagem da API de inferência. A falha inicial de comunicação foi tratada configurando `AIRFLOW__CORE__EXECUTION_API_SERVER_URL=http://airflow-api-server:8080/execution/`. Em seguida, a falha `Invalid auth token: Signature verification failed` foi resolvida com uma chave `AIRFLOW__API_AUTH__JWT_SECRET` compartilhada pelos serviços, obtida de `AIRFLOW_JWT_SECRET` em `.env` local ignorado pelo Git. **Não versionar segredos, logs, datasets ou artefatos gerados.**

### Reproduzir e conferir

```bash
# Criar .env somente se não existir; confirmar .env no .gitignore
test -e .env || python3 -c "import secrets; print('AIRFLOW_JWT_SECRET=' + secrets.token_hex(32))" > .env
git check-ignore -v .env
docker compose -f compose.airflow.yaml config --quiet
docker compose -f compose.airflow.yaml up -d --build
docker compose -f compose.airflow.yaml ps
docker compose -f compose.airflow.yaml exec airflow-scheduler airflow dags list-import-errors
# Acionar banking77_training_pipeline na UI http://localhost:8080
ls -lh artifacts/baseline_pipeline.joblib artifacts/label_mapping.json
find airflow/data/runs -name metrics.json -print -exec cat {} \;
uv run ruff check .
uv run pytest tests/application/test_training_pipeline_integration.py -v
uv run pytest
```

**Evidência observada:** execução manual em 22/10/2026, três tarefas em `success`, uma tentativa por tarefa e duração total de aproximadamente 30 segundos. **Pendente:** conferir e registrar as métricas e os horários de atualização dos artefatos dessa execução; a existência prévia de `artifacts/` não é evidência suficiente. A última suíte informada continha **36 testes aprovados**, mas deve ser repetida antes do commit.

Para explicações técnicas, incidentes, comandos de diagnóstico e estado da rubrica, consultar a [seção operacional do README geral](../../README.md#-execução-airflow-e-decisões-arquiteturais--checkpoint-23102026) e a [nota 18](airflow-training-pipeline.md). O registro de 21/10 permanece histórico e não representa o status atual.
