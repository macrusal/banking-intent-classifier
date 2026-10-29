# Arquitetura do Projeto

## 1. Objetivo

Este documento descreve a arquitetura inicial do projeto **Banking Intent Classifier**, desenvolvido para o Tech Challenge da Fase 3 da Pós-Tech FIAP em Machine Learning Engineering.

O projeto tem como objetivo construir uma solução de classificação de intenções bancárias utilizando Processamento de Linguagem Natural (NLP), contemplando também aspectos relacionados ao ciclo de vida do modelo em produção.

A arquitetura será evoluída de forma incremental ao longo do desenvolvimento do projeto.

---

## 2. Contexto

O problema de negócio consiste em classificar automaticamente mensagens enviadas por clientes de serviços bancários.

Cada mensagem deve ser associada a uma intenção específica, permitindo seu posterior direcionamento para um fluxo de atendimento adequado.

Exemplo:

```text
Mensagem do cliente
        │
        │ "I haven't received my card yet"
        │
        ▼
Classificador NLP
        │
        ▼
   card_arrival
```

O projeto utilizará o dataset **BANKING77**, composto por textos de solicitações bancárias classificadas em diferentes categorias de intenção.

---

## 3. Visão Geral da Arquitetura

A arquitetura inicial será organizada em componentes independentes responsáveis pelas principais etapas da solução.

```text
                    ┌──────────────────────┐
                    │      BANKING77       │
                    │    Dataset Público   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Processamento dos   │
                    │        Dados         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Treinamento do Modelo│
                    │       de NLP         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Modelo Treinado    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       FastAPI        │
                    │ API de Inferência    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │        Docker        │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴───────────┐
                    │                      │
                    ▼                      ▼
              Consumidor da API        Prometheus
                                           │
                                           ▼
                                        Grafana
```

Essa visão representa o estado arquitetural planejado para o projeto e poderá ser refinada conforme as decisões técnicas forem validadas.

---

## 4. Camada de Dados

A entrada inicial da solução será o dataset público **BANKING77**.

O conjunto de dados apresenta uma estrutura compatível com um problema de classificação supervisionada:

```text
text → label
```

Onde:

* `text` representa a mensagem enviada pelo cliente;
* `label` representa a intenção bancária associada à mensagem.

Exemplo:

```text
"I am still waiting on my card?" → card_arrival
```

A etapa de dados contempla atualmente:

* carregamento do dataset;
* validação da estrutura;
* identificação de valores ausentes;
* identificação de registros duplicados;
* verificação de sobreposição de textos entre treino e teste;
* análise da distribuição das classes;
* análise do comprimento dos textos em caracteres e palavras.

As etapas de carregamento, validação estrutural, distribuição das classes e análise inicial do comprimento dos textos já foram implementadas.

A análise exploratória continuará de forma incremental antes da preparação dos dados para treinamento.

---

## 5. Estratégia Inicial de Modelagem

O modelo baseline previsto utilizará uma abordagem clássica de NLP.

Fluxo inicial:

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

### TF-IDF

O `TF-IDF` será utilizado inicialmente para converter os textos em representações numéricas adequadas ao treinamento do modelo.

### Logistic Regression

A `Logistic Regression` será utilizada inicialmente como classificador multiclasse.

A escolha dessa abordagem ocorre por apresentar:

* implementação simples;
* baixo custo computacional;
* boa adequação para classificação de textos;
* capacidade de atuar como baseline;
* possibilidade de retornar probabilidades das classes;
* potencial compatibilidade com estratégias posteriores de otimização.

Outros algoritmos poderão ser avaliados durante a fase de experimentação.

---

## 6. Serviço de Inferência

Após o treinamento, o modelo será disponibilizado através de uma API REST utilizando **FastAPI**.

A API terá como principal responsabilidade:

```text
Receber texto
     │
     ▼
Executar inferência
     │
     ▼
Retornar intenção
```

