# Banking Intent Classifier

Tech Challenge — Fase 3
Pós-Tech FIAP — Machine Learning Engineering

## 📌 Visão Geral

Este projeto está sendo desenvolvido como parte do **Tech Challenge da Fase 3** da Pós-Tech em Machine Learning Engineering da FIAP.

O objetivo é construir uma solução de **classificação de textos utilizando Processamento de Linguagem Natural (NLP)**, contemplando não apenas o treinamento do modelo, mas também aspectos relacionados ao seu ciclo de vida em produção, como:

* disponibilização do modelo através de uma API REST;
* containerização da aplicação;
* automação de testes e integração contínua;
* orquestração do pipeline de treinamento;
* monitoramento da aplicação e do modelo;
* análise e otimização da latência de inferência.

O projeto utilizará o dataset público **BANKING77**, que contém mensagens de clientes relacionadas a diferentes serviços bancários.

---

## 🎯 Problema de Negócio

Instituições financeiras recebem diariamente um grande volume de solicitações de clientes relacionadas a cartões, transferências, pagamentos, saques, contas e outros serviços bancários.

A classificação manual dessas solicitações pode aumentar o tempo necessário para direcionar cada atendimento ao fluxo ou área responsável.

Este projeto propõe a construção de um classificador de intenções capaz de receber uma mensagem escrita por um cliente e identificar automaticamente o assunto relacionado à solicitação.

Exemplo:

```text
Mensagem do cliente
        │
        │  "I haven't received my card yet"
        │
        ▼
Classificador NLP
        │
        ▼
   card_arrival
```

A classificação poderá ser utilizada como base para o encaminhamento automático da solicitação ao fluxo de atendimento correspondente.

---

## 📊 Dataset

O projeto utilizará o **BANKING77**, dataset público destinado à classificação de intenções no domínio bancário.

O dataset contém:

* **13.083** consultas de clientes;
* **77** categorias de intenção;
* textos em língua inglesa;
* divisão oficial entre conjuntos de treinamento e teste;
* estrutura adequada para problemas de classificação multiclasse.

A estrutura básica utilizada pelo modelo é:

```text
text → label
```

Exemplo:

```text
"I am still waiting on my card?" → card_arrival
```

Dataset:

https://huggingface.co/datasets/PolyAI/banking77

---

## 🧠 Estratégia Inicial de Modelagem

A primeira abordagem prevista para o projeto utilizará técnicas clássicas de NLP e Machine Learning.

O baseline inicial será composto por:

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

A escolha busca estabelecer um modelo inicial leve, reproduzível e adequado para comparação de desempenho e latência.

Outros algoritmos poderão ser avaliados durante a fase de experimentação.

---

## 🏗️ Arquitetura Planejada

A arquitetura será construída incrementalmente durante o desenvolvimento do Tech Challenge.

A visão inicial é:

```text
                    BANKING77
                        │
                        ▼
                Pipeline de Dados
                        │
                        ▼
                 Treinamento NLP
                        │
                        ▼
                      Modelo
                        │
                        ▼
                     FastAPI
                        │
                        ▼
                     Docker
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
            Cliente           Prometheus
                                  │
                                  ▼
                               Grafana
```

O pipeline de treinamento deverá posteriormente ser orquestrado utilizando **Apache Airflow**.

O processo de desenvolvimento também contará com um pipeline de **CI/CD utilizando GitHub Actions**.

---

## ⚡ Otimização de Inferência

Além do modelo baseline, o projeto prevê a avaliação de técnicas de otimização da inferência.

Inicialmente será avaliada a conversão do modelo para **ONNX**, permitindo comparar a execução do modelo original com uma versão executada utilizando **ONNX Runtime**.

Serão avaliadas métricas como:

* latência média;
* percentil 50 (P50);
* percentil 95 (P95);
* percentil 99 (P99);
* throughput;
* tamanho do modelo.

Os resultados serão documentados ao longo do desenvolvimento.

---

## 📈 Monitoramento

A aplicação será instrumentada utilizando **Prometheus**, permitindo coletar métricas relacionadas à execução da API e do modelo.

Entre as métricas inicialmente previstas estão:

* quantidade total de requisições;
* tempo de resposta;
* taxa de erros;
* quantidade de classificações realizadas.

As métricas serão visualizadas através de dashboards no **Grafana**.

---

## 🔄 Pipeline de Treinamento

O processo de treinamento será automatizado utilizando **Apache Airflow**.

A estrutura inicial prevista para a DAG é:

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
       │
       ▼
Exportar ONNX
```

Essa estrutura poderá evoluir conforme as necessidades identificadas durante o desenvolvimento.

---

## 🔧 Tecnologias Planejadas

As principais tecnologias previstas para o projeto são:

* Python
* Scikit-Learn
* Pandas
* Hugging Face Datasets
* FastAPI
* Docker
* GitHub Actions
* Apache Airflow
* Prometheus
* Grafana
* ONNX
* ONNX Runtime
* Pytest

A inclusão das dependências será feita progressivamente conforme cada componente for implementado.

---

## 📂 Estrutura do Projeto

A estrutura inicial do projeto será mantida propositalmente simples e evoluirá junto com a implementação.

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

Novos diretórios serão adicionados conforme os respectivos componentes forem desenvolvidos.

---

## 🚀 Status do Projeto

> 🚧 **Em desenvolvimento**

O projeto será desenvolvido de maneira incremental, permitindo acompanhar através do histórico do Git a evolução desde a análise dos dados até a disponibilização e monitoramento do modelo.

### Próximas etapas

* [ ] Configurar estrutura inicial do projeto
* [ ] Documentar arquitetura inicial
* [ ] Implementar carregamento do BANKING77
* [ ] Realizar análise exploratória dos dados (EDA)
* [ ] Implementar modelo baseline
* [ ] Avaliar métricas do modelo
* [ ] Criar API de inferência
* [ ] Containerizar aplicação
* [ ] Configurar pipeline CI/CD
* [ ] Implementar DAG de treinamento no Airflow
* [ ] Instrumentar métricas com Prometheus
* [ ] Criar dashboard no Grafana
* [ ] Converter e validar modelo ONNX
* [ ] Realizar benchmark de latência
* [ ] Consolidar documentação e resultados

---

## 📚 Tech Challenge

O projeto faz parte do **Tech Challenge — Fase 3** e tem como foco o deploy de modelos de Machine Learning em produção, contemplando CI/CD, orquestração, monitoramento e otimização de latência.

O desenvolvimento será realizado de forma incremental, mantendo o histórico de commits como registro da evolução técnica do projeto.

---

## 📄 Licença

O código-fonte deste projeto será disponibilizado sob a licença definida no arquivo `LICENSE`.

O dataset **BANKING77** possui seus próprios termos e licença de distribuição, independentes da licença aplicada ao código deste repositório.
