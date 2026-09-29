# 08 — SRP e evolução da arquitetura

## Como o problema apareceu

O projeto começou pequeno e o `DatasetService` era suficiente para concentrar as primeiras análises.

Com a evolução da EDA, ele passou a cuidar de:

- resumo estrutural;
- distribuição de classes;
- estatísticas de comprimento;
- percentis;
- IQR e possíveis outliers;
- características do corpus;
- normalização exploratória;
- frequência de tokens.

Isso cria diferentes motivos para a mesma classe mudar.

## Um sinal concreto

Durante a revisão foi encontrada uma duplicação de `summarize_text_length()` dentro de `DatasetService`.

O programa continuava funcionando porque a definição posterior substituía a anterior em Python, mas a duplicação é um sinal de perda de clareza causada pelo crescimento da classe.

## SRP não significa “classe pequena”

O **Single Responsibility Principle** não determina uma quantidade máxima de linhas ou métodos.

A pergunta mais útil é:

> “Esta classe possui mais de um motivo conceitual para mudar?”

Por exemplo, `ConsoleReporter` possui vários métodos, mas todos pertencem à mesma responsabilidade: apresentação dos resultados no console.

Já `DatasetService` reúne análises que evoluem por razões diferentes.

## Refatoração planejada

Uma possível evolução é:

```text
application/
├── dataset_analyzer.py
├── class_distribution_analyzer.py
├── text_length_analyzer.py
└── corpus_analyzer.py
```

Responsabilidades:

- `DatasetAnalyzer`: estrutura e qualidade básica;
- `ClassDistributionAnalyzer`: distribuição das classes;
- `TextLengthAnalyzer`: comprimento, percentis e IQR;
- `CorpusAnalyzer`: vocabulário, normalização e frequências.

## Evitando o outro extremo

SRP não deve levar automaticamente a:

```text
uma classe para cada método
```

Isso poderia aumentar fragmentação e complexidade sem benefício real.

O objetivo é buscar **coesão**, não simplesmente aumentar o número de arquivos.

## Testes antes da refatoração

Antes de mover responsabilidades, a estratégia proposta é criar testes que capturem o comportamento atual.

Depois:

```text
comportamento atual
       ↓
      testes
       ↓
   refatoração
       ↓
      testes
       ↓
mesmo comportamento
```

## Aprendizado

Arquitetura não precisa nascer completa.

Ela pode evoluir à medida que responsabilidades reais aparecem no código.

## Como explicar em vídeo

> “A arquitetura inicial funcionou bem enquanto o projeto era pequeno. A própria evolução da EDA revelou novas responsabilidades. Em vez de antecipar abstrações, deixamos o código mostrar onde existiam motivos diferentes para mudança e só então planejamos a refatoração.”
