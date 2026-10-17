# Study Note 16 — Baseline formal de classificação textual

## Objetivo

Consolidar um baseline reproduzível para classificação de intenções bancárias utilizando o dataset BANKING77.

## O que é um baseline?

É um modelo de referência utilizado para avaliar se futuras melhorias realmente produzem resultados superiores.

Um baseline deve ser simples, mensurável e reproduzível.

## Arquitetura

O baseline utiliza um `Pipeline` do scikit-learn:

```text
Texto
  ↓
TfidfVectorizer(stop_words=None)
  ↓
LogisticRegression(max_iter=1000)
  ↓
Intenção bancária
```

O Pipeline mantém a transformação textual e o classificador integrados, garantindo que o pré-processamento ajustado no treinamento seja reutilizado durante a inferência.

## Separação dos dados

O conjunto oficial de treinamento do BANKING77 contém 10.003 registros.

Foi aplicada uma divisão estratificada:

- Treinamento interno: 8.002 registros.
- Validação interna: 2.001 registros.
- `random_state=42`.
- `validation_size=0.2`.

O conjunto oficial de teste, com 3.080 registros, não foi utilizado nesta etapa.

## Resultados

| Métrica | Resultado |
|---|---:|
| Accuracy | 0.8491 |
| Macro F1 | 0.8412 |
| Weighted F1 | 0.8482 |

As métricas reproduziram os resultados do experimento anterior com `stop_words=None`.

## Reprodutibilidade

Para executar o baseline:

```bash
uv run python -m banking_intent_classifier.baseline
```

Para executar os testes:

```bash
uv run pytest
```

Resultado da validação: 20 testes aprovados.

## Aprendizados

1. Um experimento compara hipóteses; o baseline consolida uma configuração de referência.
2. O Pipeline encapsula pré-processamento e classificação.
3. O TF-IDF deve ser ajustado exclusivamente com os dados de treinamento.
4. A validação interna permite avaliar o modelo sem utilizar prematuramente o conjunto oficial de teste.
5. Resultados usados na entrega precisam ter comandos documentados para reprodução.

## Próxima etapa

Treinar a configuração definida com o conjunto oficial de treinamento, avaliar no conjunto oficial de teste e persistir o modelo para utilização posterior na API e no Airflow.