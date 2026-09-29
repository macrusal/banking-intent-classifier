# 07 — Data leakage e separação treino/teste

## O que verificamos?

Comparamos os textos presentes nos splits de treinamento e teste.

Resultado:

```text
Textos presentes em treino e teste: 0
```

## Por que isso importa?

O conjunto de teste deve representar dados que o modelo não utilizou durante o aprendizado.

Se a mesma mensagem aparecesse no treino e no teste, o resultado poderia parecer melhor simplesmente porque o modelo já teria sido exposto àquela observação.

Esse tipo de contaminação é uma forma de **data leakage**.

## Aprendizado

Separar dados em treino e teste não garante, por si só, independência adequada.

É útil verificar possíveis sobreposições, duplicidades e outras formas pelas quais informação do teste poderia chegar ao treinamento.

## Limite desta verificação

A análise realizada procura **textos exatamente iguais** nos dois splits.

Ela não detecta automaticamente:

- paráfrases;
- mensagens quase duplicadas;
- relações semânticas muito próximas;
- outras formas mais sutis de leakage.

Portanto, o resultado reduz um risco específico, mas não prova ausência de toda forma possível de vazamento.

## Decisão do projeto

Como não existem textos exatamente compartilhados entre os splits, não foi necessária intervenção nessa etapa.

## Como explicar em vídeo

> “Também verificamos se havia mensagens idênticas em treino e teste. Encontramos zero sobreposição exata. Isso reduz o risco de uma forma simples de data leakage, embora não seja uma prova de ausência de todos os tipos de vazamento.”
