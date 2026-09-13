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

O projeto utiliza o dataset público **BANKING77**, que contém mensagens de clientes relacionadas a diferentes serviços bancários.

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

O projeto utiliza o **BANKING77**, dataset público destinado à classificação de intenções no domínio bancário.

A fonte utilizada pelo projeto é o dataset oficial da **PolyAI**, disponibilizado através do Hugging Face.

O dataset contém:

* **13.083 registros**;
* **10.003 registros de treinamento**;
* **3.080 registros de teste**;
* **77 categorias de intenção**;
* textos em língua inglesa;
* estrutura adequada para classificação multiclasse.

A estrutura utilizada pelo modelo é:

```text
text → label
```

Exemplo de registro:

```python
{
    "text": "I am still waiting on my card?",
    "label": 11
}
```

O carregamento é realizado programaticamente através da biblioteca `datasets`, sem necessidade de armazenar o dataset no repositório.

Fonte:

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

> A etapa de modelagem ainda não foi iniciada.

---

## 🏗️ Arquitetura Planejada

A arquitetura está sendo construída incrementalmente durante o desenvolvimento do Tech Challenge.

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

A documentação da arquitetura inicial está disponível em:

```text
docs/architecture.md
```

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

Esta etapa será implementada após a validação do modelo baseline.

---

## 📈 Monitoramento

A aplicação será posteriormente instrumentada utilizando **Prometheus**.

Entre as métricas inicialmente previstas estão:

* quantidade total de requisições;
* tempo de resposta;
* taxa de erros;
* quantidade de classificações realizadas.

As métricas serão visualizadas através de dashboards no **Grafana**.

---

## 🔄 Pipeline de Treinamento

O processo de treinamento será posteriormente automatizado utilizando **Apache Airflow**.

A estrutura inicialmente planejada é:

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

## 🔧 Tecnologias

### Atualmente utilizadas

* Python 3.12+
* uv
* Hugging Face Datasets
* Pandas

### Planejadas

* Scikit-Learn
* FastAPI
* Docker
* GitHub Actions
* Apache Airflow
* Prometheus
* Grafana
* ONNX
* ONNX Runtime
* Pytest
* Ruff

As dependências serão adicionadas progressivamente conforme cada componente for implementado.

---

## 📂 Estrutura Atual do Projeto

A estrutura do projeto está sendo mantida propositalmente simples e evoluirá junto com a implementação.

```text
banking-intent-classifier/
│
├── README.md
├── pyproject.toml
├── uv.lock
│
├── docs/
│   └── architecture.md
│
└── src/
    └── banking_intent_classifier/
        ├── __init__.py
        ├── main.py
        │
        └── data/
            ├── __init__.py
            └── loader.py
```

Novos diretórios serão adicionados somente quando os respectivos componentes forem necessários.

---

## ▶️ Execução Local

O projeto utiliza **uv** para gerenciamento do ambiente Python e das dependências.

### Sincronizar o ambiente

```bash
uv sync
```

### Executar a aplicação

```bash
uv run python -m banking_intent_classifier.main
```

No estágio atual, a execução carrega o BANKING77 e apresenta informações básicas sobre o dataset.

Exemplo:

```text
BANKING77
----------------------------------------
Registros de treino: 10003
Registros de teste: 3080
Total de registros: 13083
Classes no treino: 77
Classes no teste: 77
```

---

## 🚀 Status do Projeto

> 🚧 **Em desenvolvimento**

O desenvolvimento está sendo realizado de forma incremental, mantendo o histórico de commits como registro da evolução técnica do projeto.

### Concluído

* [x] Criar estrutura inicial do projeto
* [x] Configurar projeto Python com `uv`
* [x] Documentar arquitetura inicial
* [x] Definir BANKING77 como dataset do projeto
* [x] Implementar carregamento do BANKING77 através do Hugging Face
* [x] Validar os splits de treino e teste
* [x] Validar a presença das 77 classes nos dois splits

### Próximas etapas

* [ ] Validar valores ausentes
* [ ] Identificar registros duplicados
* [ ] Realizar análise exploratória dos dados (EDA)
* [ ] Implementar modelo baseline
* [ ] Avaliar métricas do modelo
* [ ] Criar API de inferência
* [ ] Containerizar aplicação
* [ ] Configurar pipeline CI/CD
* [ ] Implementar DAG de treinamento no Airflow
* [ ] Instrumentar métricas com Prometheus
* [ ] Criar dashboards no Grafana
* [ ] Converter e validar modelo ONNX
* [ ] Realizar benchmark de latência
* [ ] Consolidar documentação e resultados

---

## 🌿 Estratégia de Versionamento

O desenvolvimento utiliza duas branches principais:

```text
main
 │
 └── dev
```

A branch `dev` concentra o desenvolvimento corrente.

Quando um conjunto de funcionalidades atingir um estado estável e validado, as alterações poderão ser integradas à branch `main`.

O projeto utiliza mensagens de commit seguindo o padrão **Conventional Commits**, mantendo as descrições em português.

Exemplos:

```text
feat: adicionar carregamento do dataset BANKING77
docs: atualizar documentação do projeto
test: adicionar testes do carregamento de dados
fix: corrigir validação dos dados
```

---

## 📚 Tech Challenge

O projeto faz parte do **Tech Challenge — Fase 3** e tem como foco o deploy de modelos de Machine Learning em produção, contemplando CI/CD, orquestração, monitoramento e otimização de latência.

O desenvolvimento é realizado de forma incremental para que o histórico do repositório também registre a evolução das decisões e implementações realizadas durante o projeto.

---

## 📄 Licença

O código-fonte deste projeto será disponibilizado sob a licença definida no arquivo `LICENSE`.

O dataset **BANKING77** possui seus próprios termos e licença de distribuição, independentes da licença aplicada ao código deste repositório.
