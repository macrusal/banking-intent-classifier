# Split Estratificado e Conjunto de Validação

## Contexto

O dataset BANKING77 disponibiliza originalmente dois conjuntos:

- `train`: 10.003 registros;
- `test`: 3.080 registros.

Durante a construção do primeiro modelo surgiu a necessidade de comparar diferentes configurações de pré-processamento, inicialmente:

```text
TF-IDF
├── stop_words=None
└── stop_words="english"
```

Utilizar diretamente o conjunto oficial de teste para escolher entre essas configurações seria metodologicamente inadequado.

O conjunto de teste deve permanecer reservado para a avaliação final do modelo.

---

## Por que não escolher a configuração usando o conjunto de teste?

O conjunto de teste deve representar dados que o processo de desenvolvimento ainda não utilizou para tomar decisões.

Se comparássemos:

```text
stop_words=None
        ↓
    test set
        ↓
    Macro F1

versus

stop_words="english"
        ↓
    test set
        ↓
    Macro F1
```

e escolhêssemos a configuração com maior resultado, o conjunto de teste estaria participando indiretamente do processo de desenvolvimento.

Nesse caso, estaríamos ajustando uma decisão do modelo com base no próprio conjunto que deveria fornecer a avaliação final.

Isso pode produzir uma estimativa excessivamente otimista da capacidade de generalização do modelo.

---

## Estratégia adotada

O conjunto `train` original do BANKING77 será dividido em:

```text
BANKING77
│
├── train — 10.003 registros
│      │
│      ├── treino interno (~80%)
│      │
│      └── validação (~20%)
│
└── test — 3.080 registros
       │
       └── preservado para avaliação final
```

O conjunto de validação será utilizado para comparar alternativas durante o desenvolvimento.

Por exemplo:

```text
                BANKING77 train
                       │
                       ▼
             DatasetSplitter
                       │
              ┌────────┴────────┐
              ▼                 ▼
        treino interno       validação
              │                 │
              ▼                 │
           TF-IDF               │
              │                 │
              ▼                 │
    Logistic Regression         │
              │                 │
              └──── predict ────┘
                       │
                       ▼
                    métricas
                       │
                       ▼
              decisão experimental
```

Somente depois de escolhermos a configuração do modelo utilizaremos o conjunto oficial `test`.

---

## Estratificação

O BANKING77 possui 77 classes.

Uma divisão puramente aleatória poderia alterar a distribuição das classes entre treino e validação.

Por isso foi utilizado:

```python
train_test_split(
    texts,
    labels,
    test_size=validation_size,
    random_state=random_state,
    stratify=labels,
)
```

O parâmetro:

```python
stratify=labels
```

faz com que a divisão procure preservar a proporção das classes nos conjuntos resultantes.

Conceitualmente:

```text
dataset original
│
├── classe A ───────────────┐
├── classe B ───────────────┤
├── classe C ───────────────┤
└── ...                     │
                            ▼
                     stratified split
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
            treino                    validação
       proporções similares       proporções similares
```

Isso é particularmente importante em classificação multiclasse.

---

## Reprodutibilidade

Outro requisito importante do experimento é que a divisão dos dados possa ser reproduzida.

Foi utilizado:

```python
random_state=42
```

Assim, mantendo:

- os mesmos dados;
- a mesma ordem dos dados;
- os mesmos parâmetros;
- o mesmo `random_state`;

a divisão pode ser reproduzida.

Isso é importante porque queremos comparar mudanças no modelo, e não mudanças aleatórias na composição dos conjuntos.

Sem essa precaução poderíamos ter:

```text
experimento A
split aleatório #1
        ↓
Macro F1 = X

experimento B
split aleatório #2
        ↓
Macro F1 = Y
```

Nesse cenário não saberíamos se a diferença ocorreu por causa da configuração analisada ou simplesmente porque os dados foram divididos de maneira diferente.

Com um split reproduzível:

```text
mesmo split
    │
    ├── configuração A
    │
    └── configuração B
            │
            ▼
comparação controlada
```

---

## Implementação

Foi criada a classe:

```text
application/
└── dataset_splitter.py
```

Sua responsabilidade é exclusivamente criar os conjuntos internos de treino e validação.

A implementação utiliza:

```python
DatasetSplitter.split(...)
```

com:

```text
validation_size = 0.2
random_state    = 42
stratify        = labels
```

Essa separação evita que a lógica de particionamento seja misturada com:

- carregamento do dataset;
- vetorização TF-IDF;
- treinamento;
- avaliação;
- apresentação dos resultados.

---

## Testes automatizados

Foram criados dois testes.

### 1. Estratificação

O primeiro verifica se a distribuição das classes é preservada.

Dataset artificial:

```text
20 registros

classe 0 → 10
classe 1 → 10
```

Com validação de 20%:

```text
treino
├── classe 0 → 8
└── classe 1 → 8

validação
├── classe 0 → 2
└── classe 1 → 2
```

O teste utiliza `Counter` para verificar a distribuição das classes.

---

### 2. Reprodutibilidade

O segundo teste executa o split duas vezes utilizando:

```python
random_state=42
```

e verifica:

```python
assert first_split == second_split
```

Isso confirma que a divisão utilizada no experimento é reproduzível.

---

## Resultado dos testes

Execução:

```bash
uv run pytest tests/application/test_dataset_splitter.py -v
```

Resultado:

```text
test_should_create_stratified_train_and_validation_sets PASSED
test_should_create_reproducible_split PASSED

2 passed
```

---

## Decisão para o projeto

A estratégia adotada será:

```text
BANKING77 train
       │
       ▼
split estratificado
       │
       ├── treino interno
       │       │
       │       └── fit
       │
       └── validação
               │
               └── comparação experimental

BANKING77 test
       │
       └── avaliação final
```

O conjunto oficial de teste não será utilizado para escolher:

- remoção ou não de stopwords;
- configurações do TF-IDF;
- hiperparâmetros;
- outras decisões tomadas durante os experimentos.

---

## Relação com Data Leakage

Data leakage não ocorre apenas quando uma coluna contém diretamente informação do target.

Também precisamos evitar que informações do conjunto de avaliação influenciem decisões tomadas durante o desenvolvimento.

Por isso:

```text
Treino
   ↓
aprendizado

Validação
   ↓
decisões de desenvolvimento

Teste
   ↓
avaliação final
```

Essa separação reduz o risco de obter métricas artificialmente otimistas.

---

## Aprendizado principal

O split dos dados não é apenas uma operação técnica.

Ele faz parte do desenho experimental.

Neste projeto queremos responder perguntas como:

> Remover stopwords melhora a classificação das 77 intents?

Para responder corretamente, precisamos manter todas as outras condições tão constantes quanto possível.

O fluxo passa a ser:

```text
hipótese
   ↓
split reproduzível
   ↓
experimento controlado
   ↓
métricas de validação
   ↓
comparação
   ↓
decisão baseada em evidências
   ↓
avaliação final no test
```

Essa estratégia será utilizada nos próximos experimentos do projeto.