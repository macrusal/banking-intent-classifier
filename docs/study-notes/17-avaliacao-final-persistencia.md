# Study Note 17 — Avaliação final e persistência do modelo

## Objetivo

Treinar a configuração selecionada do baseline utilizando todo o conjunto oficial de treinamento do BANKING77, avaliar seu desempenho no conjunto oficial de teste e persistir o Pipeline para reutilização.

## Configuração do modelo

- Vetorização: `TfidfVectorizer(stop_words=None)`
- Classificador: `LogisticRegression(max_iter=1000)`
- Pipeline: scikit-learn
- Persistência: joblib

## Dados utilizados

| Conjunto | Registros |
|---|---:|
| Treinamento oficial | 10.003 |
| Teste oficial | 3.080 |

A configuração foi selecionada previamente por validação interna. O conjunto oficial de teste não foi utilizado para selecionar hiperparâmetros.

## Resultados oficiais

| Métrica | Resultado |
|---|---:|
| Accuracy | 0.8769 |
| Macro F1 | 0.8769 |
| Weighted F1 | 0.8769 |

Esses resultados correspondem à avaliação oficial da configuração congelada, treinada com todos os registros do conjunto oficial de treinamento.

## Reprodutibilidade

Instalar ou sincronizar as dependências:

```bash
uv sync
```

Executar o treinamento e a avaliação:

```bash
uv run python -m banking_intent_classifier.final_training
```

Executar os testes automatizados:

```bash
uv run pytest
```

Resultado confirmado: **22 testes aprovados**.

## Artefato gerado

`artifacts/baseline_pipeline.joblib`

O artefato contém o Pipeline completo, incluindo vetorização TF-IDF e classificador treinado.

O diretório `artifacts/` está excluído do versionamento pelo `.gitignore`.

Arquivos joblib devem ser carregados apenas de fontes confiáveis.

## Arquitetura

- `ModelTrainer`: criação e treinamento do Pipeline.
- `ModelEvaluator`: cálculo das métricas.
- `ModelRepository`: persistência e carregamento do modelo.
- `final_training.py`: orquestração do treinamento e avaliação oficiais.

## Próximos passos

1. Disponibilizar o modelo por uma API de inferência.
2. Criar a execução em Docker.
3. Implementar a orquestração de treinamento com Apache Airflow.
4. Ampliar o relatório de avaliação com métricas por classe e matriz de confusão.