# Banking Intent Classifier

Projeto desenvolvido para o **Tech Challenge — Fase 3 da Pós-Tech FIAP
em Machine Learning Engineering**.

O projeto tem como objetivo desenvolver uma solução de Machine Learning
capaz de identificar automaticamente a intenção presente em mensagens de
clientes de serviços bancários, explorando técnicas de **Processamento
de Linguagem Natural (NLP)** e práticas relacionadas ao ciclo de vida de
modelos em produção.


> **Estado mais recente (23/10/2026):** a DAG Airflow 3.1.0 `banking77_training_pipeline` executou `ingest → train → publish` com sucesso em 22/10, após correções de comunicação com a Execution API e assinatura JWT. Consulte [Execução Airflow e decisões arquiteturais](#-execução-airflow-e-decisões-arquiteturais--checkpoint-23102026). As seções anteriores registram também checkpoints históricos, que não devem ser interpretados como pendências atuais.

## 👥 Equipe

| Nome | RM | E-mail | Áreas de atuação                                            |
| :--- | :---: | :--- |:------------------------------------------------------------|
| **Marcelo da Cruz Salvador** | **RM375166** | [macrusal@gmail.com](mailto:macrusal@gmail.com) | Software/Backend Engineering · Data · Machine Learning · MLOps |

## 🚀 Setup rápido

### Pré-requisitos

Para reproduzir o estado atual do projeto é necessário ter instalado:

-   **Git**
-   **uv**
-   **Python >= 3.12**

O projeto utiliza o **uv** para gerenciamento do ambiente Python e das
dependências. As dependências estão declaradas no `pyproject.toml` e as
versões resolvidas são mantidas no `uv.lock`.

> **Ambiente validado durante o desenvolvimento:** `uv 0.12.13`, Python
> `3.14.5` executado pelo ambiente gerenciado pelo `uv` e
> `pytest 9.1.1`. O projeto declara `requires-python = ">=3.12"`;
> portanto, Python `3.14.5` é a versão validada nesta execução, e não
> uma exigência exclusiva.

### Clonar o repositório

```bash
git clone https://github.com/macrusal/banking-intent-classifier.git
cd banking-intent-classifier
```

### Sincronizar o ambiente

```bash
uv sync
```

Saída observada no ambiente validado:

```text
Resolved 55 packages
Checked 53 packages
```

Os tempos exibidos pelo `uv` podem variar entre ambientes.

### Validar o ambiente

```bash
uv --version
uv run python --version
uv run pytest --version
```

Versões observadas:

```text
uv 0.12.13
Python 3.14.5
pytest 9.1.1
```

> O Python global da máquina não é utilizado como referência de
> reprodução. Os comandos do projeto devem ser executados por meio de
> `uv run`.

---
## 🔁 Reprodutibilidade

Uma afirmação quantitativa apresentada neste README deve estar
associada, sempre que aplicável, a um comando versionado capaz de
reproduzi-la.

### Catálogo de comandos

| Objetivo | Comando |
| :--- | :--- |
| Sincronizar ambiente e dependências | `uv sync` |
| Verificar o Python do ambiente | `uv run python --version` |
| Executar EDA e validações do BANKING77 | `uv run python -m banking_intent_classifier.main` |
| Comparar configurações de stopwords | `uv run python -m banking_intent_classifier.experiment` |
| Treinar e validar o baseline formal | `uv run python -m banking_intent_classifier.baseline` |
| Treinar, avaliar e persistir o modelo final e as 77 classes | `uv run python -m banking_intent_classifier.final_training` |
| Iniciar a API de inferência | `uv run uvicorn banking_intent_classifier.presentation.api:app --reload` |
| Testar os endpoints HTTP | `uv run pytest tests/presentation/test_api.py -v` |
| Executar a suíte automatizada | `uv run pytest` |
| Testar a orquestração do treinamento final | `uv run pytest tests/test_final_training.py -v` |
| Testar a integração ponta a ponta do Airflow | `uv run pytest tests/application/test_training_pipeline_integration.py -v` |
| Validar configuração Docker Compose do Airflow | `docker compose -f compose.airflow.yaml config --quiet` |
| Subir o ambiente Airflow | `docker compose -f compose.airflow.yaml up -d --build` |
| Conferir DAGs e erros de importação | `docker compose -f compose.airflow.yaml exec airflow-scheduler airflow dags list-import-errors` |
| Testar as operações preparatórias do Airflow | `uv run pytest tests/application/test_training_pipeline.py tests/test_dataset_repository.py -v` |
| Verificar a qualidade do código com Ruff | `uv run ruff check .` |
| Reproduzir as verificações do CI com dependências travadas | `uv sync --frozen && uv run --frozen ruff check . && uv run --frozen pytest` |
| Construir a imagem Docker utilizada no CI (após gerar artefatos) | `docker build -t banking-intent-classifier:ci .` |
| Construir a imagem Docker (após gerar os artefatos) | `docker build -t banking-intent-classifier:local .` |
| Iniciar a API no Docker | `docker run --rm --name banking-intent-api -p 8001:8000 banking-intent-classifier:local` |
| Testar a API no Docker | `curl -s http://localhost:8001/health` |

### Reproduzir a EDA e as validações

```bash
uv run python -m banking_intent_classifier.main
```

Resultados estruturais esperados:

```text
BANKING77
========================================
Total de registros: 13083
Mesmas classes em treino e teste: True

TREINO
---
Registros: 10003
Classes: 77
Textos ausentes: 0
Labels ausentes: 0
Textos vazios: 0
Registros duplicados: 0

TESTE
---
Registros: 3080
Classes: 77
Textos ausentes: 0
Labels ausentes: 0
Textos vazios: 0
Registros duplicados: 0
Textos presentes em treino e teste: 0
```

A mesma execução apresenta distribuição das classes, comprimentos,
percentis, possíveis outliers por IQR, características do corpus e
tokens mais frequentes.

| Análise | Resultado esperado |
| :--- | ---: |
| Registros totais | 13.083 |
| Treino oficial | 10.003 |
| Teste oficial | 3.080 |
| Classes | 77 |
| Textos compartilhados entre treino e teste | 0 |
| Frequência mínima por classe | 35 |
| Frequência máxima por classe | 187 |
| Média por classe | 129,91 |
| Mediana por classe | 127 |
| Total de palavras no treino | 119.530 |
| Vocabulário bruto | 4.518 |
| Vocabulário após lowercase | 4.136 |
| Vocabulário após lowercase + tratamento de pontuação | 2.452 |

> O Hugging Face Hub pode exibir um aviso sobre requisições sem
> `HF_TOKEN`. O aviso não impede a execução; autenticação é necessária
> apenas para limites mais altos e downloads potencialmente mais
> rápidos.

### Reproduzir os testes automatizados

```bash
uv run pytest
```

No checkpoint histórico desta etapa inicial:

```text
20 passed
```

Na validação de 17/10/2026, a suíte completa apresentou **31 testes aprovados**. Em **21/10/2026**, após a preparação do pipeline para o Airflow, a execução local apresentou **35 testes aprovados**, sem falhas, e um aviso de depreciação do Starlette/httpx. O comando de reprodução permanece o mesmo.

O tempo total pode variar entre máquinas.

### Reproduzir o experimento de stopwords

O experimento que compara `stop_words=None` com
`stop_words="english"` possui um ponto de entrada próprio e pode ser
reproduzido diretamente pelo terminal:

```bash
uv run python -m banking_intent_classifier.experiment
```

O experimento utiliza um split interno estratificado e reprodutível
(`random_state=42`) sobre o conjunto oficial de treinamento do BANKING77.

O conjunto oficial de teste permanece preservado e não participa dessa
decisão de configuração.

Resultados esperados:

```text
EXPERIMENTO DE STOPWORDS
==================================================

Configuração: stop_words=None
Accuracy: 0.8491
Macro F1: 0.8412
Weighted F1: 0.8482

Configuração: stop_words=english
Accuracy: 0.8206
Macro F1: 0.8137
Weighted F1: 0.8198
```

Nas condições deste experimento, `stop_words=None` apresentou o melhor
resultado, com **Macro F1 de 0.8412**, contra **0.8137** utilizando
`stop_words="english"`.

Por esse motivo, `stop_words=None` foi selecionado para a configuração
do baseline.


### Reproduzir o baseline formal

Após comparar as configurações de pré-processamento, o projeto consolidou
um **baseline formal** usando um `Pipeline` do scikit-learn. O Pipeline
integra `TfidfVectorizer(stop_words=None)` e
`LogisticRegression(max_iter=1000)`, garantindo que o mesmo
pré-processamento ajustado durante o treinamento seja utilizado na
inferência.

O baseline utiliza apenas o split oficial de **treinamento** do
BANKING77 (10.003 registros), dividido internamente com estratificação,
`validation_size=0.2` e `random_state=42`:

| Conjunto | Registros |
| :--- | ---: |
| Treino interno | 8.002 |
| Validação interna | 2.001 |

Para reproduzir:

```bash
uv run python -m banking_intent_classifier.baseline
```

Saída observada na execução validada:

```text
BASELINE FORMAL — BANKING77
==================================================
Treino interno: 8002
Validação interna: 2001
Configuração: TF-IDF + Logistic Regression | stop_words=None
Accuracy: 0.8491
Macro F1: 0.8412
Weighted F1: 0.8482
```

Essas métricas reproduzem os resultados do experimento anterior para
`stop_words=None`. O TF-IDF é ajustado somente no treino interno; os
dados de validação são transformados com o Pipeline já ajustado. O
**teste oficial (3.080 registros) não foi utilizado** para selecionar ou
validar essa configuração e permanece reservado para a avaliação final.

Os testes automatizados incluem verificações da configuração do Pipeline
e da orquestração do comando `baseline`, além dos testes já existentes.
Na execução registrada, **20 testes passaram**:

```bash
uv run pytest
```

---
## 🧪 Treinamento final, artefatos e API HTTP

### Treinamento oficial e persistência

Após definir a configuração do baseline com validação interna, o modelo
é treinado novamente no **split oficial de treino** do BANKING77 (10.003
registros) e avaliado no **split oficial de teste** (3.080 registros).
O conjunto oficial de teste não foi utilizado para selecionar a
configuração do baseline.

```bash
uv sync
uv run python -m banking_intent_classifier.final_training
```

Saída observada:

```text
AVALIAÇÃO FINAL — BANKING77
==================================================
Treinamento oficial: 10003
Teste oficial: 3080
Accuracy: 0.8769
Macro F1: 0.8769
Weighted F1: 0.8769
Artefato salvo em: artifacts/baseline_pipeline.joblib
Classes persistidas: 77
Mapeamento salvo em: artifacts/label_mapping.json
```

O treinamento gera os seguintes artefatos locais:

| Arquivo | Conteúdo |
| :--- | :--- |
| `artifacts/baseline_pipeline.joblib` | Pipeline treinado com TF-IDF e Logistic Regression |
| `artifacts/label_mapping.json` | Lista ordenada dos nomes das 77 intenções; índice = ID da classe |

A pasta `artifacts/` é ignorada pelo Git: **os artefatos precisam ser
gerados localmente antes de iniciar a API**. Não carregue arquivos
`joblib` de fontes não confiáveis. O Hugging Face Hub pode apresentar um
aviso de acesso sem `HF_TOKEN`; nas execuções registradas isso não
impediu o treinamento.

Para verificar os metadados persistidos:

```bash
uv run python -c "from pathlib import Path; from banking_intent_classifier.infrastructure.label_repository import LabelRepository; labels = LabelRepository.load(Path('artifacts/label_mapping.json')); print('Total:', len(labels)); print('Classe 11:', labels[11])"
```

Resultado esperado:

```text
Total: 77
Classe 11: card_arrival
```

### Executar a API FastAPI

A API carrega o modelo e o mapeamento de classes durante a inicialização,
sem consultar o Hugging Face Hub a cada requisição. Instale as
dependências do projeto e gere os artefatos antes de iniciá-la:

```bash
uv sync
uv run python -m banking_intent_classifier.final_training
uv run uvicorn banking_intent_classifier.presentation.api:app --reload
```

Servidor local: `http://127.0.0.1:8000`.
Documentação interativa (OpenAPI/Swagger): `http://127.0.0.1:8000/docs`.

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| GET | `/health` | Retorna o estado operacional básico da API |
| POST | `/predict` | Classifica uma mensagem e retorna ID e nome da intenção |

Em outro terminal, teste o endpoint de saúde:

```bash
curl -s http://127.0.0.1:8000/health
```

Resposta observada:

```json
{"status":"ok"}
```

Teste a inferência real:

```bash
curl -s -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"I am still waiting on my card"}'
```

Resposta observada com os artefatos gerados nesta execução:

```json
{"intent_id":11,"intent":"card_arrival"}
```

O endpoint exige um campo `text` não vazio; entradas vazias ou somente
com espaços são rejeitadas com HTTP 422. O endpoint `/health` não deve
ser interpretado como uma verificação completa de prontidão do modelo.

### Executar a API no Docker

A imagem Docker permite executar a mesma API em um contêiner, sem
instalar as dependências Python diretamente na máquina anfitriã.
**O treinamento não acontece durante o build:** os artefatos locais
precisam existir antes da construção da imagem.

#### 1. Preparar os artefatos e conferir o Docker

Na raiz do repositório, execute:

```bash
uv sync
uv run python -m banking_intent_classifier.final_training
ls -lh artifacts/baseline_pipeline.joblib artifacts/label_mapping.json
docker info --format '{{.ServerVersion}}'
```

A execução de `final_training` gera o modelo e o mapeamento das 77 classes.
Se o Docker informar que não consegue se conectar ao daemon, inicie o
Docker Desktop e repita a verificação.

#### 2. Construir a imagem

```bash
docker build -t banking-intent-classifier:local .
```

O `Dockerfile` utiliza `python:3.12-slim`, instala as dependências com
`uv` a partir de `pyproject.toml` e `uv.lock`, copia o código de `src/`
e incorpora os dois arquivos de `artifacts/`. O `.dockerignore` evita
incluir arquivos locais desnecessários, mas **não exclui `artifacts/`**.

> Atenção: a versão do Python usada no desenvolvimento pode diferir da
> versão da imagem. A persistência via `joblib` requer compatibilidade
> entre as bibliotecas utilizadas no treinamento e na inferência.
> Por isso, valide o carregamento e uma predição real após cada alteração
> relevante de dependências ou da imagem.

#### 3. Iniciar o servidor containerizado

```bash
docker run --rm \
  --name banking-intent-api \
  -p 8001:8000 \
  banking-intent-classifier:local
```

A porta **8001** do computador é encaminhada para a porta **8000** do
contêiner. Mantenha esse terminal aberto durante os testes. Para
interromper o servidor, utilize `Ctrl+C`.

#### 4. Verificar os endpoints e a resposta

Em outro terminal, execute:

```bash
curl -s http://localhost:8001/health
```

Resposta esperada:

```json
{"status":"ok"}
```

Em seguida, teste a classificação de intenção:

```bash
curl -s -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"I am still waiting on my card"}'
```

**Resposta observada em execução real do contêiner:**

```json
{"intent_id":11,"intent":"card_arrival"}
```

A documentação interativa também fica disponível em
`http://localhost:8001/docs`. Nela, selecione `POST /predict`, clique
em **Try it out**, informe o JSON da requisição e execute.

#### 5. Testar localmente e solucionar problemas

A suíte automatizada continua sendo executada no ambiente `uv`:

```bash
uv run pytest
```

| Sintoma | Verificação ou correção |
| :--- | :--- |
| `Cannot connect to the Docker daemon` | Iniciar Docker Desktop e conferir `docker info` |
| Erro no `COPY artifacts/` durante o build | Gerar os dois artefatos com `uv run python -m banking_intent_classifier.final_training` |
| Falha ao carregar o modelo | Verificar compatibilidade de Python, scikit-learn e joblib entre treinamento e imagem |
| Porta `8001` ocupada | Interromper o processo existente ou publicar outra porta, por exemplo `-p 8002:8000` |
| API não responde | Consultar a saída do contêiner e confirmar o mapeamento de portas |

**Reprodutibilidade:** a sequência completa é gerar os artefatos,
construir a imagem, iniciar o contêiner e chamar `/health` e `/predict`.
O modelo e o JSON de classes são artefatos gerados localmente e não são
versionados no Git. Para uma imagem atualizada após novo treinamento,
execute novamente o `docker build`.

### Testes automatizados

```bash
uv run pytest tests/application/test_prediction_service.py -v
uv run pytest tests/presentation/test_api.py -v
uv run pytest tests/test_final_training.py tests/test_model_repository.py tests/test_label_repository.py -v
uv run pytest
```

**Execução registrada em 17/10/2026:** 31 testes aprovados, nenhuma falha,
1 aviso `StarletteDeprecationWarning` relacionado ao uso de `httpx`
com `starlette.testclient`. O aviso não impediu a execução, mas deverá
ser revisado na etapa de atualização de dependências/CI.

### Organização da funcionalidade

| Camada | Componente | Responsabilidade |
| :--- | :--- | :--- |
| Application | `application/prediction_service.py` | Valida o texto e executa a predição |
| Infrastructure | `infrastructure/model_repository.py` | Persiste e carrega o Pipeline joblib |
| Infrastructure | `infrastructure/label_repository.py` | Persiste e carrega os nomes ordenados das classes |
| Presentation | `presentation/api.py` | Define contratos HTTP, ciclo de vida e endpoints FastAPI |
| Orquestração | `final_training.py` | Treina, avalia e produz os dois artefatos |

A API e os testes de integração podem ser reproduzidos sem baixar o
dataset, desde que os artefatos já tenham sido gerados; os testes
substituem o carregamento dos artefatos por mocks.

---

## 🔄 Integração Contínua (CI/CD) — GitHub Actions

O projeto utiliza **GitHub Actions** para validar automaticamente a
qualidade do código, os testes e a construção da imagem Docker. O workflow
versionado está em [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

### Eventos e verificações

O workflow é acionado em `push` e `pull_request` para as branches `dev` e
`main`, além de permitir execução manual por `workflow_dispatch`.

| Job | Verificação | Comando ou mecanismo |
| :--- | :--- | :--- |
| `lint` | Análise estática do código | `uv run --frozen ruff check .` |
| `tests` | Suíte automatizada | `uv run --frozen pytest` |
| `docker-build` | Treinamento, verificação dos artefatos e construção da imagem | `uv run --frozen python -m banking_intent_classifier.final_training` e `docker/build-push-action@v6` |
| `validate-gitflow` | Verifica a origem dos PRs para `main` | Validação de `github.base_ref` e `github.head_ref` |

Os **quatro jobs são independentes e podem executar em paralelo**. Não há
uma dependência sequencial configurada entre lint, testes e build. O build
valida a construção da imagem, mas **não publica** a imagem em registry
(`push: false`) nem realiza deploy.

### Política de integração GitFlow

O job `validate-gitflow` verifica a origem de Pull Requests: quando o destino
é `main`, a origem deve ser `dev`. PRs de `feature/*` ou `hotfix/*`
diretamente para `main` são reprovados pelo job. PRs para `dev` e execuções
de `push` não são bloqueados por essa verificação.

```text
feature/* → dev → main
```

**Importante:** a reprovação de um job só impede o merge quando o respectivo
check é configurado como obrigatório na proteção da `main` (Ruleset ou
Branch protection). Confirme no GitHub que `GitFlow - Validar origem do PR`
está entre os checks exigidos. A política não equivale a uma restrição
independente de alterações no próprio workflow.

### Reprodução local do CI

Execute na raiz do repositório, com `uv`, Python 3.12 ou superior e Docker
disponíveis:

```bash
# Instalar as dependências conforme o lockfile
uv sync --frozen

# Reproduzir os dois controles de qualidade
uv run --frozen ruff check .
uv run --frozen pytest

# Gerar os artefatos que não são versionados no Git
uv run --frozen python -m banking_intent_classifier.final_training

# Confirmar a presença dos arquivos gerados
test -s artifacts/baseline_pipeline.joblib
test -s artifacts/label_mapping.json

# Reproduzir o build da imagem
docker build -t banking-intent-classifier:ci .
```

O `docker-build` do GitHub Actions executa o treinamento **antes** de
construir a imagem, pois a pasta `artifacts/` é ignorada pelo Git. O job
valida que `baseline_pipeline.joblib` e `label_mapping.json` existem e
não estão vazios. A execução requer acesso ao dataset BANKING77 no
Hugging Face Hub; o download e o treinamento podem aumentar o tempo de CI.

### Evidências de execução

Em **17/10/2026**, as três verificações originais passaram no Pull Request de
adição do build Docker e novamente após o merge na branch `dev`, conforme
validação informada e capturas do GitHub Actions:

| Verificação no Pull Request | Resultado | Duração observada |
| :--- | :--- | ---: |
| Ruff — Análise estática | Aprovado | 11 s |
| Pytest — Testes automatizados | Aprovado | 16 s |
| Docker — Build da imagem | Aprovado | 35 s |

A suíte completa também foi executada localmente com **31 testes
aprovados** e um aviso de depreciação do Starlette/httpx, sem falhas.

Para consultar as execuções e os logs dos jobs, acesse a
[aba Actions do repositório](https://github.com/macrusal/banking-intent-classifier/actions).
Os registros de execução no GitHub são a evidência verificável; os tempos
acima são apenas observações e podem variar entre execuções.

O job `validate-gitflow` foi adicionado posteriormente; seu histórico e
resultado devem ser consultados na aba Actions.

Esta entrega atende à frente técnica de **CI/CD** do Tech Challenge —
Fase 3. A documentação das demais frentes da rubrica será incorporada
conforme suas validações forem concluídas.

---

## 🛠️ Preparação do pipeline de treinamento para Airflow (21/10/2026)

A preparação das operações reutilizáveis foi concluída na branch de funcionalidade, **sem implantação ou execução de DAG no Apache Airflow até este checkpoint**. A decisão é manter a lógica de Machine Learning independente do orquestrador: a futura DAG apenas coordenará chamadas já existentes.

| Componente | Responsabilidade |
| :--- | :--- |
| `application/training_service.py` | `train_and_evaluate(dataset)`: criar o baseline, ajustar, prever, avaliar e recuperar nomes das classes |
| `application/training_pipeline.py` | Expor `ingest_data`, `train_model` e `save_artifacts` como operações reutilizáveis |
| `infrastructure/data/dataset_repository.py` | Salvar e carregar `DatasetDict` com validação dos splits e colunas |
| `final_training.py` | Manter o comando independente para treinamento, avaliação e persistência oficiais |

### Fluxo planejado

```text
ingest_data(dataset_path)
          ↓
train_model(dataset_path, output_path)
          ↓
save_artifacts(training_path, artifact_path, label_mapping_path)
```

A ingestão persiste os dados no disco; o treinamento gera `pipeline.joblib`, `label_mapping.json` e `metrics.json`; a publicação valida os intermediários e copia modelo e classes para os caminhos utilizados pela API. A futura DAG deverá compartilhar os arquivos entre tarefas sem transferir o dataset inteiro por XCom. **O teste de integração entre as três operações e a DAG ainda estão pendentes.** A publicação atual por cópia de arquivos não é atômica.

### Reproduzir as verificações disponíveis

```bash
uv run ruff check .
uv run pytest tests/test_final_training.py -v
uv run pytest tests/application/test_training_pipeline.py tests/test_dataset_repository.py -v
uv run pytest
uv run python -m banking_intent_classifier.final_training
```

Em **21/10/2026**, a execução local de Ruff e da suíte completa foi reportada com **35 testes aprovados, 0 falhas e 1 aviso de depreciação Starlette/httpx**. O comando `final_training` reproduz as métricas oficiais documentadas anteriormente (accuracy, macro F1 e weighted F1 de `0.8769`). A execução isolada das operações preparatórias e seu teste ponta a ponta não devem ser tratados como validados até que haja evidência específica.

**Decisão de testes:** após a extração de `train_and_evaluate()` para `training_service.py`, o teste da CLI passou a verificar a delegação e a persistência, sem esperar chamadas internas a `fit()` e `predict()`. O dataset simulado foi substituído por `Dataset`/`DatasetDict` do Hugging Face, porque `len()` em um dicionário comum conta chaves e não registros. A cobertura específica das chamadas internas do serviço é um próximo passo.

Para justificativas e lições aprendidas, consulte [Preparação do pipeline para Airflow](docs/study-notes/airflow-training-pipeline.md) e o [índice de notas de estudo](docs/study-notes/README.md).

---

## 🎯 Contexto e problema

Canais digitais de atendimento bancário recebem mensagens escritas de
diferentes formas para representar necessidades semelhantes. Antes que
uma solicitação possa ser direcionada para um fluxo de atendimento
adequado, é necessário identificar qual intenção está associada à
mensagem do cliente.

Esse cenário pode ser tratado como um problema de **classificação
multiclasse de textos**:

```text
Mensagem do cliente
        │
        ▼
Classificador de intenção
        │
        ▼
Intent identificada
        │
        ▼
Fluxo de atendimento correspondente
```

O problema investigado pelo projeto é:

> **Como classificar automaticamente mensagens de clientes de serviços
> bancários de acordo com sua intenção, utilizando técnicas de
> Processamento de Linguagem Natural e Machine Learning?**

## 💡 Proposta de solução

A proposta é construir progressivamente um classificador de intenções
bancárias.

A entrada do modelo será uma mensagem textual, por exemplo:

```text
I am still waiting on my card?
```

e a saída esperada será a intenção correspondente:

```text
card_arrival
```

Conceitualmente, a solução pode ser representada por:

```text
Texto
  │
  ▼
Representação textual
  │
  ▼
Modelo de classificação
  │
  ▼
Intent
```

O desenvolvimento será realizado de forma incremental, começando pela
compreensão e validação dos dados, passando pela construção de um modelo
baseline e evoluindo posteriormente para disponibilização, automação,
monitoramento e otimização da solução.

A estratégia inicial de modelagem prevista é:

```text
Texto
  │
  ▼
TF-IDF
  │
  ▼
Logistic Regression
  │
  ▼
Intent
```

Essa abordagem permitirá estabelecer um **baseline mensurável** antes da
avaliação de estratégias adicionais.

## 🏦 Por que o BANKING77?

O **BANKING77** foi escolhido por representar diretamente um problema
supervisionado de classificação textual no domínio bancário.

Sua estrutura atende ao objetivo do projeto:

```text
text → label
```

O conjunto utilizado possui:

-   **13.083 mensagens**;
-   **10.003 registros de treinamento**;
-   **3.080 registros de teste**;
-   **77 classes de intenção**.

Entre as intenções presentes no dataset estão, por exemplo:

```text
card_arrival
card_not_working
cash_withdrawal_charge
declined_transfer
pending_card_payment
lost_or_stolen_card
verify_my_identity
wrong_exchange_rate_for_cash_withdrawal
```

A escolha também permite trabalhar com um cenário mais desafiador do que
uma classificação binária simples. O modelo deverá distinguir **77
intenções**, incluindo categorias semanticamente próximas.

Isso possibilita explorar aspectos relevantes de NLP e Machine Learning,
como:

-   representação textual;
-   classificação multiclasse;
-   distribuição e balanceamento das classes;
-   avaliação global e por classe;
-   análise de erros;
-   capacidade de generalização para diferentes formas de expressar uma
    mesma intenção.

## 🚀 Objetivo técnico

Além da construção do classificador, o projeto busca percorrer
progressivamente etapas relevantes do ciclo de vida de uma solução de
Machine Learning:

```text
Dataset
   │
   ▼
Validação e EDA
   │
   ▼
Preparação dos textos
   │
   ▼
Treinamento
   │
   ▼
Avaliação
   │
   ▼
API de inferência
   │
   ▼
Containerização
   │
   ▼
Automação
   │
   ▼
Monitoramento
   │
   ▼
Otimização
```

Dessa forma, o projeto não se limita ao treinamento de um modelo. A
proposta é evoluir para uma solução organizada, reproduzível, avaliável
e preparada para as demais etapas previstas no Tech Challenge.

---
## 🚀 Status do Projeto

> 🚧 **Em desenvolvimento — EDA, baseline, avaliação oficial, API, Docker, CI e DAG Airflow executada com sucesso; monitoramento, ONNX, benchmark e arquitetura cloud pendentes.**

O desenvolvimento está sendo realizado de forma incremental, mantendo o
histórico de commits e Pull Requests como registro da evolução técnica e
das decisões realizadas durante o projeto.

### ✅ Estrutura e arquitetura inicial

-   [x] Criar estrutura inicial do projeto
-   [x] Configurar projeto Python com `uv`
-   [x] Organizar o código utilizando separação de responsabilidades
-   [x] Criar camadas iniciais de `application`, `domain` e
    `infrastructure`
-   [x] Criar camada `presentation` para apresentação dos resultados
-   [x] Manter o `main.py` responsável apenas pela orquestração da
    aplicação
-   [x] Separar análise dos dados da apresentação no console
-   [x] Documentar arquitetura inicial

#### Organização das responsabilidades

A estrutura do projeto está sendo evoluída de forma incremental,
buscando manter responsabilidades bem definidas e aplicar princípios de
design como o **Single Responsibility Principle (SRP)**.

Atualmente, as principais responsabilidades estão organizadas da
seguinte forma:

| Componente | Responsabilidade |
| :--- | :--- |
| `domain` | Representação dos objetos e resultados das análises |
| `application` | Execução das análises e regras da aplicação |
| `infrastructure` | Integração e carregamento de fontes externas de dados |
| `presentation` | Formatação e apresentação dos resultados |
| `main.py` | Orquestração do fluxo de EDA |
| `experiment.py` | Execução reproduzível da comparação de stopwords |
| `baseline.py` | Treinamento e validação interna do baseline formal |

Dentro da camada `application`, as responsabilidades da EDA também foram
separadas para evitar que um único serviço concentre diferentes tipos de
análise:

| Componente | Responsabilidade |
| :--- | :--- |
| `DatasetService` | Análise estrutural e qualidade básica do dataset |
| `ClassDistributionAnalyzer` | Distribuição das classes e estatísticas de balanceamento |
| `TextLengthAnalyzer` | Comprimento dos textos, percentis e identificação de possíveis outliers |
| `CorpusAnalyzer` | Características do corpus e frequência dos tokens |
| `DatasetSplitter` | Split interno estratificado e reprodutível para treino e validação |
| `TextPreprocessingExperiment` | Execução e comparação dos experimentos de pré-processamento textual |
| `ModelTrainer` | Criação do classificador e do Pipeline TF-IDF + Logistic Regression |
| `ModelEvaluator` | Cálculo de Accuracy, Macro F1 e Weighted F1 |

A apresentação dos resultados no terminal permanece isolada no
`ConsoleReporter`, evitando que o ponto de entrada da aplicação
concentre regras de análise e formatação de saída.

Essa organização permite que cada componente tenha uma responsabilidade
mais coesa e possa evoluir de forma independente à medida que novas
etapas forem incorporadas ao projeto.

### 📐 Documentação da arquitetura

A arquitetura do projeto é documentada em
[`docs/architecture.md`](docs/architecture.md).

Esse documento concentra as decisões arquiteturais e a evolução da
organização interna do projeto, enquanto este README apresenta uma visão
resumida do estado atual da implementação.

A estrutura foi evoluída incrementalmente para manter responsabilidades
bem definidas e evitar que um único serviço concentre diferentes tipos
de análise.

A organização atual inclui:

```text
src/banking_intent_classifier/
├── application/
│   ├── class_distribution_analyzer.py
│   ├── corpus_analyzer.py
│   ├── dataset_service.py
│   ├── dataset_splitter.py
│   ├── model_evaluator.py
│   ├── model_trainer.py
│   ├── text_length_analyzer.py
│   └── text_preprocessing_experiment.py
├── domain/
│   ├── dataset_summary.py
│   └── experiment_result.py
├── infrastructure/
│   └── data/
│       └── banking77_loader.py
├── presentation/
│   └── console_reporter.py
├── baseline.py
├── experiment.py
└── main.py
```

A separação das análises de distribuição de classes, comprimento dos
textos e características do corpus foi realizada como uma refatoração
estrutural, mantendo o comportamento previamente validado da aplicação.

Os testes automatizados foram utilizados como rede de segurança durante
essa evolução, permitindo extrair as responsabilidades progressivamente
e verificar que os resultados da EDA permaneceram inalterados.

### ✅ Dataset e carregamento

-   [x] Definir BANKING77 como dataset do projeto
-   [x] Utilizar a fonte oficial `PolyAI/banking77`
-   [x] Implementar carregamento através do Hugging Face
-   [x] Validar os splits de treino e teste
-   [x] Confirmar 13.083 registros
-   [x] Confirmar as 77 classes em ambos os splits

### ✅ Validação estrutural dos dados

A validação inicial do BANKING77 foi concluída com os seguintes
resultados:

| Validação | Treino | Teste |
| :--- | ---: | ---: |
| Registros | 10.003 | 3.080 |
| Classes | 77 | 77 |
| Textos ausentes | 0 | 0 |
| Labels ausentes | 0 | 0 |
| Textos vazios | 0 | 0 |
| Registros duplicados | 0 | 0 |

Também foi verificada a existência de textos compartilhados entre os
conjuntos de treino e teste:

```text
Textos presentes em treino e teste: 0
```

Com isso, não foram identificados problemas estruturais que exijam,
neste momento, remoção, imputação ou correção de registros.

A ausência de textos compartilhados entre os splits também reduz o risco
de data leakage decorrente da presença da mesma mensagem nos conjuntos
de treino e teste.

### 🔄 Análise Exploratória dos Dados — EDA

Com a validação estrutural concluída, foi iniciada a **Análise
Exploratória dos Dados (EDA)** do BANKING77.

A análise está sendo realizada de forma incremental, com cada etapa
implementada e validada separadamente antes do avanço para a próxima
análise.

#### ✅ Distribuição das classes

O conjunto de treinamento possui **10.003 registros distribuídos entre
77 intents**.

As frequências observadas apresentam as seguintes estatísticas:

| Métrica | Exemplos por classe |
| :--- | ---: |
| Mínimo | 35 |
| Máximo | 187 |
| Média | 129,91 |
| Mediana | 127 |

Entre as classes com menor quantidade de exemplos estão:

-   `contactless_not_working`: 35
-   `virtual_card_not_working`: 41
-   `card_acceptance`: 59
-   `card_swallowed`: 61

Entre as classes com maior quantidade de exemplos estão:

-   `card_payment_fee_charged`: 187
-   `direct_debit_payment_not_recognised`: 182
-   `balance_not_updated_after_cheque_or_cash_deposit`: 181
-   `wrong_amount_of_cash_received`: 180

A distribuição das classes não é perfeitamente uniforme. A maior classe
possui aproximadamente **5,34 vezes** a quantidade de exemplos da menor
classe.

Neste momento, nenhuma técnica de balanceamento será aplicada. A
necessidade de estratégias específicas para lidar com o desbalanceamento
será avaliada posteriormente a partir dos resultados do modelo baseline
e de métricas adequadas para classificação multiclasse, especialmente o
desempenho por classe e o **Macro F1**.

#### ✅ Comprimento dos textos

Também foram analisados os comprimentos das mensagens presentes no
conjunto de treinamento, considerando tanto a quantidade de caracteres
quanto a quantidade de palavras.

| Métrica | Caracteres | Palavras |
| :--- | ---: | ---: |
| Mínimo | 13 | 2 |
| Máximo | 433 | 79 |
| Média | 59,47 | 11,95 |
| Mediana | 47 | 10 |

Os resultados mostram que as mensagens do BANKING77 são, em geral,
relativamente curtas.

A média superior à mediana, tanto em caracteres quanto em palavras,
indica uma distribuição assimétrica à direita, com a presença de
mensagens mais longas na cauda da distribuição.

#### ✅ Distribuição do comprimento dos textos

Para compreender melhor essa distribuição, também foram calculados os
principais percentis dos comprimentos das mensagens.

| Percentil | Caracteres | Palavras |
| :--- | ---: | ---: |
| P25 | 36,00 | 7,00 |
| P50 | 47,00 | 10,00 |
| P75 | 64,00 | 13,00 |
| P90 | 110,00 | 22,00 |
| P95 | 152,00 | 29,80 |
| P99 | 221,96 | 43,00 |

Os resultados mostram que **75% das mensagens possuem até 64 caracteres
e 13 palavras**, enquanto **90% possuem até 110 caracteres e 22
palavras**.

A diferença entre os percentis superiores e a mediana confirma a
existência de uma cauda de mensagens mais longas no conjunto de
treinamento.

#### ✅ Análise de possíveis outliers

Para identificar valores extremos na distribuição do comprimento dos
textos, foi utilizado o critério do **Intervalo Interquartil (IQR)**.

Os limites e resultados encontrados foram:

| Medida | Limite inferior | Limite superior | Possíveis outliers | Percentual |
| :--- | ---: | ---: | ---: | ---: |
| Caracteres | -6,00 | 106,00 | 1.038 | 10,38% |
| Palavras | -2,00 | 22,00 | 930 | 9,30% |

O critério IQR identificou uma cauda de mensagens mais longas,
correspondendo a aproximadamente **10% do conjunto de treinamento**.

Esses registros serão preservados, pois o comprimento elevado,
isoladamente, **não caracteriza erro ou baixa qualidade textual**. Em um
problema de classificação de intenções, mensagens mais detalhadas podem
representar exemplos legítimos do comportamento esperado dos usuários.

Dessa forma, nenhuma remoção será realizada nesta etapa da EDA. O
impacto desses exemplos será reavaliado posteriormente durante a
modelagem e a análise de desempenho do classificador.

#### ✅ Características gerais do corpus

Também foram analisadas características gerais do corpus textual do
conjunto de treinamento.

Os resultados encontrados foram:

| Métrica | Resultado |
| :--- | ---: |
| Documentos | 10.003 |
| Total de palavras | 119.530 |
| Palavras únicas — corpus bruto | 4.518 |
| Palavras únicas após lowercase | 4.136 |
| Palavras únicas após lowercase + tratamento de pontuação | 2.452 |

A conversão dos tokens para **lowercase** reduziu o vocabulário de 4.518
para 4.136 tokens únicos, uma redução de aproximadamente **8,46%**.

Ao considerar também o tratamento de caracteres de pontuação nas
extremidades dos tokens produzidos pela separação por espaços, o
vocabulário foi reduzido para 2.452 tokens únicos. Isso representa uma
redução de aproximadamente **45,73% em relação ao vocabulário bruto**.

Esses resultados indicam que diferenças de capitalização e pontuação
contribuem significativamente para a fragmentação do vocabulário. Por
esse motivo, essas transformações serão consideradas na definição do
pré-processamento utilizado na etapa de representação textual.

##### Tokens mais frequentes

Após a aplicação de lowercase e do tratamento de pontuação utilizado
nesta análise exploratória, os 20 tokens mais frequentes no conjunto de
treinamento foram:

| Token | Frequência | Token | Frequência |
| :--- | ---: | :--- | ---: |
| `i` | 8.312 | `my` | 5.684 |
| `to` | 4.038 | `a` | 3.565 |
| `the` | 3.498 | `card` | 2.672 |
| `is` | 2.376 | `it` | 1.849 |
| `do` | 1.848 | `can` | 1.842 |
| `for` | 1.581 | `how` | 1.520 |
| `what` | 1.375 | `why` | 1.365 |
| `account` | 1.348 | `you` | 1.216 |
| `and` | 1.215 | `money` | 1.130 |
| `was` | 1.090 | `transfer` | 1.081 |

Entre os tokens mais frequentes aparecem tanto palavras funcionais da
língua inglesa, como `i`, `my`, `to`, `a` e `the`, quanto termos
diretamente relacionados ao domínio bancário, como `card`, `account`,
`money` e `transfer`.

A presença de palavras funcionais entre os termos mais frequentes não
implica sua remoção automática. A utilização de **stopwords** foi
tratada como uma hipótese experimental durante a construção do primeiro
baseline, permitindo comparar configurações e avaliar seu impacto por
meio das métricas do modelo.

##### ✅ Decisão de pré-processamento baseada em experimento

A hipótese de remoção de stopwords foi avaliada de forma controlada
utilizando **TF-IDF + Logistic Regression**. Para evitar o uso do
conjunto oficial de teste durante decisões de configuração, o conjunto
de treinamento foi dividido de forma estratificada e reprodutível
(`random_state=42`):

| Conjunto experimental | Registros | Classes |
| :--- | ---: | ---: |
| Treino interno | 8.002 | 77 |
| Validação | 2.001 | 77 |

O TF-IDF é ajustado exclusivamente sobre o treino interno e aplicado
posteriormente à validação. O conjunto oficial de teste, com **3.080
registros**, permanece preservado para a avaliação final.

Foram comparadas duas configurações:

| Configuração | Accuracy | Macro F1 | Weighted F1 |
| :--- | ---: | ---: | ---: |
| `stop_words=None` | **0,8491** | **0,8412** | **0,8482** |
| `stop_words="english"` | 0,8206 | 0,8137 | 0,8198 |

Nas condições deste experimento, a remoção de stopwords reduziu o
**Macro F1 em aproximadamente 2,75 pontos percentuais**. Por isso, a
configuração escolhida para o baseline é:

```text
stop_words=None
```

Essa decisão é específica às condições avaliadas e não representa uma
regra geral para problemas de classificação textual.

#### ✅ Checkpoint atual

A EDA, o experimento de stopwords, o baseline formal e a avaliação oficial
foram concluídos. O modelo final foi persistido junto ao mapeamento das
77 classes e disponibilizado por uma API FastAPI. A suíte automatizada
possuía **31 testes aprovados** em 17/10/2026; em 21/10/2026, após a preparação para o Airflow, foram **35 testes aprovados**.

```text
BANKING77 (13.083 mensagens; 77 classes)
    │
    ├── EDA e validações                       ✅
    ├── Experimento de stopwords               ✅
    ├── Baseline formal (validação interna)    ✅
    │     ├── Accuracy:    0,8491
    │     ├── Macro F1:    0,8412
    │     └── Weighted F1: 0,8482
    ├── Treinamento e avaliação oficiais       ✅
    │     ├── Treino: 10.003 / Teste: 3.080
    │     ├── Accuracy:    0,8769
    │     ├── Macro F1:    0,8769
    │     └── Weighted F1: 0,8769
    ├── Modelo joblib + metadados JSON         ✅
    ├── API FastAPI (health + predict)         ✅
    ├── Docker (build e inferência HTTP)       ✅
    ├── Testes automatizados (35 aprovados)    ✅
    └── CI/CD (Ruff + Pytest + Docker Build)   ✅
        └── Validação de origem GitFlow        ✅
```

A containerização da API foi validada com uma inferência real no Docker.
O pipeline de CI/CD foi validado em Pull Request e após merge na `dev`,
e posteriormente promovido para `main`. A validação GitFlow foi
incorporada ao workflow; a obrigatoriedade do check depende do Ruleset.
As próximas etapas planejadas são a orquestração do treinamento com
Apache Airflow, monitoramento e otimização de latência.

### 📋 Roadmap

-   [x] Estrutura inicial do projeto
-   [x] Arquitetura inicial
-   [x] Carregamento do BANKING77
-   [x] Validação estrutural do dataset
-   [x] Análise exploratória dos dados (EDA)
    -   [x] Distribuição das classes
    -   [x] Estatísticas de balanceamento
    -   [x] Comprimento dos textos
    -   [x] Distribuição dos comprimentos
    -   [x] Análise de possíveis outliers
    -   [x] Características gerais do corpus
    -   [x] Definição e avaliação experimental do pré-processamento
        textual
-   [x] Refatoração das responsabilidades da EDA
    -   [x] Extrair análise da distribuição de classes
    -   [x] Extrair análise do comprimento dos textos
    -   [x] Extrair análise do corpus
    -   [x] Adicionar testes automatizados para os analyzers
-   [x] Primeiro baseline experimental com TF-IDF + Logistic Regression
    -   [x] Criar split interno estratificado e reprodutível
    -   [x] Comparar `stop_words=None` e `stop_words="english"`
    -   [x] Avaliar Accuracy, Macro F1 e Weighted F1
    -   [x] Selecionar `stop_words=None` com base nos resultados
-   [x] Consolidar baseline formal de modelagem
    -   [x] Integrar TF-IDF e Logistic Regression em um Pipeline
    -   [x] Reproduzir métricas na validação interna
    -   [x] Criar comando independente para execução do baseline
    -   [x] Adicionar testes do Pipeline e do entrypoint
-   [x] Avaliação final e detalhada das métricas do modelo
-   [x] API de inferência
-   [x] Containerização da API com Docker
-   [x] Pipeline CI/CD
    -   [x] Ruff — análise estática
    -   [x] Pytest — testes automatizados
    -   [x] Geração e validação dos artefatos no runner
    -   [x] Docker Build — construção da imagem
    -   [x] Validação em Pull Request e após merge na `dev`
    -   [x] Promoção do workflow para `main`
    -   [x] Job de validação de origem dos PRs (GitFlow)
-   [x] Preparar operações reutilizáveis para o Airflow (sem DAG)
-   [x] Teste de integração ponta a ponta das operações
-   [x] Pipeline de treinamento com Airflow (execução manual validada em 22/10/2026)
-   [ ] Monitoramento com Prometheus
-   [ ] Dashboards no Grafana
-   [ ] Conversão e validação ONNX
-   [ ] Benchmark de latência
-   [ ] Documentação e resultados finais


---
## Checkpoint operacional — Airflow 3.1.0 (22–23/10/2026)

> **Este checkpoint atualiza o estado histórico descrito nas seções anteriores.** A preparação de 21/10 era um retrato anterior à execução da DAG; não representa o estado atual.

**Confirmado por execução na interface Airflow em 22/10:** `banking77_training_pipeline` com tarefas `ingest`, `train` e `publish` em **success**, uma tentativa por tarefa, duração total aproximada de **30 segundos**. A imagem da interface é a evidência da orquestração; a verificação pós-execução dos arquivos e de `metrics.json` ainda precisa ser registrada. **Não interpretar os artefatos já existentes como prova de sua geração pela DAG** até verificar datas e conteúdo.

**Implementação:** `airflow/dags/banking77_training_pipeline.py`, `airflow/Dockerfile`, `compose.airflow.yaml`, `application/training_pipeline.py` e teste de integração `tests/application/test_training_pipeline_integration.py`. DAG manual (`schedule=None`), `catchup=False`, `max_active_runs=1`; identificador de execução sanitizado para separar datasets e métricas intermediários em `airflow/data/runs/`. Os artefatos publicados ficam em `artifacts/` para a API.

**Arquitetura local:** Airflow 3.1.0, `LocalExecutor`, PostgreSQL 16, serviços `postgres`, `airflow-init`, `airflow-api-server`, `airflow-scheduler`, `airflow-dag-processor`; UI em http://localhost:8080. A execução foi inicialmente bloqueada por `Connection refused` na Execution API e, depois, `Invalid auth token: Signature verification failed`. Foram adotados `AIRFLOW__CORE__EXECUTION_API_SERVER_URL=http://airflow-api-server:8080/execution/` e **a mesma** `AIRFLOW__API_AUTH__JWT_SECRET` nos serviços via variável `${AIRFLOW_JWT_SECRET}` em `.env` local ignorado pelo Git. **Nunca versionar a chave JWT nem o `.env`.**

### Procedimento de reprodução e diagnóstico

```bash
# Na raiz do projeto; exige Docker Compose e arquivo .env com AIRFLOW_JWT_SECRET.
# Gerar .env somente se ainda não existir (não sobrescrever segredos existentes):
test -e .env || python3 -c "import secrets; print('AIRFLOW_JWT_SECRET=' + secrets.token_hex(32))" > .env
# Garantir .env no .gitignore e verificar com: git check-ignore -v .env
docker compose -f compose.airflow.yaml config --quiet
docker compose -f compose.airflow.yaml up -d --build
docker compose -f compose.airflow.yaml ps
docker compose -f compose.airflow.yaml exec airflow-scheduler airflow dags list-import-errors
# Na UI, despausar e acionar manualmente banking77_training_pipeline.
# Conferir arquivos e métricas da execução:
ls -lh artifacts/baseline_pipeline.joblib artifacts/label_mapping.json
find airflow/data/runs -name metrics.json -print -exec cat {} \;
# Logs de diagnóstico:
docker compose -f compose.airflow.yaml logs --tail=150 airflow-scheduler airflow-api-server
# Testes e lint locais:
uv run ruff check .
uv run pytest
```

A senha administrativa do Airflow deve ser consultada nos logs/configuração local; não a registrar em documentação pública. Não executar `docker compose down -v` durante diagnósticos, pois remove o volume PostgreSQL. Para verificar runs sem depender da CLI ou de links com `+` mal codificado:

```bash
docker compose -f compose.airflow.yaml exec postgres psql -U airflow -d airflow -c "SELECT dag_id, run_id, state FROM dag_run WHERE dag_id = 'banking77_training_pipeline' ORDER BY id DESC LIMIT 10;"
```

**Qualidade:** após inclusão do teste de integração, foi relatada validação local com **36 testes aprovados**, Ruff aprovado e `git diff --check` sem problemas. Recomenda-se repetir esses comandos antes do commit. O aviso de depreciação Starlette/httpx não bloqueou os testes.

**Rubrica (situação técnica, sem presumir nota):** Airflow 15% demonstrado por execução; CI/CD 15% com workflows implementados, sujeito à verificação de evidências; benchmark + ONNX 20% parcial (baseline pronto, ONNX/benchmark pendentes); Prometheus/Grafana 20% pendente; arquitetura cloud 15% pendente; vídeo STAR 15% pendente. Restam validação pós-execução de artefatos/métricas, documentação final e evidências reproduzíveis.

**Fluxo de integração:** manter branch `feature/airflow-training-pipeline`; executar `uv run ruff check .`, `uv run pytest`, `git diff --check`, conferir `git status` e alterações; commit em PT-BR; abrir PR para `dev` e posteriormente `dev → main` conforme GitFlow. Sem coautoria automática em commits.


## 🧭 Execução Airflow e decisões arquiteturais — checkpoint 23/10/2026

### Evidência e alcance da entrega

Em **22/10/2026**, a interface do Airflow registrou uma execução manual bem-sucedida de `banking77_training_pipeline`: `ingest` (~12 s), `train` (~14 s) e `publish` (~1,9 s), cada tarefa em uma tentativa; **30 segundos de duração total**. Isso comprova a execução orquestrada naquele ambiente. A verificação independente das métricas e da data de atualização dos artefatos após a DAG ainda precisa ser registrada; não atribuir automaticamente à DAG arquivos que já existiam antes da execução.

### Decisões de arquitetura e justificativas

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

### Diagnóstico e segurança

```bash
docker compose -f compose.airflow.yaml logs --tail=150 airflow-scheduler airflow-api-server
docker compose -f compose.airflow.yaml exec airflow-scheduler \
  airflow config get-value core execution_api_server_url
```

Histórico de incidentes: primeiro `httpx.ConnectError: [Errno 111] Connection refused`; depois `Invalid auth token: Signature verification failed`. Em ambos os casos, a tarefa `ingest` falhou antes de executar o código do dataset, e os logs de tentativa estavam vazios. A mensagem `LocalExecutor ... state failed ... state queued` era consequência da falha de inicialização, não diagnóstico de erro do BANKING77. A correção foi validada pela execução posterior bem-sucedida. **Não usar `docker compose down -v`** para investigar: isso apagaria o volume de metadados do PostgreSQL.

### Rubrica e próximos passos

| Frente | Peso | Estado técnico em 23/10/2026 |
| :--- | ---: | :--- |
| Airflow | 15% | DAG executada com sucesso; faltam conferência final de artefatos/métricas e evidências consolidadas. |
| CI/CD | 15% | GitHub Actions com lint, testes, build e política GitFlow; verificar evidências do checkpoint atual. |
| Benchmark e ONNX | 20% | Baseline pronto; conversão e comparação ainda não executadas. |
| Prometheus e Grafana | 20% | Pendentes. |
| Arquitetura cloud | 15% | Documentação específica da solução cloud pendente. |
| Vídeo STAR | 15% | Pendente. |

Os percentuais são **pesos da rubrica**, não notas atribuídas. A última suíte local informada após o teste de integração foi de **36 testes aprovados**; executar novamente antes do commit. Continuar na branch `feature/airflow-training-pipeline` e promover por PR `feature/* → dev → main`, com mensagens de commit em português e sem coautoria automática.

**Notas relacionadas:** [índice de estudos](docs/study-notes/README.md), [nota de pipeline Airflow](docs/study-notes/airflow-training-pipeline.md) e [arquitetura](docs/architecture.md).
