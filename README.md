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
**Single Responsibility Principle (SRP)**.

Atualmente, as principais responsabilidades estão organizadas da seguinte forma:

| Componente | Responsabilidade |
| --- | --- |
| `domain` | Representação dos objetos e resultados das análises |
| `application` | Execução das análises e regras da aplicação |
| `infrastructure` | Integração e carregamento de fontes externas de dados |
| `presentation` | Formatação e apresentação dos resultados |
| `main.py` | Orquestração do fluxo da aplicação |

Dentro da camada `application`, as responsabilidades da EDA também foram
separadas para evitar que um único serviço concentre diferentes tipos de análise:

| Componente | Responsabilidade |
| --- | --- |
| `DatasetService` | Análise estrutural e qualidade básica do dataset |
| `ClassDistributionAnalyzer` | Distribuição das classes e estatísticas de balanceamento |
| `TextLengthAnalyzer` | Comprimento dos textos, percentis e identificação de possíveis outliers |
| `CorpusAnalyzer` | Características do corpus e frequência dos tokens |

A apresentação dos resultados no terminal permanece isolada no `ConsoleReporter`,
evitando que o ponto de entrada da aplicação concentre regras de análise e
formatação de saída.

Essa organização permite que cada componente tenha uma responsabilidade mais
coesa e possa evoluir de forma independente à medida que novas etapas forem
incorporadas ao projeto.

### 📐 Documentação da arquitetura

A arquitetura do projeto é documentada em [`docs/architecture.md`](docs/architecture.md).

Esse documento concentra as decisões arquiteturais e a evolução da organização
interna do projeto, enquanto este README apresenta uma visão resumida do estado
atual da implementação.

A estrutura foi evoluída incrementalmente para manter responsabilidades bem
definidas e evitar que um único serviço concentre diferentes tipos de análise.

A organização atual inclui:

```text
src/banking_intent_classifier/
├── application/
│   ├── class_distribution_analyzer.py
│   ├── corpus_analyzer.py
│   ├── dataset_service.py
│   └── text_length_analyzer.py
├── domain/
│   └── dataset_summary.py
├── infrastructure/
│   └── data/
│       └── banking77_loader.py
├── presentation/
│   └── console_reporter.py
└── main.py
```

A separação das análises de distribuição de classes, comprimento dos textos e
características do corpus foi realizada como uma refatoração estrutural, mantendo
o comportamento previamente validado da aplicação.

Os testes automatizados foram utilizados como rede de segurança durante essa
evolução, permitindo extrair as responsabilidades progressivamente e verificar
que os resultados da EDA permaneceram inalterados.

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

A média superior à mediana, tanto em caracteres quanto em palavras, indica uma distribuição assimétrica à direita, com a presença de mensagens mais longas na cauda da distribuição.

#### ✅ Distribuição do comprimento dos textos

Para compreender melhor essa distribuição, também foram calculados os principais percentis dos comprimentos das mensagens.

| Percentil | Caracteres | Palavras |
| --------- | ---------: | -------: |
| P25       |      36,00 |     7,00 |
| P50       |      47,00 |    10,00 |
| P75       |      64,00 |    13,00 |
| P90       |     110,00 |    22,00 |
| P95       |     152,00 |    29,80 |
| P99       |     221,96 |    43,00 |

Os resultados mostram que **75% das mensagens possuem até 64 caracteres e 13 palavras**, enquanto **90% possuem até 110 caracteres e 22 palavras**.

A diferença entre os percentis superiores e a mediana confirma a existência de uma cauda de mensagens mais longas no conjunto de treinamento.

#### ✅ Análise de possíveis outliers

Para identificar valores extremos na distribuição do comprimento dos textos, foi utilizado o critério do **Intervalo Interquartil (IQR)**.

Os limites e resultados encontrados foram:

| Medida | Limite inferior | Limite superior | Possíveis outliers | Percentual |
| ------ | --------------: | --------------: | -----------------: | ---------: |
| Caracteres | -6,00 | 106,00 | 1.038 | 10,38% |
| Palavras | -2,00 | 22,00 | 930 | 9,30% |

