# Arquitetura Inicial

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

A etapa de dados deverá contemplar inicialmente:

* carregamento do dataset;
* validação da estrutura;
* identificação de valores ausentes;
* identificação de registros duplicados;
* análise da distribuição das classes;
* análise do tamanho dos textos;
* preparação dos dados para treinamento.

Essas atividades serão implementadas posteriormente durante a etapa de análise exploratória.

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

## 13. Estratégia de Deploy

O cenário do projeto é mais adequado para inferência em tempo real.

Uma solicitação recebida deve ser classificada imediatamente para permitir seu encaminhamento para o fluxo correspondente.

Portanto, a estratégia arquitetural inicial considera:

```text
Real-time inference
```

como abordagem principal.

A primeira versão do projeto será executada localmente.

Uma arquitetura de deploy em nuvem será detalhada posteriormente no projeto, após a implementação e validação dos componentes principais.

---

## 14. Organização Inicial do Código

A estrutura inicial do projeto será mantida simples:

```text
banking-intent-classifier/
│
├── README.md
├── .gitignore
├── LICENSE
├── pyproject.toml
│
├── docs/
│   └── architecture.md
│
└── src/
    └── banking_intent_classifier/
        └── __init__.py
```

Novos diretórios serão adicionados somente quando os respectivos componentes forem implementados.

Exemplos futuros:

```text
notebooks/
tests/
data/
models/
airflow/
monitoring/
benchmarks/
.github/workflows/
```

Essa abordagem permite que a estrutura do repositório evolua juntamente com o desenvolvimento do projeto.

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

Após a criação desta documentação, os próximos incrementos previstos são:

1. criar o pacote Python inicial;
2. implementar o carregamento do BANKING77;
3. validar a estrutura do dataset;
4. realizar a análise exploratória;
5. implementar o baseline com TF-IDF e Logistic Regression;
6. avaliar o desempenho inicial do modelo.

A infraestrutura de API, Docker, CI/CD, Airflow, monitoramento e ONNX será adicionada progressivamente após a validação do pipeline de Machine Learning.
