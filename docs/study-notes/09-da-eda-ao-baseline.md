# 09 — Da EDA ao baseline

## EDA não é uma etapa isolada

O objetivo da EDA não é apenas produzir estatísticas interessantes.

Ela deve influenciar decisões posteriores.

No projeto, a sequência construída foi:

```text
Validação
   ↓
Distribuição das classes
   ↓
Comprimento dos textos
   ↓
Percentis
   ↓
IQR
   ↓
Vocabulário
   ↓
Tokens frequentes
   ↓
Decisões de preprocessing
   ↓
TF-IDF
   ↓
Logistic Regression
```

## Evidências produzidas

### Classes

Existe diferença entre frequências, mas ainda não há evidência suficiente para aplicar balanceamento.

### Comprimento

A maioria das mensagens é curta, mas existe uma cauda de mensagens maiores.

### IQR

Foram encontrados possíveis outliers, porém eles não foram considerados automaticamente inválidos.

### Vocabulário

Lowercase e tratamento de pontuação reduzem significativamente a fragmentação observada.

### Stopwords

A alta frequência de palavras funcionais justifica um experimento, não uma remoção automática.

## Baseline planejado

A primeira estratégia é:

```text
Texto
  ↓
TF-IDF
  ↓
Logistic Regression
  ↓
Intent
```

O baseline estabelece um ponto de referência mensurável.

Modelos mais complexos só poderão ser avaliados adequadamente se existir uma referência simples e reproduzível.

## Aprendizado

EDA e modelagem formam uma cadeia de decisões.

Uma boa pergunta para cada transformação é:

> “Qual evidência dos dados justifica esta escolha?”

## Como explicar em vídeo

> “Nossa EDA não foi feita apenas para descrever o dataset. Cada análise prepara uma decisão do baseline. Agora conseguimos iniciar TF-IDF e Logistic Regression sabendo quais hipóteses de preprocessing precisam ser testadas e quais transformações ainda não têm justificativa para serem aplicadas.”
