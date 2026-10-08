# 15 — Reprodutibilidade de experimentos

## Contexto

Durante a evolução do projeto, o experimento de pré-processamento textual
já estava implementado e coberto por testes automatizados.

O experimento comparava duas configurações:

- `stop_words=None`;
- `stop_words="english"`.

As métricas obtidas também já estavam registradas na documentação.

Entretanto, existia uma diferença importante entre **ter o experimento
implementado** e **permitir que outra pessoa reproduza o experimento de
forma direta**.

## Problema identificado

O experimento era executado internamente por meio de
`TextPreprocessingExperiment`, mas não existia um ponto de entrada
público que pudesse ser chamado pelo terminal.

Isso significava que as métricas estavam documentadas, porém não havia
um comando simples que permitisse ao professor executar o projeto e
reproduzir esses resultados.

Essa situação levou à seguinte regra de desenvolvimento:

> Sempre que uma funcionalidade produzir um resultado utilizado na
> entrega, deve existir também um caminho versionado e documentado para
> reproduzir esse resultado.

## Solução

Foi criado um ponto de entrada específico para os experimentos:

```text
src/banking_intent_classifier/experiment.py
```

Esse módulo não implementa regras de Machine Learning.

Sua responsabilidade é apenas orquestrar os componentes existentes:

```text
load_banking77()
        │
        ▼
prepare_data()
        │
        ▼
compare()
        │
        ▼
ExperimentResult
        │
        ▼
apresentação das métricas
```

Dessa forma, responsabilidades como:

- criação do TF-IDF;
- treinamento do modelo;
- geração das previsões;
- cálculo das métricas;
- criação do split;

continuam nos componentes responsáveis por essas operações.

## Comando reproduzível

O experimento pode ser executado com:

```bash
uv run python -m banking_intent_classifier.experiment
```

## Resultado reproduzido

A execução produziu:

```text
Configuração: stop_words=None
Accuracy: 0.8491
Macro F1: 0.8412
Weighted F1: 0.8482

Configuração: stop_words=english
Accuracy: 0.8206
Macro F1: 0.8137
Weighted F1: 0.8198
```

Os resultados reproduzem as métricas anteriormente obtidas durante o
experimento.

Nas condições avaliadas, `stop_words=None` permaneceu como a
configuração escolhida para o baseline.

## Preservação do conjunto oficial de teste

O comando utiliza o split interno estratificado criado a partir do
conjunto oficial de treinamento.

O conjunto oficial de teste do BANKING77, contendo 3.080 registros,
continua sem participar das decisões de configuração do modelo.

Isso evita utilizar o conjunto destinado à avaliação final durante a
seleção das configurações do baseline.

## Teste do ponto de entrada

Também foi criado um teste automatizado para verificar a orquestração
realizada pelo novo entrypoint.

O teste utiliza mocks para evitar:

- download do BANKING77;
- treinamento real do modelo;
- execução desnecessária do TF-IDF.

O objetivo desse teste não é recalcular as métricas do modelo, pois os
componentes responsáveis pelo experimento já possuem seus próprios
testes.

O teste verifica se o entrypoint:

1. carrega o dataset;
2. prepara os dados;
3. executa a comparação;
4. apresenta os resultados.

Com essa inclusão, a suíte passou de:

```text
17 testes
```

para:

```text
18 testes
```

A suíte completa foi executada com:

```bash
uv run pytest
```

Resultado observado:

```text
18 passed
```

## Aprendizado

Reprodutibilidade não significa apenas possuir código capaz de realizar
um experimento.

Uma funcionalidade utilizada como evidência em uma entrega deve possuir
um caminho claro para que outra pessoa consiga executar a mesma operação
e verificar seus resultados.

O fluxo adotado no projeto passa a ser:

```text
Funcionalidade
      │
      ▼
Implementação
      │
      ▼
Testes
      │
      ▼
Resultado / evidência
      │
      ▼
Comando reproduzível
      │
      ▼
Documentação
      │
      ▼
Commit / Pull Request
```

Esse padrão será aplicado às próximas etapas do projeto, incluindo o
baseline formal, avaliação final, API, containerização, automação,
monitoramento e otimização.