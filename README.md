# Banking Intent Classifier

Projeto desenvolvido para o **Tech Challenge — Fase 3 da Pós-Tech FIAP em Machine Learning Engineering**.

O projeto tem como objetivo desenvolver uma solução de Machine Learning capaz de identificar automaticamente a intenção presente em mensagens de clientes de serviços bancários, explorando técnicas de **Processamento de Linguagem Natural (NLP)** e práticas relacionadas ao ciclo de vida de modelos em produção.

## 🎯 Contexto e problema

Canais digitais de atendimento bancário recebem mensagens escritas de diferentes formas para representar necessidades semelhantes. Antes que uma solicitação possa ser direcionada para um fluxo de atendimento adequado, é necessário identificar qual intenção está associada à mensagem do cliente.

Esse cenário pode ser tratado como um problema de **classificação multiclasse de textos**:

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

> **Como classificar automaticamente mensagens de clientes de serviços bancários de acordo com sua intenção, utilizando técnicas de Processamento de Linguagem Natural e Machine Learning?**

## 💡 Proposta de solução

A proposta é construir progressivamente um classificador de intenções bancárias.

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

O desenvolvimento será realizado de forma incremental, começando pela compreensão e validação dos dados, passando pela construção de um modelo baseline e evoluindo posteriormente para disponibilização, automação, monitoramento e otimização da solução.

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

Essa abordagem permitirá estabelecer um **baseline mensurável** antes da avaliação de estratégias adicionais.

## 🏦 Por que o BANKING77?

O **BANKING77** foi escolhido por representar diretamente um problema supervisionado de classificação textual no domínio bancário.

Sua estrutura atende ao objetivo do projeto:

```text
text → label
```

O conjunto utilizado possui:

- **13.083 mensagens**;
- **10.003 registros de treinamento**;
- **3.080 registros de teste**;
- **77 classes de intenção**.

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

A escolha também permite trabalhar com um cenário mais desafiador do que uma classificação binária simples. O modelo deverá distinguir **77 intenções**, incluindo categorias semanticamente próximas.

Isso possibilita explorar aspectos relevantes de NLP e Machine Learning, como:

- representação textual;
- classificação multiclasse;
- distribuição e balanceamento das classes;
- avaliação global e por classe;
- análise de erros;
- capacidade de generalização para diferentes formas de expressar uma mesma intenção.

## 🚀 Objetivo técnico

Além da construção do classificador, o projeto busca percorrer progressivamente etapas relevantes do ciclo de vida de uma solução de Machine Learning:

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

Dessa forma, o projeto não se limita ao treinamento de um modelo. A proposta é evoluir para uma solução organizada, reproduzível, avaliável e preparada para as demais etapas previstas no Tech Challenge.

---

## 🚀 Status do Projeto

> 🚧 **Em desenvolvimento**

O desenvolvimento está sendo realizado de forma incremental, mantendo o histórico de commits e Pull Requests como registro da evolução técnica e das decisões realizadas durante o projeto.

### ✅ Estrutura e arquitetura inicial

* [x] Criar estrutura inicial do projeto
* [x] Configurar projeto Python com `uv`
* [x] Organizar o código utilizando separação de responsabilidades
* [x] Criar camadas iniciais de `application`, `domain` e `infrastructure`
* [x] Criar camada `presentation` para apresentação dos resultados
* [x] Manter o `main.py` responsável apenas pela orquestração da aplicação
* [x] Separar análise dos dados da apresentação no console
* [x] Documentar arquitetura inicial

#### Organização das responsabilidades

A estrutura do projeto está sendo evoluída de forma incremental, buscando manter
responsabilidades bem definidas e aplicar princípios de design como o
Single Responsibility Principle (SRP).

Atualmente, as principais responsabilidades estão organizadas da seguinte forma:

| Componente | Responsabilidade |
| --- | --- |
| `domain` | Representação dos objetos e resultados das análises |
| `application` | Execução das análises e regras da aplicação |
| `infrastructure` | Integração e carregamento de fontes externas de dados |
| `presentation` | Formatação e apresentação dos resultados |
| `main.py` | Orquestração do fluxo da aplicação |

A apresentação dos resultados no terminal foi isolada no `ConsoleReporter`,
evitando que o ponto de entrada da aplicação concentre regras de análise e
formatação de saída.

### 📐 Documentação da arquitetura

A arquitetura do projeto é documentada em [`docs/architecture.md`](docs/architecture.md).

Esse documento concentra as decisões arquiteturais e a evolução da organização interna do projeto, enquanto este README apresenta uma visão resumida do estado atual da implementação.

A estrutura atual separa as responsabilidades entre:

```text
src/banking_intent_classifier/
├── application/
│   └── dataset_service.py
├── domain/
│   └── dataset_summary.py
├── infrastructure/
│   └── data/
│       └── banking77_loader.py
├── presentation/
│   └── console_reporter.py
└── main.py
```

As responsabilidades principais são:

- `domain`: representa os objetos e resultados das análises;
- `application`: executa as análises e regras da aplicação;
- `infrastructure`: integra e carrega fontes externas de dados;
- `presentation`: formata e apresenta os resultados;
- `main.py`: atua como ponto de entrada e orquestra o fluxo da aplicação.

A criação da camada `presentation` permite retirar do `main.py` a responsabilidade de formatar e imprimir os resultados. A saída para o terminal fica concentrada no `ConsoleReporter`, enquanto o ponto de entrada permanece responsável pela coordenação dos componentes.

