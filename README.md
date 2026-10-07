# Banking Intent Classifier

Projeto desenvolvido para o **Tech Challenge — Fase 3 da Pós-Tech FIAP
em Machine Learning Engineering**.

O projeto tem como objetivo desenvolver uma solução de Machine Learning
capaz de identificar automaticamente a intenção presente em mensagens de
clientes de serviços bancários, explorando técnicas de **Processamento
de Linguagem Natural (NLP)** e práticas relacionadas ao ciclo de vida de
modelos em produção.

## 👥 Equipe

| Nome | RM | E-mail | Papel |
| :--- | :---: | :--- | :--- |
| **Marcelo da Cruz Salvador** | **RM375166** | [macrusal@gmail.com](mailto:macrusal@gmail.com) | Software Engineering · Dados · Machine Learning Engineering |

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
| Executar a suíte automatizada | `uv run pytest` |

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

No checkpoint documentado:

```text
17 passed
```

O tempo total pode variar entre máquinas.

### Experimento de stopwords: estado de reprodução

O experimento de `stop_words=None` versus `stop_words="english"` está
implementado e coberto por testes automatizados. Os resultados deste
README foram obtidos com split interno estratificado
(`random_state=42`), TF-IDF e Logistic Regression.

Entretanto, **no checkpoint atual ainda não existe um comando público de
terminal dedicado que reproduza integralmente o experimento e imprima
suas métricas**. Por isso, esta documentação não apresenta um comando
inexistente ou hipotético.

A criação dessa entrada operacional será tratada antes da consolidação
do baseline formal. O conjunto oficial de teste permanece preservado.

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

> 🚧 **Em desenvolvimento — EDA concluída e baseline experimental
> validado**

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
| `main.py` | Orquestração do fluxo da aplicação |

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
| `ModelTrainer` | Criação e treinamento do classificador Logistic Regression |
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

A etapa de EDA está concluída e o primeiro baseline experimental foi
reproduzido com sucesso. A suíte automatizada atual possui **17
testes**, todos aprovados.

```text
BANKING77
   │
   ├── Validação estrutural          ✅
   ├── Qualidade dos dados           ✅
   ├── Distribuição das 77 classes   ✅
   ├── Comprimento dos textos        ✅
   ├── Possíveis outliers / IQR      ✅
   ├── Corpus e vocabulário          ✅
   ├── Tokens frequentes             ✅
   ├── Leakage / overlap exato       ✅
   ├── Split estratificado           ✅
   └── Experimento de stopwords      ✅
              │
              ├── None     Macro F1 = 0,8412
              └── English  Macro F1 = 0,8137
```

O próximo passo é evoluir do experimento para o **baseline formal de
modelagem**, mantendo o conjunto oficial de teste preservado até a
definição da configuração a ser avaliada.

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
-   [ ] Consolidar baseline formal de modelagem
-   [ ] Avaliação final e detalhada das métricas do modelo
-   [ ] API de inferência
-   [ ] Containerização
-   [ ] Pipeline CI/CD
-   [ ] Pipeline de treinamento com Airflow
-   [ ] Monitoramento com Prometheus
-   [ ] Dashboards no Grafana
-   [ ] Conversão e validação ONNX
-   [ ] Benchmark de latência
-   [ ] Documentação e resultados finais