Exemplo conceitual:

```json
{
  "text": "I haven't received my card yet"
}
```

Resposta esperada:

```json
{
  "intent": "card_arrival"
}
```

Posteriormente, a resposta poderá incluir informações adicionais, como:

* confiança da classificação;
* versão do modelo;
* runtime utilizado;
* tempo de inferência.

---

## 7. Containerização

A API será empacotada em um container Docker.

O objetivo é garantir que a aplicação possa ser executada de forma reproduzível, independente do ambiente local utilizado durante o desenvolvimento.

A visão inicial é:

```text
FastAPI
   │
   ▼
Modelo NLP
   │
   ▼
Imagem Docker
   │
   ▼
Container
```

A configuração do Docker será adicionada quando a API de inferência estiver implementada.

---

## 8. Pipeline de Treinamento

O treinamento do modelo será posteriormente automatizado utilizando **Apache Airflow**.

A DAG prevista inicialmente deverá representar o seguinte fluxo:

```text
Carregar Dataset
       │
       ▼
Validar Dados
       │
       ▼
Treinar Modelo
       │
       ▼
Avaliar Modelo
       │
       ▼
Salvar Modelo
```

Em uma etapa posterior, o fluxo poderá evoluir para incluir:

```text
Salvar Modelo
       │
       ▼
Exportar ONNX
       │
       ▼
Validar Modelo Otimizado
```

A DAG será implementada somente após o pipeline de treinamento local estar funcional.

---

## 9. Integração Contínua

O projeto utilizará **GitHub Actions** para automatizar verificações durante o desenvolvimento.

A estratégia inicial prevista é:

```text
Push / Pull Request
        │
        ▼
      Lint
        │
        ▼
      Testes
        │
        ▼
      Build
```

A configuração de CI será adicionada à medida que os testes e a aplicação começarem a ser implementados.

---

## 10. Monitoramento

A API será instrumentada utilizando **Prometheus**.

Inicialmente serão consideradas métricas relacionadas a:

* quantidade de requisições;
* tempo de resposta;
* quantidade de erros;
* quantidade de classificações realizadas.

O Prometheus será responsável pela coleta dessas métricas.

O Grafana será utilizado para visualização.

Fluxo previsto:

```text
FastAPI
   │
   │ /metrics
   ▼
Prometheus
   │
   ▼
Grafana
```

A arquitetura inicial prevê pelo menos três tipos de visualização:

* quantidade de requisições;
* latência da API;
* taxa de erros.

Outros painéis poderão ser adicionados posteriormente.

---

## 11. Estratégia de Otimização

O projeto deverá comparar o comportamento do modelo original com uma versão otimizada para inferência.

A estratégia inicial será avaliar a conversão para **ONNX**.

Fluxo previsto:

```text
Modelo Scikit-Learn
        │
        ▼
      ONNX
        │
        ▼
  ONNX Runtime
```

O objetivo será comparar métricas como:

* latência média;
* P50;
* P95;
* P99;
* throughput;
* tamanho do artefato.

A decisão final sobre a implementação será tomada após a validação do modelo baseline.

---

## 12. Arquitetura de Execução Local

Quando todos os componentes principais estiverem implementados, a arquitetura local deverá evoluir para:

```text
                         ┌──────────────────┐
                         │     Cliente      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │       API        │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    Modelo NLP    │
                         └──────────────────┘
                                  │
                                  │ métricas
                                  ▼
                         ┌──────────────────┐
                         │    Prometheus    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     Grafana      │
                         └──────────────────┘
```

Esses serviços deverão posteriormente ser executados de forma integrada utilizando Docker Compose.

---

## 13. Arquitetura em Nuvem (proposta)

### 13.1 Status