Essa separação busca manter responsabilidades bem definidas e aplicar de forma incremental princípios como o **Single Responsibility Principle (SRP)**, evitando abstrações desnecessárias para o estágio atual do projeto.

### ✅ Dataset e carregamento

* [x] Definir BANKING77 como dataset do projeto
* [x] Utilizar a fonte oficial `PolyAI/banking77`
* [x] Implementar carregamento através do Hugging Face
* [x] Validar os splits de treino e teste
* [x] Confirmar 13.083 registros
* [x] Confirmar as 77 classes em ambos os splits

### ✅ Validação estrutural dos dados

A validação inicial do BANKING77 foi concluída com os seguintes resultados:

| Validação            | Treino | Teste |
| -------------------- | -----: | ----: |
| Registros            | 10.003 | 3.080 |
| Classes              |     77 |    77 |
| Textos ausentes      |      0 |     0 |
| Labels ausentes      |      0 |     0 |
| Textos vazios        |      0 |     0 |
| Registros duplicados |      0 |     0 |

Também foi verificada a existência de textos compartilhados entre os conjuntos de treino e teste:

```text
Textos presentes em treino e teste: 0
```

Com isso, não foram identificados problemas estruturais que exijam, neste momento, remoção, imputação ou correção de registros.

A ausência de textos compartilhados entre os splits também reduz o risco de data leakage decorrente da presença da mesma mensagem nos conjuntos de treino e teste.

### 🔄 Análise Exploratória dos Dados — EDA

Com a validação estrutural concluída, foi iniciada a **Análise Exploratória dos Dados (EDA)** do BANKING77.

A análise está sendo realizada de forma incremental, com cada etapa implementada e validada separadamente antes do avanço para a próxima análise.

#### ✅ Distribuição das classes

O conjunto de treinamento possui **10.003 registros distribuídos entre 77 intents**.

As frequências observadas apresentam as seguintes estatísticas:

| Métrica | Exemplos por classe |
| ------- | ------------------: |
| Mínimo  |                  35 |
| Máximo  |                 187 |
| Média   |              129,91 |
| Mediana |                 127 |

Entre as classes com menor quantidade de exemplos estão:

* `contactless_not_working`: 35
* `virtual_card_not_working`: 41
* `card_acceptance`: 59
* `card_swallowed`: 61

Entre as classes com maior quantidade de exemplos estão:

* `card_payment_fee_charged`: 187
* `direct_debit_payment_not_recognised`: 182
* `balance_not_updated_after_cheque_or_cash_deposit`: 181
* `wrong_amount_of_cash_received`: 180

A distribuição das classes não é perfeitamente uniforme. A maior classe possui aproximadamente **5,34 vezes** a quantidade de exemplos da menor classe.

Neste momento, nenhuma técnica de balanceamento será aplicada. A necessidade de estratégias específicas para lidar com o desbalanceamento será avaliada posteriormente a partir dos resultados do modelo baseline e de métricas adequadas para classificação multiclasse, especialmente o desempenho por classe e o **Macro F1**.

#### ✅ Comprimento dos textos

Também foram analisados os comprimentos das mensagens presentes no conjunto de treinamento, considerando tanto a quantidade de caracteres quanto a quantidade de palavras.

| Métrica | Caracteres | Palavras |
| ------- | ---------: | -------: |
| Mínimo  |         13 |        2 |
| Máximo  |        433 |       79 |
| Média   |      59,47 |    11,95 |
| Mediana |         47 |       10 |

Os resultados mostram que as mensagens do BANKING77 são, em geral, relativamente curtas.

A média superior à mediana, tanto em caracteres quanto em palavras, indica a presença de textos mais longos que deslocam a distribuição para a direita.

Essas características serão consideradas posteriormente na definição das estratégias de representação textual e dos parâmetros utilizados durante a modelagem.

#### 🔄 Próximas análises

A EDA continuará investigando características relevantes do corpus antes da construção do primeiro modelo baseline.

Entre os próximos pontos de análise estão:

* distribuição do comprimento dos textos;
* identificação de possíveis valores extremos;
* características gerais do vocabulário;
* possíveis padrões relevantes para a etapa de modelagem;
* definição das decisões iniciais de pré-processamento.

Os resultados consolidados da EDA serão utilizados para orientar a estratégia de representação textual, os parâmetros iniciais do modelo e o protocolo de avaliação.

### 📋 Roadmap

* [x] Estrutura inicial do projeto
* [x] Arquitetura inicial
* [x] Carregamento do BANKING77
* [x] Validação estrutural do dataset
* [ ] Análise exploratória dos dados (EDA)

  * [x] Distribuição das classes
  * [x] Estatísticas de balanceamento
  * [x] Comprimento dos textos
  * [ ] Distribuição dos comprimentos
  * [ ] Características gerais do corpus
* [ ] Implementação do modelo baseline
* [ ] Avaliação das métricas do modelo
* [ ] API de inferência
* [ ] Containerização
* [ ] Pipeline CI/CD
* [ ] Pipeline de treinamento com Airflow
* [ ] Monitoramento com Prometheus
* [ ] Dashboards no Grafana
* [ ] Conversão e validação ONNX
* [ ] Benchmark de latência
* [ ] Documentação e resultados finais

