# 10 — Decisões orientadas por evidências

## Um padrão que surgiu no projeto

Durante a EDA, várias decisões poderiam ter sido tomadas automaticamente:

- classes desbalanceadas → balancear;
- outliers → remover;
- pontuação → remover;
- stopwords → remover;
- textos longos → truncar.

Optamos por não fazer isso.

## Estratégia adotada

Separar três conceitos:

```text
observação
    ↓
hipótese
    ↓
experimento
    ↓
decisão
```

### Exemplo: stopwords

Observação:

> palavras funcionais aparecem entre os tokens mais frequentes.

Hipótese:

> removê-las pode melhorar a representação.

Experimento:

> baseline com e sem stopwords.

Decisão:

> baseada nas métricas obtidas.

### Exemplo: outliers

Observação:

> cerca de 10% das mensagens ultrapassam limites definidos pelo IQR.

Hipótese:

> textos longos podem afetar o modelo.

Mas antes de removê-los verificamos o significado da observação: mensagens longas podem ser dados legítimos.

Decisão:

> preservar e reavaliar durante a modelagem.

## Aprendizado

Uma transformação de dados é uma decisão de modelagem.

Quanto mais transformações são aplicadas antecipadamente, maior o risco de apagar informação útil antes de medir seu valor.

## Regra de trabalho

Sempre que possível:

> **medir antes de modificar.**

## Valor profissional

Esse raciocínio é útil em entrevistas e apresentações porque demonstra que o pipeline não foi construído apenas pela aplicação mecânica de receitas de Machine Learning.

## Como explicar em vídeo

> “Uma das regras que adotamos foi medir antes de modificar. Encontrar um outlier, uma stopword ou um desbalanceamento não significa automaticamente aplicar uma correção. Primeiro buscamos entender o fenômeno e depois usamos experimentos e métricas para decidir.”