> **Arquitetura proposta, não implantada.** Nenhum recurso foi criado no GCP, nenhum
> custo foi levantado e nenhuma medição foi feita em ambiente de nuvem. Todos os números
> desta seção vêm das medições locais documentadas no repositório, com a fonte indicada.
> O que foi implementado e validado roda localmente com Docker Compose (§12).

### 13.2 Provedor: Google Cloud Platform

O provedor é o **GCP**. A escolha decorre das restrições concretas deste projeto:

| Restrição do projeto | Como o GCP atende |
| :--- | :--- |
| API stateless em **um único contêiner**, já empacotada pelo `Dockerfile` | **Cloud Run** executa o contêiner como serviço gerenciado, sem cluster para administrar e sem alterar a imagem |
| Métricas no formato Prometheus, consultas PromQL versionadas em `monitoring/grafana/dashboards/api.json` | **Google Cloud Managed Service for Prometheus** recebe métricas no formato Prometheus e responde PromQL; as consultas dos painéis continuam válidas |
| CI no GitHub Actions publicando a imagem | **Artifact Registry** armazena a mesma imagem; **Workload Identity Federation** autentica o GitHub Actions sem chave de service account estática |
| Segredo local em `.env` (`AIRFLOW_JWT_SECRET`) | **Secret Manager** substitui o `.env` |
| Artefatos do modelo pequenos e versionados por execução | **Cloud Storage** com versionamento de objetos |

**Onde a plataforma é menos direta: o Grafana.** O GCP não oferece Grafana gerenciado de
primeira classe, como a AWS oferece com o Amazon Managed Grafana. A proposta resolve isso
assim:

- **Grafana OSS em um serviço Cloud Run próprio**, com a mesma imagem fixada no local
  (`grafana/grafana:13.0.1`) e o mesmo provisionamento em arquivo (datasource com `uid`
  fixo e dashboard `api.json`). Como no local, o estado do Grafana é descartável
  (`allowUiUpdates: false`): tudo o que importa está versionado, então não há banco do
  Grafana para operar.
- **O datasource aponta para a API de consulta PromQL do Managed Service for Prometheus.**
  Essa API exige um token OAuth de curta duração. O Google fornece um *datasource syncer*,
  executado periodicamente, que renova o token no datasource do Grafana.
- **Custo dessa escolha:** um serviço a mais para operar, a atualização da imagem do
  Grafana sob responsabilidade do projeto e a dependência do syncer. Se o token expirar
  sem renovação, os painéis param de exibir dados, mas a coleta continua. A alternativa
  nativa, os dashboards do Cloud Monitoring com PromQL, abriria mão do dashboard
  versionado já validado, e por isso não foi adotada.

### 13.3 Mapeamento componente a componente

| Componente | Local (implementado) | GCP (proposto) |
| :--- | :--- | :--- |
| API FastAPI | Contêiner do `Dockerfile` no Docker Compose, porta 8000 | **Cloud Run**, região `southamerica-east1` (São Paulo), a mesma imagem |
| Registry de imagens | Imagem construída localmente; o CI apenas a constrói (`docker-build`) | **Artifact Registry** (repositório Docker na mesma região) |
| Apache Airflow | `compose.airflow.yaml`: Airflow 3.1.0, `LocalExecutor`, PostgreSQL 16 | **Uma VM do Compute Engine** com o mesmo `compose.airflow.yaml`, PostgreSQL em disco persistente, ligada sob demanda para a execução manual da DAG |
| Artefatos do modelo | `artifacts/` no host, copiados pelo `publish` e embutidos na imagem no build | **Bucket do Cloud Storage** com versionamento de objetos; o `publish` grava no bucket, e o build da imagem lê do bucket |
| Coleta de métricas | Prometheus raspa `api:8000/metrics` a cada 5 s | **Sidecar coletor do Managed Service for Prometheus** na própria instância do Cloud Run, raspando `localhost:8000/metrics` |
| Destino das métricas | Série temporal no contêiner do Prometheus, sem volume persistente | **Managed Service for Prometheus** (armazenamento do Cloud Monitoring) |
| Visualização | Grafana no Compose, porta 3000, leitura anônima | **Grafana OSS no Cloud Run**, atrás do IAP, sem acesso anônimo |