O critério IQR identificou uma cauda de mensagens mais longas, correspondendo a aproximadamente **10% do conjunto de treinamento**.

Esses registros serão preservados, pois o comprimento elevado, isoladamente, **não caracteriza erro ou baixa qualidade textual**. Em um problema de classificação de intenções, mensagens mais detalhadas podem representar exemplos legítimos do comportamento esperado dos usuários.

Dessa forma, nenhuma remoção será realizada nesta etapa da EDA. O impacto desses exemplos será reavaliado posteriormente durante a modelagem e a análise de desempenho do classificador.

#### ✅ Características gerais do corpus

Também foram analisadas características gerais do corpus textual do conjunto de treinamento.

Os resultados encontrados foram:

| Métrica | Resultado |
| --- | ---: |
| Documentos | 10.003 |
| Total de palavras | 119.530 |
| Palavras únicas — corpus bruto | 4.518 |
| Palavras únicas após lowercase | 4.136 |
| Palavras únicas após lowercase + tratamento de pontuação | 2.452 |

A conversão dos tokens para **lowercase** reduziu o vocabulário de 4.518 para 4.136 tokens únicos, uma redução de aproximadamente **8,46%**.

Ao considerar também o tratamento de caracteres de pontuação nas extremidades dos tokens produzidos pela separação por espaços, o vocabulário foi reduzido para 2.452 tokens únicos. Isso representa uma redução de aproximadamente **45,73% em relação ao vocabulário bruto**.

Esses resultados indicam que diferenças de capitalização e pontuação contribuem significativamente para a fragmentação do vocabulário. Por esse motivo, essas transformações serão consideradas na definição do pré-processamento utilizado na etapa de representação textual.

##### Tokens mais frequentes

Após a aplicação de lowercase e do tratamento de pontuação utilizado nesta análise exploratória, os 20 tokens mais frequentes no conjunto de treinamento foram:

| Token | Frequência | Token | Frequência |
| --- | ---: | --- | ---: |
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

Entre os tokens mais frequentes aparecem tanto palavras funcionais da língua inglesa, como `i`, `my`, `to`, `a` e `the`, quanto termos diretamente relacionados ao domínio bancário, como `card`, `account`, `money` e `transfer`.

A presença de palavras funcionais entre os termos mais frequentes não implica, neste momento, sua remoção automática. A utilização de **stopwords** será tratada como uma hipótese experimental durante a construção do baseline, permitindo comparar configurações e avaliar seu impacto por meio das métricas do modelo.

##### Decisões preliminares para o pré-processamento

A análise do corpus fornece evidências para considerar:

* normalização para lowercase;
* tratamento de pontuação;
* avaliação experimental da remoção de stopwords.

Essas decisões ainda não alteram o dataset original. Elas serão avaliadas durante a construção da representação textual e do modelo baseline.

#### 🔄 Próximas análises

Com as características gerais do corpus analisadas, a próxima etapa será consolidar as decisões de pré-processamento e iniciar a representação textual utilizada pelo modelo baseline.

A estratégia inicial permanece:

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

As configurações de pré-processamento serão avaliadas experimentalmente para que as decisões sejam orientadas pelos resultados do modelo, especialmente pelas métricas adequadas à classificação multiclasse.

### 📋 Roadmap

* [x] Estrutura inicial do projeto
* [x] Arquitetura inicial
* [x] Carregamento do BANKING77
* [x] Validação estrutural do dataset
* [ ] Análise exploratória dos dados (EDA)
  * [x] Distribuição das classes
  * [x] Estatísticas de balanceamento
  * [x] Comprimento dos textos
  * [x] Distribuição dos comprimentos
  * [x] Análise de possíveis outliers
  * [x] Características gerais do corpus
  * [ ] Definição e avaliação do pré-processamento textual
* [x] Refatoração das responsabilidades da EDA
  * [x] Extrair análise da distribuição de classes
  * [x] Extrair análise do comprimento dos textos
  * [x] Extrair análise do corpus
  * [x] Adicionar testes automatizados para os analyzers
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