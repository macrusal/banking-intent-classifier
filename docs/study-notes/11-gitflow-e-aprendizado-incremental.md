# 11 — GitFlow como diário técnico

## Estratégia adotada

O desenvolvimento foi dividido em pequenas branches de feature.

Cada incremento adiciona uma capacidade observável e registra seu histórico por commits e Pull Requests.

Fluxo:

```text
feature
   ↓
dev
   ↓
main
```

## Por que isso ajuda no aprendizado?

Uma branch não representa apenas uma mudança de código.

Ela pode representar uma pergunta técnica:

```text
feature de distribuição
→ Como as classes estão distribuídas?

feature de comprimento
→ Como são os textos?

feature de corpus
→ Como é o vocabulário?

refactor
→ As responsabilidades continuam coesas?
```

Isso transforma o histórico Git em uma linha do tempo do raciocínio do projeto.

## Nova prática: study notes

A partir deste ponto, cada feature relevante deve produzir:

```text
código
+
resultado
+
interpretação
+
decisão
+
nota de estudo
```

## Benefícios

- facilita revisão para apresentação;
- registra por que uma decisão foi tomada;
- reduz dependência de memória;
- cria material reutilizável para posts;
- melhora a explicação do projeto em entrevistas;
- ajuda professores e colaboradores a acompanhar a evolução.

## Ponto de atenção

Não é necessário criar documentação extensa para cada commit pequeno.

A nota deve existir quando houver um conceito, decisão ou aprendizado que mereça ser preservado.

## Como explicar em vídeo

> “Além do código, passamos a tratar o GitFlow como registro do aprendizado. Cada feature relevante responde uma pergunta sobre o problema e gera uma nota de estudo com os resultados e as decisões técnicas.”