Pontos do mapeamento:

- **Por que o scrape muda.** No Compose, o Prometheus alcança a API pelo nome do serviço.
  No Cloud Run, as instâncias não têm endereço individual alcançável de fora, e um
  Prometheus externo só enxergaria o balanceador. Com o sidecar, cada instância exporta as
  próprias métricas. Isso também combina com a decisão de usar o registry padrão do
  `prometheus_client` em processo único (`prometheus-instrumentation.md`, "Decisões de
  desenho"): cada instância tem um processo, e o Managed Prometheus agrega as séries.
- **Por que uma VM e não o Cloud Composer.** O Cloud Composer é o Airflow gerenciado do GCP,
  mas provisiona um cluster GKE por baixo. Para uma DAG de três tarefas
  (`ingest → train → publish`) acionada manualmente, isso é sobredimensionado e esbarra na
  restrição de não usar cluster gerenciado. A VM reaproveita a estrutura de serviços do
  `compose.airflow.yaml` validado em 22/10/2026. Mudam só a origem do segredo (Secret
  Manager em vez de `.env`) e o destino dos artefatos (bucket em vez do volume
  `./artifacts`).
- **Por que os artefatos continuam embutidos na imagem.** O modelo validado localmente é o
  da imagem. Manter o artefato dentro dela faz cada imagem corresponder a uma única versão
  do modelo e mantém a API sem acesso ao bucket em tempo de execução. O que muda é a
  origem: o build lê do bucket em vez de `./artifacts`.

### 13.4 Tempo real versus batch

A inferência é **em tempo real, síncrona, por requisição**. Uma mensagem precisa ser
classificada no momento em que chega, porque o encaminhamento ao fluxo de atendimento
depende da intenção. As medições locais mostram que a inferência não é o gargalo que
justificaria acumular mensagens em lote:

| Medição | Valor | Fonte |
| :--- | :--- | :--- |
| Latência p50 de `POST /predict`, vista pelo cliente | 2,47–2,48 ms | [`http-latency-baseline.md`](http-latency-baseline.md), "Estado confirmado em 26/10/2026" |
| Média de latência do lado servidor (`_sum / _count`) | 1,80–1,92 ms | [`prometheus-instrumentation.md`](prometheus-instrumentation.md), "Calibração dos buckets" |
| Latência p95 exibida no Grafana sob a stack completa | 2,91 ms | [`operacao-monitoramento.md`](operacao-monitoramento.md), "Estado confirmado em 26/10/2026" |
| Throughput em lote × individual, modelo isolado | Mesma ordem de grandeza | [`onnx-benchmark.md`](onnx-benchmark.md), "Estado confirmado em 24/10/2026" |

O raciocínio:

- **Uma classificação custa poucos milissegundos.** Um processamento em lote só se paga
  quando o custo por item cai muito ao agrupar. Aqui, o ganho medido de agrupar ficou na
  mesma ordem de grandeza, e o lote acrescentaria a espera da fila, de segundos a minutos,
  a uma operação que leva milissegundos.
- **Batch não tem consumidor neste cenário.** Não há relatório nem reprocessamento
  periódico que use as intenções em massa. O consumidor é o roteamento, que é síncrono.
- **Limitação das medições.** Os números foram medidos no Docker Desktop no macOS Intel,
  com 1 cliente sequencial. A própria baseline registra que eles **não se transferem
  automaticamente para a nuvem** (`http-latency-baseline.md`, "Interpretação e
  limitações"). Eles justificam a ordem de grandeza da decisão, não um SLA no GCP. A
  latência em nuvem teria de ser medida após um deploy, que não foi feito.
- **Consequência para o Cloud Run.** Como a inferência dura milissegundos, uma subida de
  instância a frio dominaria a latência da primeira requisição. Por isso a proposta mantém
  `min-instances=1`. O tempo de cold start desta imagem não foi medido.

### 13.5 Dimensionamento

A proposta é dimensionada para a carga deste projeto, uma API stateless com modelo
TF-IDF + Logistic Regression de 1.479.476 bytes (`onnx-benchmark.md`):

| Serviço | Configuração proposta | Justificativa |
| :--- | :--- | :--- |
| API (Cloud Run) | 1 vCPU, 1 processo `uvicorn`, `min-instances=1`, `max-instances` baixo (poucas instâncias) | Um processo por contêiner, como no local, o que mantém válido o registry Prometheus de processo único. O teto baixo limita custo e impacto de erro. A memória deve ser definida medindo o contêiner, o que não foi feito neste projeto |
| Grafana (Cloud Run) | Uma instância, sem réplica | Uso de leitura ocasional, estado descartável |
| Airflow (Compute Engine) | Uma VM, ligada só para as execuções | Uma DAG manual com `LocalExecutor`; não há fila nem execução contínua |
| Cloud Storage / Artifact Registry | Um bucket, um repositório | Poucos artefatos e imagens, de tamanho na casa dos megabytes |

**Não são propostos Kubernetes, GKE nem qualquer cluster gerenciado.** Com uma API de um
contêiner, um cluster acrescentaria operação sem atender a nenhuma necessidade medida.

**O que não se sabe sobre capacidade.** O throughput de 387,2–391,4 req/s da baseline foi
medido com 1 cliente sequencial e é o inverso da latência, não a capacidade da API
(`http-latency-baseline.md`, "O que elas não sustentam"). O escalonamento sob concorrência
não foi medido, e o `max-instances` deve ser ajustado por um teste de carga concorrente
feito no próprio Cloud Run.

### 13.6 Segurança

**Segredos.**

- `AIRFLOW_JWT_SECRET` e a senha de administrador do Grafana ficam no **Secret Manager**.
  Na nuvem não existe `.env`.
- A VM do Airflow lê o segredo pela própria identidade. No Cloud Run, o Grafana recebe a
  senha como segredo montado.
- A credencial padrão `admin`/`admin` do Grafana local não é usada.

**Identidade.** Uma service account por serviço, com privilégio mínimo:

| Identidade | Permissões |
| :--- | :--- |
| API (Cloud Run) | `roles/monitoring.metricWriter`, só para o sidecar exportar métricas. Sem acesso ao bucket, porque o modelo está na imagem |
| Grafana (Cloud Run) | `roles/monitoring.viewer`, leitura de métricas, e acesso ao seu segredo |
| Airflow (VM) | Escrita apenas no bucket de artefatos e acesso ao seu segredo |
| GitHub Actions (via Workload Identity Federation) | Escrita no Artifact Registry e deploy no Cloud Run, restritas ao repositório e à branch `main` |

Nenhuma chave JSON de service account é gerada nem armazenada no GitHub.

**Rede.**

- **API:** sem invocação anônima, só identidades com `roles/run.invoker`, e ingress
  restrito ao tráfego interno do projeto. Isso também protege `/metrics`, que fica na mesma
  porta do `/predict`: o sidecar coleta por `localhost`, dentro da instância, e não depende
  de exposição externa.
- **Grafana:** atrás do Identity-Aware Proxy (IAP), com o acesso anônimo de leitura do
  setup local desligado (`operacao-monitoramento.md`, "Segurança").
- **VM do Airflow:** sem IP público. A interface é acessada por túnel IAP, e a saída para
  o Hugging Face Hub, necessária ao `ingest`, passa pelo Cloud NAT.

### 13.7 O que muda e o que permanece em relação ao setup local

| Permanece | Muda |
| :--- | :--- |
| `Dockerfile` e imagem da API | Origem dos artefatos no build: bucket em vez de `./artifacts` |
| Camadas de domínio, aplicação e apresentação, sem alteração | Infraestrutura: um destino de publicação no Cloud Storage para o `publish`, em vez da cópia para `artifacts/` |
| Instrumentação da API (middleware e `/metrics`), sem alteração | Coleta: sidecar raspando `localhost:8000` em vez de Prometheus raspando `api:8000` |
| Métricas `http_requests_total` e `http_request_duration_seconds`, com os mesmos buckets | Armazenamento das métricas: Managed Service for Prometheus em vez do contêiner do Prometheus |
| Dashboard `api.json` e consultas PromQL dos três painéis | Grafana: acesso anônimo desligado, autenticação via IAP e token do datasource renovado pelo syncer |
| DAG `ingest → train → publish` e estrutura de serviços do `compose.airflow.yaml` (`LocalExecutor`, PostgreSQL) | `compose.airflow.yaml`: segredo lido do Secret Manager em vez do `.env`, e o volume `./artifacts` deixa de ser o destino; o `publish` grava no bucket versionado em vez de fazer a cópia não atômica para `artifacts/` |
| CI com `lint`, `tests`, `docker-build` e `validate-gitflow` | Segredos: Secret Manager em vez de `.env`. Entrada de rede: ingress restrito e IAP em vez de `localhost` |

### 13.8 Fora desta proposta

Não fazem parte desta entrega e não foram feitos: o job de CD que publicaria a imagem e
faria o deploy, a infraestrutura como código, o levantamento de custos, o teste de carga
concorrente e qualquer medição em ambiente de nuvem.

---

## 14. Organização Atual do Código

A organização do código evoluiu juntamente com a implementação das primeiras etapas do projeto.

A estrutura atual é:

```text
banking-intent-classifier/
│
├── README.md
├── docs/
│   └── architecture.md
├── pyproject.toml
├── uv.lock
│
└── src/
    └── banking_intent_classifier/
        ├── __init__.py
        ├── application/
        │   ├── __init__.py
        │   └── dataset_service.py
        ├── domain/
        │   ├── __init__.py
        │   └── dataset_summary.py
        ├── infrastructure/
        │   ├── __init__.py
        │   └── data/
        │       ├── __init__.py
        │       └── banking77_loader.py
        ├── presentation/
        │   ├── __init__.py
        │   └── console_reporter.py
        └── main.py
```

Diretórios gerados automaticamente, como `__pycache__`, não fazem parte da arquitetura do projeto e não são representados acima.

### 14.1 Domain

O pacote `domain` contém os objetos que representam os resultados das análises realizadas sobre o dataset.

Atualmente, `dataset_summary.py` concentra estruturas como:

* resumo dos splits;
* resumo geral do dataset;
* estatísticas da distribuição das classes;
* estatísticas do comprimento dos textos.

Esses objetos representam dados do domínio da análise e não possuem responsabilidade de carregamento ou apresentação.

### 14.2 Application

O pacote `application` contém os serviços responsáveis por executar as análises.

O `DatasetService` concentra atualmente operações como:

* geração do resumo estrutural do dataset;
* análise dos splits;
* identificação de textos compartilhados entre treino e teste;
* cálculo da distribuição das classes;
* cálculo das estatísticas da distribuição;
* cálculo das estatísticas de comprimento dos textos.

A camada de aplicação trabalha sobre os dados recebidos sem conhecer como eles serão apresentados ao usuário.

### 14.3 Infrastructure

O pacote `infrastructure` concentra integrações com recursos externos.

Atualmente, `infrastructure/data/banking77_loader.py` é responsável pelo carregamento do BANKING77 através do Hugging Face.

Essa separação evita que detalhes relacionados à origem do dataset sejam incorporados às regras de análise.

### 14.4 Presentation

O pacote `presentation` foi introduzido durante a evolução da EDA para separar a apresentação dos resultados da lógica de análise.

O `ConsoleReporter` é responsável por:

* apresentar o resumo estrutural do dataset;
* apresentar informações dos splits;
* apresentar a distribuição das classes;
* apresentar o resumo estatístico da distribuição;
* apresentar as estatísticas de comprimento dos textos.

Com isso, chamadas de `print()` e detalhes de formatação deixam de ficar concentrados no ponto de entrada da aplicação.

### 14.5 Main

O `main.py` permanece como ponto de entrada da aplicação e tem como principal responsabilidade orquestrar o fluxo de execução.

O fluxo atual pode ser representado como:

```text
main.py
   │
   ├── carrega BANKING77
   │       │
   │       ▼
   │  infrastructure
   │
   ├── executa análises
   │       │
   │       ▼
   │   application
   │       │
   │       ▼
   │     domain
   │
   └── apresenta resultados
           │
           ▼
      presentation
```

O `main.py` não deve concentrar regras de análise nem detalhes de formatação dos resultados.

### 14.6 Princípios de design

A evolução da estrutura busca aplicar princípios de design de forma incremental, especialmente o **Single Responsibility Principle (SRP)**.

A divisão atual estabelece responsabilidades distintas:

| Componente | Responsabilidade |
| --- | --- |
| `domain` | representar os resultados das análises |
| `application` | executar as análises e regras da aplicação |
| `infrastructure` | integrar e carregar fontes externas de dados |
| `presentation` | formatar e apresentar os resultados |
| `main.py` | orquestrar o fluxo da aplicação |

A arquitetura continuará simples enquanto o projeto estiver nas etapas iniciais. Novas abstrações, interfaces ou componentes serão introduzidos somente quando houver necessidade concreta.

Essa decisão evita complexidade prematura e permite que a arquitetura evolua juntamente com os requisitos do Tech Challenge.

### 14.7 Evolução prevista da estrutura

Novos diretórios poderão ser adicionados conforme os respectivos componentes forem efetivamente implementados.

Exemplos previstos:

```text
tests/
models/
airflow/
monitoring/
benchmarks/
.github/workflows/
```

A futura API de inferência também deverá reutilizar as regras existentes sem depender da apresentação em console. A separação atual permite que outros mecanismos de entrada e saída sejam adicionados posteriormente sem transferir essas responsabilidades para o `DatasetService`.

---

## 15. Evolução da Arquitetura

Esta arquitetura representa uma **visão inicial**.

As decisões documentadas neste arquivo poderão ser revisadas ao longo do projeto com base em:

* resultados da análise exploratória;
* métricas obtidas pelo modelo baseline;
* dificuldades de integração;
* compatibilidade com ONNX;
* resultados dos testes de latência;
* requisitos identificados durante o desenvolvimento.

Alterações significativas deverão ser documentadas no próprio repositório, preservando o histórico das decisões técnicas.

---

## 16. Próximos Passos

As primeiras etapas de estruturação, carregamento e validação do BANKING77 já foram concluídas.

A análise exploratória encontra-se em andamento e já contempla:

1. validação estrutural do dataset;
2. verificação de valores ausentes, textos vazios e duplicatas;
3. verificação de sobreposição entre treino e teste;
4. distribuição das 77 classes;
5. estatísticas de balanceamento;
6. análise inicial do comprimento dos textos em caracteres e palavras.

Os próximos incrementos previstos são:

1. continuar a análise exploratória do corpus;
2. investigar a distribuição dos comprimentos e possíveis valores extremos;
3. analisar características relevantes do vocabulário;
4. consolidar as decisões iniciais de pré-processamento;
5. implementar o baseline com TF-IDF e Logistic Regression;
6. avaliar o desempenho inicial do modelo.

A infraestrutura de API, Docker, CI/CD, Airflow, monitoramento e ONNX será adicionada progressivamente após a validação do pipeline de Machine Learning.
