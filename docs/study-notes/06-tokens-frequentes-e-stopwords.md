# 06 — Tokens frequentes e stopwords

## Objetivo

Depois de observar o tamanho do vocabulário, investigamos quais tokens aparecem com maior frequência.

## Top 20

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

## Dois grupos aparecem

### Palavras funcionais

Exemplos:

- `i`
- `my`
- `to`
- `a`
- `the`
- `is`
- `and`

Muitas delas são candidatas comuns a listas de **stopwords**.

### Termos do domínio

Exemplos:

- `card`
- `account`
- `money`
- `transfer`

Esses termos têm relação direta com o contexto bancário.

## O que são stopwords?

Stopwords são palavras muito frequentes que, em determinados problemas, podem carregar pouca informação discriminativa.

Mas a palavra “pouca” é importante: sua utilidade depende da tarefa.

## Por que não removemos stopwords imediatamente?

Porque estamos resolvendo **classificação de intenção**.

Palavras funcionais podem participar de padrões úteis e removê-las antecipadamente é uma hipótese sobre o que o modelo precisa.

Além disso, TF-IDF já reduz a importância relativa de termos presentes em muitos documentos.

## Estratégia experimental

Comparar:

```text
Experimento A
TF-IDF sem remoção de stopwords

versus

Experimento B
TF-IDF com stopwords em inglês
```

Depois comparar as métricas, especialmente Macro F1 e desempenho por classe.

## Aprendizado

Frequência alta não significa automaticamente irrelevância.

Em Machine Learning, preprocessing também pode ser tratado como hiperparâmetro ou escolha experimental.

## Como explicar em vídeo

> “A lista dos tokens mais frequentes contém muitas palavras funcionais, mas também termos importantes do domínio bancário. Em vez de remover stopwords automaticamente, decidimos transformar isso em um experimento: treinaremos configurações com e sem remoção e deixaremos as métricas indicar qual estratégia funciona melhor.”
