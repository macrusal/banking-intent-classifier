# Pipeline de treinamento com Apache Airflow — preparação e execução

**Projeto:** Banking Intent Classifier — Tech Challenge FIAP, Fase 3
**Data:** 21/10/2026
**Estado em 21/10:** preparação concluída. **Atualização de 22/10:** DAG executada com sucesso (ver seção 7).

## 1. Contexto e objetivo

O projeto já possui treinamento final reproduzível, avaliação sobre o conjunto oficial de teste do BANKING77 e persistência do modelo para uso pela API. A próxima etapa é orquestrar esse processo com o Apache Airflow, separando ingestão, treinamento e publicação dos artefatos.

A preparação foi feita antes da criação da DAG para evitar que o código de treinamento dependa do orquestrador. O Airflow deverá **chamar operações existentes**, e não concentrar a lógica de ML.

## 2. Decisões arquiteturais

### 2.1. Serviço de treinamento independente da interface de linha de comando

A operação `train_and_evaluate(dataset)` foi extraída de `final_training.py` para `application/training_service.py`. Ela encapsula criação do pipeline TF-IDF + Logistic Regression, ajuste, predição, avaliação e obtenção dos nomes das classes.

O módulo `final_training.py` continua sendo uma entrada executável para treinamento local. Ele carrega o dataset, invoca o serviço e persiste os artefatos. A separação permite reutilizar a lógica a partir do pipeline orquestrado sem importar funções de um ponto de entrada CLI.

**Motivo:** coesão, reuso e testes por responsabilidade, evitando acoplamento entre a aplicação e o orquestrador.

### 2.2. Operações independentes para o futuro DAG

O módulo `application/training_pipeline.py` expõe três operações:

| Operação | Responsabilidade | Saída |
| --- | --- | --- |
| `ingest_data(dataset_path)` | Carregar e validar BANKING77 e salvar dataset em disco | Caminho do dataset |
| `train_model(dataset_path, output_path)` | Ler dataset persistido, treinar, avaliar e salvar arquivos intermediários | Diretório de treinamento |
| `save_artifacts(training_path, artifact_path, label_mapping_path)` | Verificar arquivos intermediários e publicar modelo e classes | Arquivos finais |

O fluxo pretendido para o Airflow é `ingest_data → train_model → save_artifacts`. Até esta data, a sequência ainda não foi validada em um teste de integração ponta a ponta nem executada em uma DAG.

### 2.3. Repositório de datasets

`infrastructure/data/dataset_repository.py` centraliza a persistência do `DatasetDict` com `save_to_disk` e a recuperação com `load_from_disk`, incluindo validação dos splits e colunas esperados.

**Motivo:** transferir dados entre etapas por artefatos em disco, em vez de transportar o dataset inteiro por mensagens entre tarefas.

### 2.4. Persistência explícita dos artefatos

O treinamento intermediário produz:

- `pipeline.joblib`: pipeline treinado;
- `label_mapping.json`: nomes das classes na ordem dos IDs;
- `metrics.json`: accuracy, macro F1 e weighted F1.

A etapa de publicação valida a presença desses arquivos e verifica a leitura do modelo e do mapeamento antes de copiá-los para os caminhos utilizados pela API.

**Limitação atual:** a publicação utiliza cópias de arquivos e ainda não é uma operação atômica. Isso deve ser avaliado antes de uma implantação concorrente ou de produção.

## 3. Decisões de testes e problema encontrado

Após extrair `train_and_evaluate()` para o serviço, o teste de `final_training.py` deixou de poder verificar diretamente `ModelTrainer.create_baseline_pipeline()`, `pipeline.fit()`, `pipeline.predict()` e `ModelEvaluator.evaluate()` nesse módulo.

A correção foi alinhar o teste à responsabilidade atual da CLI:

1. simular o carregamento de dados;
2. simular `train_and_evaluate()` e verificar que recebeu o dataset;
3. verificar a persistência do modelo e do mapeamento;
4. conferir a saída com as métricas.

O teste passou a usar `Dataset` e `DatasetDict` reais da biblioteca Hugging Face como fixtures leves, em vez de dicionários comuns. A razão é importante: `len(dataset['test'])` conta **registros** em um `Dataset`, mas conta **chaves** em um `dict`. O dicionário artificial com `text` e `label` devolvia `2` mesmo contendo apenas um registro, gerando uma falha enganosa.

**Lição:** doubles de teste devem preservar os comportamentos relevantes dos tipos reais, especialmente protocolos como `len()`. Os testes de treinamento interno (`fit`, `predict`, avaliação) pertencem à camada do serviço e devem ser adicionados ou verificados separadamente.

## 4. Evidências de validação

Execução local reportada em 21/10/2026:

```bash
uv run ruff check .
uv run pytest tests/test_final_training.py -v
uv run pytest
```

Resultados observados:

```text
All checks passed!
1 passed
35 passed, 1 warning
```

