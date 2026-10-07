# 13 — TF-IDF, pré-processamento e stopwords

## Contexto

Durante a análise exploratória do BANKING77 foram investigadas algumas
transformações simples sobre o corpus textual, principalmente:

- conversão dos tokens para lowercase;
- tratamento de caracteres de pontuação nas extremidades dos tokens;
- análise dos tokens mais frequentes;
- possível remoção de stopwords.

Essas análises mostraram que capitalização e pontuação contribuem para a
fragmentação do vocabulário.

Entretanto, uma transformação utilizada durante a EDA não precisa
necessariamente ser implementada manualmente no pipeline de Machine Learning.

## EDA não é o mesmo que pipeline de pré-processamento

Durante a EDA foi utilizada uma normalização exploratória semelhante a:

```python
word.lower().strip(string.punctuation)
```

O objetivo era compreender como essas transformações afetavam o vocabulário.

Na etapa de representação textual, porém, será utilizado inicialmente o
`TfidfVectorizer` do scikit-learn.

O vectorizer já possui comportamentos próprios relacionados à normalização e
tokenização dos textos, incluindo conversão para lowercase por padrão.

Portanto, não será criado automaticamente um pré-processamento manual apenas
porque essas transformações foram utilizadas durante a EDA.

A decisão será manter o pipeline tão simples quanto possível e adicionar
transformações somente quando houver evidências de que elas são necessárias.

## Hipótese sobre stopwords

A análise dos tokens mais frequentes mostrou a presença de diversas palavras
funcionais da língua inglesa, como:

```text
i
my
to
a
the
is
it
do
can
for
how
what
why
you
and
was
```

Isso levantou a hipótese de que a remoção de stopwords poderia reduzir ruído
na representação textual.

Entretanto, frequência elevada não significa automaticamente que esses tokens
não possuem informação útil para distinguir as intents.

Por esse motivo, a remoção de stopwords será tratada como uma hipótese
experimental.

## Configurações avaliadas

Foram definidas inicialmente duas configurações do `TfidfVectorizer`.

### Configuração A — preservar stopwords

```python
TfidfVectorizer(
    stop_words=None,
)
```

Nessa configuração, palavras como:

```text
the
how
can
```

permanecem no vocabulário.

### Configuração B — remover stopwords em inglês

```python
TfidfVectorizer(
    stop_words="english",
)
```

Nessa configuração, stopwords inglesas reconhecidas pelo vectorizer são
removidas do vocabulário.

## Testes automatizados

Foram adicionados testes para verificar explicitamente o comportamento das
duas configurações.

Resultado:

```text
test_should_remove_english_stopwords_when_configured PASSED
test_should_keep_english_stopwords_when_not_configured PASSED

2 passed
```

Os testes confirmam que as configurações produzem o comportamento esperado.

Entretanto, eles ainda não demonstram qual configuração produz o melhor
classificador.

## Próximo experimento

A próxima etapa consiste em comparar as duas configurações utilizando as
mesmas condições de treinamento:

```text
                    BANKING77 TRAIN
                          │
                ┌─────────┴─────────┐
                │                   │
                ▼                   ▼
       stop_words=None     stop_words="english"
                │                   │
                ▼                   ▼
             TF-IDF              TF-IDF
                │                   │
                ▼                   ▼
      Logistic Regression   Logistic Regression
                │                   │
                ▼                   ▼
             métricas             métricas
                │                   │
                └─────────┬─────────┘
                          ▼
                       comparar
```

Para que o experimento seja controlado, as demais configurações devem
permanecer iguais.

A variável analisada inicialmente será apenas:

```text
stop_words
```

## Métrica principal

Como o BANKING77 possui 77 classes e sua distribuição não é perfeitamente
uniforme, o **Macro F1** será uma das principais métricas utilizadas na
comparação.

Também poderão ser observadas posteriormente:

- accuracy;
- weighted F1;
- precision;
- recall;
- F1 por classe;
- classes frequentemente confundidas.

## Decisão pendente

Neste momento ainda não existe evidência suficiente para decidir pela remoção
das stopwords.

A decisão será tomada somente após comparar o desempenho das duas
configurações no problema real de classificação.

Portanto:

```text
lowercase
    └── comportamento já oferecido pelo TfidfVectorizer

tokenização
    └── inicialmente delegada ao TfidfVectorizer

stopwords
    └── decisão experimental ainda pendente
```

## Aprendizado

Uma etapa exploratória ajuda a formular hipóteses, mas não deve transformar
automaticamente todas as observações em regras do pipeline.

O fluxo adotado neste projeto é:

```text
observação na EDA
        ↓
formulação de hipótese
        ↓
experimento controlado
        ↓
métricas
        ↓
decisão
        ↓
pipeline final
```

Essa abordagem evita adicionar complexidade ao pré-processamento sem evidência
de benefício para o modelo.

## Resultado do experimento

A hipótese sobre remoção de stopwords foi avaliada utilizando o conjunto
`train` do BANKING77 dividido de forma estratificada e reproduzível em:

- treino interno: 8.002 registros;
- validação: 2.001 registros;
- 77 classes presentes em ambos os conjuntos;
- `random_state=42`.

O conjunto oficial `test` não foi utilizado durante essa decisão.

Foram comparadas duas configurações, mantendo as demais condições do
experimento constantes:

| Configuração | Accuracy | Macro F1 | Weighted F1 |
|---|---:|---:|---:|
| `stop_words=None` | 0.8491 | 0.8412 | 0.8482 |
| `stop_words="english"` | 0.8206 | 0.8137 | 0.8198 |

A remoção das stopwords produziu uma redução de:

- Accuracy: 0.0285;
- Macro F1: 0.0275;
- Weighted F1: 0.0284.

No critério principal do experimento, Macro F1, o resultado caiu de
84,12% para 81,37%, uma diferença de 2,75 pontos percentuais.

## Decisão

A configuração adotada para o baseline será:

```python
TfidfVectorizer(
    stop_words=None,
)