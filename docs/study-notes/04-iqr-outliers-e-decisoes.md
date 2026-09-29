# 04 — IQR, possíveis outliers e decisões sobre remoção

## O que é IQR?

O **Intervalo Interquartil (IQR)** mede a distância entre o primeiro e o terceiro quartil:

```text
IQR = Q3 - Q1
```

Uma regra comum identifica possíveis valores extremos utilizando:

```text
limite inferior = Q1 - 1,5 × IQR
limite superior = Q3 + 1,5 × IQR
```

## Resultados

| Medida | Limite inferior | Limite superior | Possíveis outliers | Percentual |
| --- | ---: | ---: | ---: | ---: |
| Caracteres | -6,00 | 106,00 | 1.038 | 10,38% |
| Palavras | -2,00 | 22,00 | 930 | 9,30% |

A análise identifica principalmente uma cauda à direita, formada pelas mensagens mais longas.

## O ponto mais importante

**Outlier estatístico não significa dado inválido.**

Uma mensagem bancária mais longa pode ser perfeitamente legítima. Ela pode conter contexto adicional, explicações ou detalhes sobre o problema do cliente.

Excluir automaticamente essas mensagens poderia eliminar exemplos reais que o classificador deverá reconhecer em produção.

## Decisão do projeto

Os registros foram preservados.

O impacto das mensagens longas será reavaliado posteriormente durante a modelagem e análise de erros.

## Ponto de atenção

Um algoritmo estatístico identifica observações incomuns em relação à distribuição. Ele não conhece o significado do domínio.

Por isso:

```text
valor extremo
     ≠
dado incorreto
```

A decisão de remover precisa combinar estatística, domínio e impacto no modelo.

## Aprendizado

EDA não deve ser uma sequência automática de “encontrar problema → apagar dado”.

Ela deve apoiar decisões.

## Como explicar em vídeo

> “O IQR marcou cerca de 10% das mensagens como possíveis outliers de comprimento. Nós não as removemos, porque serem longas não significa serem inválidas. Em NLP, essas mensagens podem representar casos reais. Preferimos preservar informação e avaliar posteriormente seu impacto no modelo.”
