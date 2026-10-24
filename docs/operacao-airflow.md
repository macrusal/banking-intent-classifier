# Operação do pipeline Apache Airflow

Este documento concentra a arquitetura operacional, a reprodução, o diagnóstico e os incidentes do Airflow 3.1.0 no projeto Banking Intent Classifier.

## Estado confirmado em 23/10/2026

A DAG `banking77_training_pipeline` foi executada com sucesso em 22/10/2026, com as tarefas `ingest → train → publish` concluídas. O registro de inspeção posterior em 23/10 confirmou os arquivos e hashes abaixo; não representa uma nova execução.

**Métricas registradas no run:** `accuracy=0.8769480519480519`, `macro_f1=0.8768846181655345`, `weighted_f1=0.8768846181655345`.

**Run:** `manual__2026-10-22T12_20_39_753264_00_00` (identificador sanitizado no diretório).

**SHA-256:** pipeline `ba88b088efa61e266eb9c4e856cd945251fc70761ad48f05d74db77e5e1217f3`; mapeamento `2a0729c0d558057bbd2a1e6b690e09c37be565d6278f18603df8b3d602fa4bc7`.

Os hashes verificam igualdade entre intermediários e publicados naquele momento; não garantem publicação atômica.

## Decisões de arquitetura e justificativas

| Decisão | Justificativa e consequência |
| :--- | :--- |
| Separar `application/training_service.py` e `application/training_pipeline.py` da DAG | A lógica de ML permanece testável e reutilizável sem dependência do Airflow; a DAG apenas coordena as operações. |
| DAG TaskFlow com `ingest → train → publish` | Etapas observáveis, reexecutáveis e com responsabilidades independentes. |
| `schedule=None`, `catchup=False`, `max_active_runs=1` | Execução manual controlada; não realizar backfill nem permitir duas execuções simultâneas que disputem os artefatos finais. |
| Persistir `DatasetDict` com `DatasetRepository` | Evitar transportar milhares de registros por XCom; tarefas compartilham **caminhos de arquivos**, não o dataset inteiro. |
| Diretório intermediário por `run_id` sanitizado em `airflow/data/runs/` | Isolar datasets e métricas intermediárias de cada execução. |
| `train_model` salva `pipeline.joblib`, `label_mapping.json`, `metrics.json` no diretório intermediário | Tornar os resultados da avaliação inspecionáveis antes da publicação. |
| `save_artifacts` valida e copia modelo e classes para `artifacts/` | Preservar os caminhos consumidos pela API FastAPI. A publicação por cópia **não é atômica**; melhorar se houver concorrência ou operação em produção. |
| Airflow 3.1.0 + `LocalExecutor` + PostgreSQL 16 em Compose separado | Orquestração local reprodutível sem misturar o contêiner de inferência com o de treinamento. |
| `AIRFLOW__CORE__EXECUTION_API_SERVER_URL` apontando para `http://airflow-api-server:8080/execution/` | A comunicação entre contêineres usa DNS interno Docker, não `localhost`. Resolveu a falha inicial de conexão, revelando o erro seguinte de autenticação. |
| `AIRFLOW__API_AUTH__JWT_SECRET` compartilhado entre serviços | Corrigiu `Invalid auth token: Signature verification failed`. O segredo é fornecido por `${AIRFLOW_JWT_SECRET}` em `.env` **local, ignorado pelo Git**. |
| Montagens `airflow/dags`, `airflow/logs`, `airflow/data` e `artifacts` | Disponibilizar código, dados intermediários, logs e modelos no host e nos serviços necessários. |

## Serviços, portas e persistência

O ambiente usa Airflow 3.1.0, PostgreSQL 16 e `LocalExecutor`, definidos em `compose.airflow.yaml`, com imagem em `airflow/Dockerfile`. Serviços documentados: `postgres`, `airflow-init`, `airflow-api-server`, `airflow-scheduler`, `airflow-dag-processor`. Interface local: `http://localhost:8080`. Montagens incluem `airflow/dags`, `airflow/logs`, `airflow/data` e `artifacts`.

