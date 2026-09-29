# 02 — Distribuição das classes e balanceamento

## Por que analisar as classes?

Em classificação supervisionada, a quantidade de exemplos por classe pode influenciar o aprendizado do modelo.

No BANKING77 existem **77 intents**, portanto não basta observar apenas a quantidade total de registros.

## Resultados no conjunto de treinamento

| Métrica | Exemplos por classe |
| --- | ---: |
| Mínimo | 35 |
| Máximo | 187 |
| Média | 129,91 |
| Mediana | 127 |

A maior classe possui aproximadamente **5,34 vezes** a quantidade de exemplos da menor.

Exemplos de classes menores:

- `contactless_not_working`: 35
- `virtual_card_not_working`: 41
- `card_acceptance`: 59
- `card_swallowed`: 61

Exemplos de classes maiores:

- `card_payment_fee_charged`: 187
- `direct_debit_payment_not_recognised`: 182
- `balance_not_updated_after_cheque_or_cash_deposit`: 181
- `wrong_amount_of_cash_received`: 180

## Aprendizado

“Dataset desbalanceado” não significa automaticamente “aplicar balanceamento”.

Uma técnica de oversampling, undersampling ou pesos de classe altera o processo de treinamento. Portanto, deve existir uma razão mensurável para utilizá-la.

## Decisão do projeto

Não aplicar técnicas de balanceamento antes do baseline.

Primeiro será observado:

- desempenho global;
- Macro F1;
- desempenho por classe;
- classes com maior dificuldade de classificação.

Somente depois será avaliado se o desbalanceamento está produzindo um problema relevante.

## Ponto de atenção

Accuracy isoladamente pode esconder dificuldades nas classes menores.

Em um problema multiclasse com distribuição desigual, métricas agregadas e métricas por classe precisam ser analisadas em conjunto.

## Como explicar em vídeo

> “Encontramos diferença entre as frequências das 77 classes, mas decidimos não corrigir o desbalanceamento antecipadamente. Primeiro vamos construir um baseline e medir o desempenho, principalmente com Macro F1 e métricas por classe. Assim, uma eventual técnica de balanceamento será uma resposta a um problema observado, e não uma escolha automática.”
