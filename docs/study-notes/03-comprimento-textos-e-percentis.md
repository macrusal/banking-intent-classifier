# 03 — Comprimento dos textos e percentis

## Objetivo

Entender o tamanho típico das mensagens e a forma da distribuição de seus comprimentos.

Foram analisadas duas medidas:

- número de caracteres;
- número de palavras.

## Estatísticas básicas

| Métrica | Caracteres | Palavras |
| --- | ---: | ---: |
| Mínimo | 13 | 2 |
| Máximo | 433 | 79 |
| Média | 59,47 | 11,95 |
| Mediana | 47 | 10 |

As mensagens são, em geral, curtas.

A média maior que a mediana sugere uma distribuição assimétrica à direita: existem mensagens mais longas puxando a média para cima.

## Percentis

| Percentil | Caracteres | Palavras |
| --- | ---: | ---: |
| P25 | 36,00 | 7,00 |
| P50 | 47,00 | 10,00 |
| P75 | 64,00 | 13,00 |
| P90 | 110,00 | 22,00 |
| P95 | 152,00 | 29,80 |
| P99 | 221,96 | 43,00 |

## Como interpretar

P75 de 13 palavras significa que aproximadamente 75% das mensagens possuem até 13 palavras.

P90 de 22 palavras significa que aproximadamente 90% possuem até 22 palavras.

O máximo de 79 palavras mostra que existe uma cauda de mensagens consideravelmente maiores.

## Por que alguns percentis são decimais?

O comprimento individual de uma mensagem é inteiro, mas o cálculo de quantis pode utilizar interpolação entre observações. Por isso valores como `29,80` ou `221,96` são possíveis.

## Aprendizado

Média e mediana sozinhas não contam toda a história.

Percentis permitem enxergar a distribuição de maneira muito mais concreta e ajudam a responder:

- qual é o tamanho típico?
- onde começa a cauda?
- quão raros são os textos muito longos?

## Como explicar em vídeo

> “A maioria das mensagens é curta: 75% possuem até 13 palavras e 90% até 22. Entretanto, existem mensagens bem maiores, chegando a 79 palavras. Essa cauda motivou a análise seguinte com IQR.”
