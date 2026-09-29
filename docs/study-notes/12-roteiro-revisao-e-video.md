# 12 — Roteiro de revisão e apresentação

Esta nota funciona como guia rápido para revisar a história técnica do projeto antes de uma apresentação ou gravação.

## 1. Qual problema estamos resolvendo?

Classificação automática de mensagens bancárias em uma das 77 intenções do BANKING77.

## 2. Por que validar antes de modelar?

Para confirmar que splits, colunas e registros possuem a estrutura esperada e identificar problemas de qualidade antes do treinamento.

## 3. O dataset está balanceado?

Não perfeitamente.

As classes variam de 35 a 187 exemplos no treinamento.

Não aplicamos balanceamento ainda porque queremos medir primeiro o impacto no baseline.

## 4. Como são as mensagens?

São predominantemente curtas:

- mediana: 10 palavras;
- P75: 13 palavras;
- P90: 22 palavras;
- máximo: 79 palavras.

Existe uma cauda à direita.

## 5. Encontramos outliers?

O IQR marcou:

- 1.038 mensagens por comprimento em caracteres;
- 930 por quantidade de palavras.

Mas não removemos esses registros.

### Frase-chave

> Outlier estatístico não é sinônimo de dado inválido.

## 6. O que aconteceu com o vocabulário?

```text
4.518 tokens únicos
        ↓ lowercase
4.136
        ↓ tratamento de pontuação
2.452
```

Isso mostrou fragmentação causada por capitalização e pontuação.

## 7. E as stopwords?

Muitas palavras funcionais aparecem entre os tokens mais frequentes.

Não serão removidas automaticamente.

Vamos comparar experimentalmente o baseline com e sem stopwords.

### Frase-chave

> Frequência alta não significa automaticamente irrelevância.

## 8. Houve data leakage?

Não foram encontrados textos exatamente iguais entre treino e teste.

Essa verificação reduz um tipo específico de leakage, mas não garante ausência de todas as formas possíveis.

## 9. Qual será o primeiro modelo?

```text
Texto → TF-IDF → Logistic Regression → Intent
```

O objetivo é estabelecer um baseline simples e mensurável.

## 10. O que aprendemos sobre arquitetura?

O crescimento da EDA fez o `DatasetService` acumular responsabilidades.

A próxima refatoração pretende separar:

- análise estrutural;
- distribuição das classes;
- comprimento;
- corpus.

### Frase-chave

> SRP não significa classe pequena; significa responsabilidade coesa.

## 11. Qual princípio resume as decisões?

```text
Observar
   ↓
formular hipótese
   ↓
experimentar
   ↓
medir
   ↓
decidir
```

### Frase-chave

> Medir antes de modificar.

## Roteiro curto para vídeo

> “O projeto começou pela validação do BANKING77 e evoluiu de forma incremental. Analisamos distribuição das classes, comprimento das mensagens, percentis, possíveis outliers, vocabulário e frequência dos tokens. Um ponto importante foi evitar decisões automáticas: não removemos mensagens longas apenas porque o IQR as marcou, não aplicamos balanceamento antes de medir o baseline e não removemos stopwords sem testar seu impacto. A EDA passou, portanto, a orientar as hipóteses que serão avaliadas com TF-IDF e Logistic Regression. Paralelamente, o crescimento do código mostrou a necessidade de revisar responsabilidades arquiteturais antes de iniciar a próxima fase.”
