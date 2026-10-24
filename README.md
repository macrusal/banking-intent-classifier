# Banking Intent Classifier

Projeto desenvolvido para o **Tech Challenge — Fase 3 da Pós-Tech FIAP
em Machine Learning Engineering**.

O projeto tem como objetivo desenvolver uma solução de Machine Learning
capaz de identificar automaticamente a intenção presente em mensagens de
clientes de serviços bancários, explorando técnicas de **Processamento
de Linguagem Natural (NLP)** e práticas relacionadas ao ciclo de vida de
modelos em produção.

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

## 🗂️ Estrutura do Projeto

Principais componentes do projeto.

```text
banking-intent-classifier/
├── airflow/
│   ├── Dockerfile                         # Imagem do orquestrador
│   └── dags/
│       └── banking77_training_pipeline.py # DAG ingest → train → publish
├── compose.airflow.yaml                  # Serviços do Airflow e PostgreSQL
├── docs/
│   ├── architecture.md                   # Arquitetura e responsabilidades
│   ├── entrega.md                        # Rubrica e checkpoints
│   ├── operacao-airflow.md               # Operação e diagnóstico
│   └── study-notes/                     # Histórico técnico detalhado
├── src/banking_intent_classifier/
│   ├── application/
│   │   ├── prediction_service.py         # Inferência
│   │   ├── training_pipeline.py          # Operações reutilizáveis da DAG
│   │   └── training_service.py           # Treinamento e avaliação
│   ├── domain/                           # Tipos e resultados do domínio
│   ├── infrastructure/
│   │   ├── model_repository.py           # Persistência do modelo
│   │   ├── label_repository.py           # Mapeamento das classes
│   │   └── data/
│   │       ├── banking77_loader.py       # Fonte Hugging Face
│   │       └── dataset_repository.py     # Persistência do dataset
│   ├── presentation/
│   │   └── api.py                        # API FastAPI
│   ├── baseline.py                       # Baseline reproduzível
│   ├── experiment.py                     # Experimentos textuais
│   ├── final_training.py                 # CLI do treinamento final
│   └── main.py                           # CLI de EDA
├── .github/
│   └── workflows/
│       └── ci.yml                        # Lint, testes, build e política GitFlow
├── tests/                                # Testes automatizados
├── Dockerfile                            # Imagem da API de inferência
├── pyproject.toml                        # Dependências e ferramentas
└── uv.lock                               # Resolução de dependências
```

## 📚 Documentação

| Documento | Conteúdo | Quando consultar |
| :--- | :--- | :--- |
| [`docs/architecture.md`](docs/architecture.md) | Camadas, responsabilidades e decisões | Entender a organização do código |
| [`docs/study-notes/README.md`](docs/study-notes/README.md) | Índice das notas de decisões técnicas | Investigar por que cada escolha foi feita |
| [`docs/operacao-airflow.md`](docs/operacao-airflow.md) | Arquitetura local, incidentes e diagnóstico | Subir ou depurar o Airflow |
| [`docs/entrega.md`](docs/entrega.md) | Rubrica, checkpoints e pendências | Acompanhar a entrega acadêmica |

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

## 🧰 Catálogo de comandos

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

## 🔁 Reprodutibilidade

Uma afirmação quantitativa apresentada neste README deve estar
associada, sempre que aplicável, a um comando versionado capaz de
reproduzi-la.

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

A suíte completa passa sem falhas, com um aviso de depreciação do Starlette/httpx relacionado ao uso de `httpx` com `starlette.testclient`.

A contagem de testes não é fixada neste README porque evolui a cada feature; o comando acima é a fonte da informação. O tempo total pode variar entre máquinas.

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
e da orquestração do comando `baseline`, além dos testes já existentes:

```bash
uv run pytest
```

---

## 🧪 Treinamento final e artefatos

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

## 🌐 API FastAPI

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

## 🐳 Docker

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

## 🌬️ Pipeline Apache Airflow

O pipeline `banking77_training_pipeline` usa Airflow 3.1.0 com execução manual e três tarefas: `ingest` (carregamento e validação), `train` (treinamento e avaliação) e `publish` (publicação do modelo e mapeamento para a API). O ambiente local usa PostgreSQL 16 e `LocalExecutor`.

```bash
docker compose -f compose.airflow.yaml config --quiet
docker compose -f compose.airflow.yaml up -d --build
docker compose -f compose.airflow.yaml ps
```

