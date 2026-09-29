# 05 — Corpus, vocabulário e normalização

## O que é corpus?

Neste projeto, o corpus corresponde ao conjunto de mensagens textuais utilizadas na análise.

No treinamento temos:

- 10.003 documentos;
- 119.530 palavras.

A média implícita é de aproximadamente 11,95 palavras por mensagem, coerente com a análise de comprimento realizada anteriormente.

## Vocabulário observado

| Transformação | Tokens únicos |
| --- | ---: |
| Texto bruto | 4.518 |
| Lowercase | 4.136 |
| Lowercase + tratamento de pontuação | 2.452 |

## Lowercase

Converter tokens para minúsculas reduziu o vocabulário de 4.518 para 4.136 tokens únicos.

Redução aproximada: **8,46%**.

Isso mostra que diferenças de capitalização estavam criando representações distintas para tokens que podem representar a mesma palavra.

## Pontuação

Após lowercase e tratamento de pontuação nas extremidades dos tokens produzidos por `split()`, o vocabulário caiu para 2.452 tokens únicos.

Redução aproximada em relação ao vocabulário bruto: **45,73%**.

## Ponto de atenção técnico

A implementação exploratória utiliza uma lógica equivalente a:

```python
word.lower().strip(string.punctuation)
```

`strip()` remove caracteres de pontuação **das extremidades** do token. Isso não equivale a um tokenizer linguístico completo nem garante remoção de toda pontuação interna.

É importante descrever exatamente o que o código faz.

## Aprendizado

Normalização pode reduzir a fragmentação do vocabulário.

Entretanto, reduzir o vocabulário não significa automaticamente melhorar o classificador. O efeito real precisa ser confirmado experimentalmente.

## Decisão do projeto

Lowercase e tratamento de pontuação passam a ser candidatos para o pipeline de preparação textual.

A decisão final será avaliada durante os experimentos do baseline.

## Como explicar em vídeo

> “O vocabulário bruto tinha 4.518 tokens distintos. Apenas converter para lowercase reduziu esse número em cerca de 8,5%. Quando também tratamos pontuação nas extremidades dos tokens, chegamos a 2.452. Isso mostrou que capitalização e pontuação fragmentavam significativamente o vocabulário.”