Os dados intermediários são isolados por `run_id` em `airflow/data/runs/`; a publicação copia os arquivos finais para `artifacts/` em caminhos fixos. Essa cópia não é atômica.

## Reproduzir e verificar

### Reproduzir a execução em outra máquina

Pré-requisitos: Docker Desktop/Engine e Compose, portas locais disponíveis, acesso ao Hugging Face Hub. Na raiz do repositório, garantir que `.env` esteja no `.gitignore`. Criar a variável somente quando o arquivo ainda não existir:

```bash
test -e .env || python3 -c "import secrets; print('AIRFLOW_JWT_SECRET=' + secrets.token_hex(32))" > .env
git check-ignore -v .env
docker compose -f compose.airflow.yaml config --quiet
docker compose -f compose.airflow.yaml up -d --build
docker compose -f compose.airflow.yaml ps
docker compose -f compose.airflow.yaml exec airflow-scheduler airflow dags list-import-errors
```

Se `.env` já existir, **verifique localmente** se contém `AIRFLOW_JWT_SECRET`; não sobrescreva outros segredos. Acesse <http://localhost:8080>, autentique-se com a credencial administrativa gerada localmente, despause a DAG se necessário e acione `banking77_training_pipeline`. Não versionar credenciais nem copiar seus valores para logs públicos.

Verifique o resultado e as evidências:

```bash
ls -lh artifacts/baseline_pipeline.joblib artifacts/label_mapping.json
find airflow/data/runs -name metrics.json -print -exec cat {} \;
docker compose -f compose.airflow.yaml exec postgres \
  psql -U airflow -d airflow \
  -c "SELECT dag_id, run_id, state FROM dag_run WHERE dag_id = 'banking77_training_pipeline' ORDER BY id DESC LIMIT 10;"
uv run ruff check .
uv run pytest tests/application/test_training_pipeline_integration.py -v
uv run pytest
```

A consulta SQL é somente de leitura e evita depender de links de `run_id` contendo `+`, que podem ser interpretados incorretamente como espaço na URL. Os resultados da avaliação oficial documentada são `accuracy = macro_f1 = weighted_f1 = 0.8769`; compare os valores de `metrics.json` com essa referência **após efetuar a verificação**.

Para comparar o run histórico, use:

```bash
RUN_DIR="airflow/data/runs/manual__2026-10-22T12_20_39_753264_00_00/training"
cat "$RUN_DIR/metrics.json"
shasum -a 256 "$RUN_DIR/pipeline.joblib" artifacts/baseline_pipeline.joblib
shasum -a 256 "$RUN_DIR/label_mapping.json" artifacts/label_mapping.json
```

Para novos runs, substitua `RUN_DIR` pelo diretório da execução correspondente. Não compare artefatos publicados por outra execução.

## Incidentes, diagnóstico e segurança

Comandos de diagnóstico:

```bash
docker compose -f compose.airflow.yaml logs --tail=150 airflow-scheduler airflow-api-server
docker compose -f compose.airflow.yaml exec airflow-scheduler \
  airflow config get-value core execution_api_server_url
```

Histórico de incidentes: primeiro `httpx.ConnectError: [Errno 111] Connection refused`; depois `Invalid auth token: Signature verification failed`. Em ambos os casos, a tarefa `ingest` falhou antes de executar o código do dataset, e os logs de tentativa estavam vazios. A mensagem `LocalExecutor ... state failed ... state queued` era consequência da falha de inicialização, não diagnóstico de erro do BANKING77. A correção foi validada pela execução posterior bem-sucedida. **Não usar `docker compose down -v`** para investigar: isso apagaria o volume de metadados do PostgreSQL.

A falha de comunicação com a Execution API foi corrigida com `AIRFLOW__CORE__EXECUTION_API_SERVER_URL=http://airflow-api-server:8080/execution/`. A falha de assinatura JWT foi corrigida compartilhando `AIRFLOW__API_AUTH__JWT_SECRET: ${AIRFLOW_JWT_SECRET}` entre serviços. O segredo pertence ao `.env` local, ignorado pelo Git.

Para aprofundamento técnico: [nota de estudo do pipeline](study-notes/airflow-training-pipeline.md).