Acesse `http://localhost:8080` e acione a DAG manualmente. Antes, configure o segredo JWT local conforme [guia operacional](docs/operacao-airflow.md). O run de 22/10/2026 foi concluído e suas métricas e hashes foram conferidos em 23/10/2026. A publicação atual é por cópia, não atômica.

**Detalhes de incidentes, diagnóstico, reprodução, verificação de hashes e segurança:** [`docs/operacao-airflow.md`](docs/operacao-airflow.md).

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

A suíte completa também foi executada localmente, sem falhas, com um aviso
de depreciação do Starlette/httpx.

Para consultar as execuções e os logs dos jobs, acesse a
[aba Actions do repositório](https://github.com/macrusal/banking-intent-classifier/actions).
Os registros de execução no GitHub são a evidência verificável; os tempos
acima são apenas observações e podem variar entre execuções.

O job `validate-gitflow` foi adicionado posteriormente; seu histórico e
resultado devem ser consultados na aba Actions.

A documentação das demais frentes será incorporada conforme suas validações
forem concluídas; o acompanhamento da entrega está em
[`docs/entrega.md`](docs/entrega.md).

---

## 📐 Arquitetura e padrões

O projeto separa responsabilidades em `domain`, `application`, `infrastructure` e `presentation`, mantendo a lógica de treinamento reutilizável fora da DAG e da CLI. Consulte [`docs/architecture.md`](docs/architecture.md) e a [estrutura do projeto](#-estrutura-do-projeto).

## 📊 Métricas principais

No run Airflow de 22/10/2026, inspecionado em 23/10/2026, as métricas em `training/metrics.json` foram:

| Métrica | Valor |
| :--- | ---: |
| Accuracy | 0.8769480519480519 |
| Macro F1 | 0.8768846181655345 |
| Weighted F1 | 0.8768846181655345 |

Para reproduzir, execute o pipeline ou a CLI documentada em [Reprodutibilidade](#-reprodutibilidade), e consulte o arquivo `metrics.json` do `run_id` correspondente. Os hashes históricos e o procedimento de comparação estão em [`docs/operacao-airflow.md`](docs/operacao-airflow.md).

## 🧪 Testes automatizados

```bash
uv run pytest tests/application/test_prediction_service.py -v
uv run pytest tests/presentation/test_api.py -v
uv run pytest tests/test_final_training.py tests/test_model_repository.py tests/test_label_repository.py -v
uv run pytest
```

A suíte completa roda com `uv run pytest` e passa sem falhas. Há um aviso `StarletteDeprecationWarning`, relacionado ao uso de `httpx` com `starlette.testclient`, que não impede a execução e será revisado na etapa de atualização de dependências.

A contagem de testes não é fixada neste README, pois evolui a cada feature.

## 👥 Equipe

| Nome | RM | E-mail | Áreas de atuação                                            |
| :--- | :---: | :--- |:------------------------------------------------------------|
| **Marcelo da Cruz Salvador** | **RM375166** | [macrusal@gmail.com](mailto:macrusal@gmail.com) | Software/Backend Engineering · Data · Machine Learning · MLOps |

## 🗺️ Etapas do Projeto

O acompanhamento da rubrica e os checkpoints datados ficam em [`docs/entrega.md`](docs/entrega.md). O Airflow está implementado; os próximos blocos são ONNX/benchmark, observabilidade e arquitetura Cloud.

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
77 classes e disponibilizado por uma API FastAPI, containerizada e validada
por uma esteira de CI. O treinamento foi orquestrado em uma DAG do Apache
Airflow, com execução manual concluída em 22/10/2026.

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
    ├── Testes automatizados                   ✅
    ├── CI/CD (Ruff + Pytest + Docker Build)   ✅
    │     └── Validação de origem GitFlow      ✅
    └── Airflow (ingest → train → publish)     ✅
```

A containerização da API foi validada com uma inferência real no Docker.
O pipeline de CI/CD foi validado em Pull Request e após merge na `dev`,
e posteriormente promovido para `main`. A validação GitFlow foi
incorporada ao workflow; a obrigatoriedade do check depende do Ruleset.
O treinamento foi orquestrado em uma DAG do Airflow, com execução manual
validada em 22/10/2026.

As próximas etapas planejadas são o monitoramento com Prometheus e Grafana,
a conversão para ONNX com benchmark de latência e a documentação da
arquitetura em nuvem.

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