O aviso é `StarletteDeprecationWarning` relacionado a `httpx`/`starlette.testclient`; não representa falha de teste nesta execução.

A avaliação oficial do baseline anteriormente reproduzida no projeto apresentou accuracy, macro F1 e weighted F1 de aproximadamente `0.8769` no conjunto oficial de teste. Para reproduzir:

```bash
uv run python -m banking_intent_classifier.final_training
```

Esse comando também gera os artefatos locais necessários para a API. Os arquivos gerados não devem ser confundidos com arquivos versionados no Git.

## 5. Pendências e próximos passos

1. Criar um teste de integração `ingest_data → train_model → save_artifacts`, com diretórios temporários e dados sintéticos ou carregamento controlado.
2. Adicionar teste específico de `application/training_service.py` para assegurar o comportamento de `fit`, `predict` e avaliação na nova camada.
3. Definir diretórios compartilhados e identificadores por execução para as tarefas do Airflow.
4. Criar Docker Compose e DAG funcional, validar ingestão, treinamento e publicação em execução real.
5. Documentar comandos de inicialização, execução e inspeção da DAG e registrar evidências reproduzíveis no README principal.
6. Considerar publicação atômica/versionada de artefatos antes de uso concorrente.

## 6. Princípios preservados

- GitFlow: `feature/* → dev → main`, por Pull Requests.
- Testes e lint antes de integrar alterações.
- Separação entre aplicação, infraestrutura e interfaces de execução.
- Reprodutibilidade: cada resultado relevante da entrega deve ter comando ou procedimento versionado.
- Documentação em português, acompanhando a evolução real da implementação.


## 7. Atualização de implementação e execução — 22/10/2026

As seções 1–6 documentam o **checkpoint histórico de 21/10**. As pendências relativas à criação da DAG, infraestrutura e teste de integração foram superadas no checkpoint seguinte.

### 7.1. DAG funcional

- Arquivo: `airflow/dags/banking77_training_pipeline.py`.
- Decorators do Airflow 3: `from airflow.sdk import dag, task`.
- `dag_id=banking77_training_pipeline`, `schedule=None`, `catchup=False`, `max_active_runs=1`.
- Etapas: `ingest` carrega BANKING77 e salva dataset; `train` carrega o dataset persistido, treina e grava `pipeline.joblib`, `label_mapping.json` e `metrics.json`; `publish` valida e copia modelo/mapeamento para `artifacts/`.
- Caminhos por execução: `/opt/airflow/data/runs/<run_id_sanitizado>/dataset` e `.../training`, evitando colisão dos intermediários; publicação final usa caminhos fixos, portanto ainda não é atômica/versionada.
- Infraestrutura: `compose.airflow.yaml` com PostgreSQL 16 e Airflow 3.1.0 (`LocalExecutor`); imagem customizada em `airflow/Dockerfile`, com projeto Python disponível por `PYTHONPATH=/opt/project/src`.

### 7.2. Incidentes diagnosticados e decisões

1. Primeira execução falhou em `ingest` antes de entrar no código; log da tarefa vazio, Scheduler reportou `httpx.ConnectError: [Errno 111] Connection refused` ao iniciar task pela Execution API.
2. Configurado no ambiente comum do Compose `AIRFLOW__CORE__EXECUTION_API_SERVER_URL=http://airflow-api-server:8080/execution/`; teste de rede do Scheduler até o API Server obteve resposta HTTP 404 para GET na raiz `/execution/`, o que comprova conectividade, **não** sucesso da operação da API.
3. Segunda execução falhou com `Invalid auth token: Signature verification failed`. Decisão: compartilhar `AIRFLOW__API_AUTH__JWT_SECRET` entre API Server e Scheduler via `${AIRFLOW_JWT_SECRET}` de `.env` local (ignorado pelo Git); serviços recriados sem remover volumes.
4. Links de runs na UI apresentaram erro 404 quando o `+` do `run_id` foi interpretado como espaço; consulta somente leitura ao PostgreSQL confirmou a existência das execuções com falha.
5. Terceira execução na UI em 22/10/2026: **sucesso**, com `ingest`, `train`, `publish` verdes, uma tentativa cada, duração total aproximada de 30 segundos. Este resultado valida a orquestração. **A inspeção posterior das métricas e dos arquivos publicados foi concluída** (ver seção 8).

### 7.3. Reprodução

```bash
# Criar o .env apenas se inexistente:
test -e .env || python3 -c "import secrets; print('AIRFLOW_JWT_SECRET=' + secrets.token_hex(32))" > .env
# O Compose deve conter AIRFLOW__API_AUTH__JWT_SECRET: ${AIRFLOW_JWT_SECRET}
# no bloco environment compartilhado, e .env deve constar no .gitignore.
docker compose -f compose.airflow.yaml config --quiet
docker compose -f compose.airflow.yaml up -d --build
docker compose -f compose.airflow.yaml ps
docker compose -f compose.airflow.yaml exec airflow-scheduler airflow dags list-import-errors
# Acessar http://localhost:8080; despausar e acionar a DAG manualmente.
ls -lh artifacts/baseline_pipeline.joblib artifacts/label_mapping.json
find airflow/data/runs -name metrics.json -print -exec cat {} \;
uv run ruff check .
uv run pytest
```

Não publicar JWT, senhas, `.env`, logs nem modelos grandes no Git. O último checkpoint de testes relatado foi **36 passed**; repetir antes do commit. As métricas da execução Airflow e a conferência dos artefatos foram registradas na seção 8. Pendências: avaliar publicação atômica/versionada, fixar versões das dependências da imagem e avançar ONNX, monitoramento e cloud.


## 8. Evidências pós-execução — verificadas em 23/10/2026

Esta seção registra a inspeção dos arquivos produzidos pela execução bem-sucedida de **22/10/2026**, complementando o checkpoint operacional da seção 7. Os resultados abaixo foram obtidos a partir dos comandos executados localmente e de suas saídas registradas; não representam uma nova execução da DAG.

### 8.1. Identificação da execução e métricas

Diretório da execução (identificador sanitizado para uso no sistema de arquivos):

```text
airflow/data/runs/manual__2026-10-22T12_20_39_753264_00_00/
```

Arquivo `training/metrics.json`:

```json
{
  "accuracy": 0.8769480519480519,
  "macro_f1": 0.8768846181655345,
  "weighted_f1": 0.8768846181655345
}
```

As três métricas arredondam para aproximadamente **0,8769**, coerentes com o baseline oficial já documentado. A evidência mostra que a etapa de treinamento gerou o arquivo de métricas; por si só, não comprova equivalência byte a byte entre execuções distintas do treinamento.

### 8.2. Integridade dos artefatos publicados

Foram comparados os hashes SHA-256 dos arquivos intermediários da execução com os artefatos finais consumidos pela API:

| Arquivo intermediário | Artefato publicado | SHA-256 (idêntico em ambos) |
| --- | --- | --- |
| `training/pipeline.joblib` | `artifacts/baseline_pipeline.joblib` | `ba88b088efa61e266eb9c4e856cd945251fc70761ad48f05d74db77e5e1217f3` |
| `training/label_mapping.json` | `artifacts/label_mapping.json` | `2a0729c0d558057bbd2a1e6b690e09c37be565d6278f18603df8b3d602fa4bc7` |

**Resultado:** os dois pares possuem hashes idênticos. Isso confirma que, no momento da verificação, os arquivos publicados eram byte a byte iguais aos intermediários dessa execução. **Não** torna a publicação atômica nem impede substituições futuras nos caminhos fixos.

### 8.3. Comandos para reproduzir a inspeção

Executar na raiz do repositório **após acionar a DAG com sucesso**, substituindo o diretório de execução pelo `run_id` sanitizado da execução que se deseja inspecionar:

```bash
RUN_DIR="airflow/data/runs/manual__2026-10-22T12_20_39_753264_00_00/training"

# Verificar métricas geradas na execução:
cat "$RUN_DIR/metrics.json"

# Verificar se os arquivos publicados são idênticos aos intermediários:
shasum -a 256 \
  "$RUN_DIR/pipeline.joblib" \
  artifacts/baseline_pipeline.joblib

shasum -a 256 \
  "$RUN_DIR/label_mapping.json" \
  artifacts/label_mapping.json

# Verificar se dados de execução e segredos são ignorados pelo Git:
git check-ignore -v "$RUN_DIR/metrics.json" .env

# Conferir os arquivos da DAG que ainda precisam ser versionados:
git status --short --untracked-files=all -- airflow/
```

Os hashes de cada par devem coincidir. Se uma nova execução publicar outro modelo, é esperado que os hashes mudem; a comparação deve ser feita com o diretório correspondente à execução que publicou os arquivos atuais.

### 8.4. Política de versionamento e pendências

- **Versionar:** `airflow/Dockerfile`, `airflow/dags/banking77_training_pipeline.py`, `compose.airflow.yaml`, código de aplicação, testes e documentação.
- **Ignorar:** `airflow/data/`, `airflow/logs/`, `.env`, caches e artefatos gerados. A exclusão de `airflow/data/` e `.env` foi confirmada com `git check-ignore -v`; `git status --short --untracked-files=all -- airflow/` passou a listar apenas `airflow/Dockerfile` e a DAG.
- **Preservar a limitação conhecida:** publicação final em caminhos fixos, por cópia, ainda sem mecanismo atômico ou versionamento por modelo.
- **Antes do commit:** executar `git diff --check`, `uv run ruff check .` e `uv run pytest`; conferir `git status --short` e revisar os arquivos incluídos no stage. A execução mais recente desses testes não foi repetida nesta verificação de hashes.
