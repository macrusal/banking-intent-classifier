# Exportação ONNX e benchmark de inferência

Este documento concentra a exportação do classificador BANKING77 para ONNX, a verificação de equivalência com o Scikit-learn, o benchmark de desempenho, a reprodução e as limitações da comparação.

## Objetivo e escopo

- Exportar o `Pipeline` treinado (TF-IDF + `LogisticRegression`) para ONNX.
- Verificar se o modelo ONNX reproduz as predições do Scikit-learn no split oficial de teste e se o mapeamento das classes é preservado.
- Medir latência p50/p95/p99, throughput individual e em lote, e o tamanho dos artefatos, registrando as condições do ambiente.

**Fora do escopo desta etapa:** servir o modelo ONNX pela API FastAPI, empacotá-lo na imagem Docker e incluir a exportação na DAG do Airflow. A API continua usando o `.joblib`.

## Estado confirmado em 24/10/2026

| Item | Resultado |
| :--- | :--- |
| Concordância Scikit-learn × ONNX (split `test`, 3.080 amostras) | **100%** (3.080/3.080), **0 divergências**, nas 5 execuções |
| Métricas dos dois modelos | `accuracy=0.8769480519480519`, `macro_f1=0.8768846181655345`, `weighted_f1=0.8768846181655345` |
| Mapeamento de classes | 77 classes, `classes_ == 0..76`, nomes iguais aos do dataset |
| Latência individual (p50) | Scikit-learn 0,59–0,62 ms; ONNX 0,088–0,093 ms |
| Throughput em lote | Mesma ordem de grandeza; ONNX entre 1,2% e 9,0% acima |
| Tamanho | `.joblib` 1.479.476 bytes; `.onnx` 942.678 bytes (36,3% menor) |

**SHA-256 dos artefatos medidos na execução 5:**

| Artefato | Bytes | SHA-256 |
| :--- | ---: | :--- |
| `artifacts/baseline_pipeline.joblib` | 1.479.476 | `8eb8f85fd48c326ea80a8a179f0fe4e4e37f310cf2967e572fc0c6e8e2285514` |
| `artifacts/baseline_pipeline.onnx` | 942.678 | `316c06e6cc753d882cc2d2279b50f06321bebe9a7613906b1ea233b28a18f354` |
| `artifacts/label_mapping.json` | 2.036 | `2a0729c0d558057bbd2a1e6b690e09c37be565d6278f18603df8b3d602fa4bc7` |

O `.joblib` foi gerado novamente em 24/10/2026 com `final_training` no ambiente descrito abaixo. As métricas são iguais às da execução Airflow de 22/10/2026, mas o hash difere do registrado em [`operacao-airflow.md`](operacao-airflow.md), porque a serialização pickle varia entre versões do Python (aquela geração usou Python 3.14). O `label_mapping.json` é idêntico.

## Ambiente da medição

| Item | Valor |
| :--- | :--- |
| Sistema | macOS 15.7.9, `x86_64` |
| Processador | Intel Core i9-9980HK @ 2,40 GHz, 8 núcleos físicos / 16 lógicos (anotado com `sysctl -n machdep.cpu.brand_string`) |
| Memória | 32 GiB |
| Python | 3.12.2 |
| Pacotes | `scikit-learn 1.9.1`, `numpy 2.5.3`, `onnxruntime 1.23.2`, `skl2onnx 1.20.0`, `onnx 1.23.2` |
| Threads | Padrão de cada biblioteca; `OMP_NUM_THREADS` e `MKL_NUM_THREADS` não definidos |
| Execution provider | `CPUExecutionProvider` |

O relatório JSON registra automaticamente sistema, arquitetura, CPUs lógicas, Python, versões e variáveis de threads. O modelo do processador não é coletado pelo código (`platform.processor()` retorna apenas `i386` no macOS) e deve ser anotado manualmente.

## Reprodução

### Pré-requisitos

- `uv` e Python 3.12, como no CI.
- Acesso ao Hugging Face Hub ou cache local do dataset `PolyAI/banking77` (revisão `refs/pr/6`). O aviso sobre `HF_TOKEN` ausente não impede a execução.
- Grupo opcional de dependências `onnx`, que não faz parte da imagem da API:

```bash
uv sync --python 3.12 --group onnx
uv run --group onnx python -c "import skl2onnx, onnxruntime; print(skl2onnx.__version__, onnxruntime.__version__)"
```

### Comandos

```bash
# 1. Gerar o modelo e o mapeamento de classes
uv run python -m banking_intent_classifier.final_training

# 2. Exportar para ONNX, verificar equivalência e executar o benchmark
uv run --group onnx python -m banking_intent_classifier.onnx_benchmark
```

| Entrada | Saída |
| :--- | :--- |
| `artifacts/baseline_pipeline.joblib`, `artifacts/label_mapping.json`, split `test` do BANKING77 | `artifacts/baseline_pipeline.onnx`, `artifacts/onnx_benchmark.json` e resumo no terminal |

Os artefatos ficam em `artifacts/`, ignorado pelo Git, e são sobrescritos a cada execução. A execução levou cerca de 9 segundos na máquina descrita.

### Verificação

```bash
# Hashes dos artefatos
shasum -a 256 artifacts/baseline_pipeline.joblib artifacts/baseline_pipeline.onnx artifacts/label_mapping.json

# Equivalência e parâmetros registrados
uv run python -c "import json; r = json.load(open('artifacts/onnx_benchmark.json')); print(r['equivalence']['agreement_rate'], r['equivalence']['mismatch_count'], r['parameters'])"
```

Resultado esperado: `agreement_rate` igual a `1.0` e `mismatch_count` igual a `0`. O hash do `.onnx` só coincide com o da tabela se o `.joblib` também coincidir; um novo treinamento em outro ambiente pode gerar outro `.joblib` com as mesmas métricas.

**Determinismo da exportação entre processos:**

```bash
for i in 1 2 3; do
  PYTHONHASHSEED=random uv run --group onnx python -c "from banking_intent_classifier.infrastructure.model_repository import ModelRepository; from banking_intent_classifier.infrastructure.onnx_model_repository import OnnxModelRepository; OnnxModelRepository.export(ModelRepository.load('artifacts/baseline_pipeline.joblib'), 'artifacts/export_check.onnx')"
  shasum -a 256 artifacts/export_check.onnx
done
```

Os três hashes devem ser iguais entre si e ao de `artifacts/baseline_pipeline.onnx`. O arquivo `artifacts/export_check.onnx` pode ser removido depois da conferência.

### Testes

```bash
uv run --group onnx pytest tests/test_onnx_model_repository.py tests/test_onnx_benchmark.py tests/application/test_onnx_prediction_service.py tests/application/test_model_equivalence.py tests/application/test_inference_benchmark.py -v
uv run --group onnx pytest
```

Os testes não acessam a rede nem dependem dos artefatos reais. Sem o grupo `onnx`, os testes que exigem `onnxruntime` e `skl2onnx` são ignorados via `pytest.importorskip`; os demais continuam executando. O job `tests` do CI instala o grupo (`uv sync --frozen --python 3.12 --group onnx`), portanto todos executam no GitHub Actions.

## Fluxo implementado

```text
baseline_pipeline.joblib ──► ModelRepository.load
label_mapping.json ───────► LabelRepository.load
                               │
                               ▼
              ModelEquivalenceChecker.check_label_mapping
              (+ nomes do dataset == label_mapping.json)
                               │
                               ▼
     OnnxModelRepository.export ──► baseline_pipeline.onnx
                               │
                               ▼
   PredictionService (sklearn) │ OnnxPredictionService (ONNX Runtime)
                               ▼
     ModelEquivalenceChecker.compare  →  equivalência e métricas
     InferenceBenchmark.measure       →  latência e throughput
                               │
                               ▼
                    onnx_benchmark.json
```

| Componente | Camada | Responsabilidade |
| :--- | :--- | :--- |
| `infrastructure/onnx_model_repository.py` | Infraestrutura | Conversão com `skl2onnx`, gravação e carregamento da `InferenceSession` |
| `application/onnx_prediction_service.py` | Aplicação | `predict` e `predict_batch` com o mesmo contrato e validação do `PredictionService` |
| `application/model_equivalence.py` | Aplicação | Concordância, divergências, métricas e conferência das classes |
| `application/inference_benchmark.py` | Aplicação | Aquecimento, latências, throughput e coleta do ambiente |
| `onnx_benchmark.py` | Ponto de entrada | Orquestração, hashes dos artefatos e relatório JSON |

## Metodologia do benchmark

| Parâmetro | Valor | Observação |
| :--- | :--- | :--- |
| Textos | 3.080 (split `test` completo) | Mesmos textos para os dois modelos |
| Aquecimento | 100 chamadas individuais | Não entram nas medições |
| Latência individual | 1 chamada por texto, `time.perf_counter` | Scikit-learn via `PredictionService.predict`, caminho atual da API; ONNX via `OnnxPredictionService.predict` |
| Lote | `batch_size=256`, 5 repetições | Scikit-learn via `pipeline.predict`; ONNX via `predict_batch` |
| Ordem | Scikit-learn, depois ONNX Runtime | Fixa e registrada em `parameters.execution_order` |
| Percentis | `numpy.percentile` (interpolação linear) | Em milissegundos |

## Resultados das 5 execuções (24/10/2026, UTC)

| # | Horário | Modelo | p50 (ms) | p95 (ms) | p99 (ms) | Individual (req/s) | Lote (textos/s) |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| 1 | 11:24:42 | Scikit-learn | 0,6193 | 0,8667 | 1,1150 | 1.510,5 | 106.004,9 |
| | | ONNX Runtime | 0,0908 | 0,1681 | 0,2228 | 9.868,4 | 108.911,1 |
| 2 | 11:25:46 | Scikit-learn | 0,5870 | 0,7236 | 0,8160 | 1.625,1 | 103.633,5 |
| | | ONNX Runtime | 0,0902 | 0,1610 | 0,2067 | 9.994,2 | 107.556,9 |
| 3 | 11:25:55 | Scikit-learn | 0,6183 | 0,9308 | 1,0930 | 1.517,1 | 107.478,9 |
| | | ONNX Runtime | 0,0932 | 0,1747 | 0,2150 | 9.508,0 | 109.391,5 |
| 4 | 11:28:41 | Scikit-learn | 0,5928 | 0,7133 | 0,8454 | 1.625,7 | 104.486,6 |
| | | ONNX Runtime | 0,0931 | 0,1525 | 0,1959 | 10.028,7 | 113.843,7 |
| 5 | 11:43:53 | Scikit-learn | 0,5946 | 0,7644 | 0,9153 | 1.594,2 | 109.282,2 |
| | | ONNX Runtime | 0,0879 | 0,1645 | 0,2167 | 10.157,0 | 110.576,2 |

| Métrica | Scikit-learn (faixa) | ONNX Runtime (faixa) | Razão sklearn ÷ ONNX |
| :--- | ---: | ---: | ---: |
| p50 | 0,5870–0,6193 ms | 0,0879–0,0932 ms | 6,4×–6,8× |
| p95 | 0,7133–0,9308 ms | 0,1525–0,1747 ms | 4,5×–5,3× |
| p99 | 0,8160–1,1150 ms | 0,1959–0,2228 ms | 3,9×–5,1× |
| Throughput individual | 1.510,5–1.625,7 req/s | 9.508,0–10.157,0 req/s | ONNX 6,1×–6,5× maior |
| Throughput em lote | 103.634–109.282 textos/s | 107.557–113.844 textos/s | ONNX 1,2%–9,0% maior |

As execuções 1 a 3 usaram uma exportação com metadados não determinísticos (ver incidentes); o grafo de cálculo era o mesmo e a equivalência foi de 100% em todas. O hash definitivo é o da execução 5.

## Interpretação e limitações

**Sustentado pelas medições, nesta máquina e neste ambiente:**

- O modelo ONNX reproduziu exatamente as predições do Scikit-learn nos 3.080 textos do teste oficial.
- Na inferência individual, o ONNX Runtime apresentou latência de 4 a 7 vezes menor nos percentis medidos, de forma consistente nas 5 execuções.
- O artefato ONNX ocupa cerca de 36% menos espaço que o `.joblib`.

**Não sustentado pelas medições:**

- **Ganho em lote:** o ONNX ficou à frente nas 5 execuções, mas a diferença variou de 1,2% a 9,0% e as faixas se sobrepõem. Trata-se de vantagem pequena e instável, não demonstrada estatisticamente.
- **Outros ambientes:** os números não se transferem automaticamente para Linux (CI, Docker) ou nuvem.
- **Origem do ganho individual:** não foi isolado quanto vem das threads padrão do ONNX Runtime e quanto vem do custo fixo de chamada do Scikit-learn por requisição.
- **API:** o benchmark mede o modelo isolado, sem HTTP nem serialização JSON; o ganho percebido em `/predict` não foi medido.
- **Tamanho:** compara artefato com artefato; o `.joblib` é um pickle de objetos Python e o `.onnx` é um grafo serializado.
- **Ordem fixa:** o Scikit-learn é sempre medido primeiro; o aquecimento reduz, mas não elimina, efeitos de ordem.

## Decisões e incidentes

| Decisão ou incidente | Diagnóstico e consequência |
| :--- | :--- |
| Grupo opcional `onnx` em `pyproject.toml` | `skl2onnx` e `onnxruntime` não entram na imagem da API (`--no-dev`) nem no `uv sync` padrão. Quem reproduz o benchmark usa `--group onnx`. |
| `onnxruntime 1.31.0` sem wheel para macOS Intel | O `uv add` falhou em `macosx_15_0_x86_64`. Adicionado `tool.uv.required-environments` para macOS `x86_64`. |
| Resolução dividida por plataforma | Com `required-environments`, o `uv` resolveu `1.23.2` no macOS Intel e `1.31.0` nas demais plataformas. Para manter a mesma versão em todos os ambientes do benchmark, a restrição foi fixada em `onnxruntime>=1.23.2,<1.24`. |
| Entrada `StringTensorType([None, 1])` e ZipMap desativado | O modelo recebe lotes de textos e retorna `label` (`int64`) e `probabilities` (`float`) como tensores, sem lista de dicionários. |
| Hash do `.onnx` diferente a cada exportação | O `skl2onnx` gera um UUID como `graph.name` quando nenhum nome é informado. Corrigido com `GRAPH_NAME = "banking77_intent_classifier"`. |
| Hash ainda diferente entre processos | A ordem de `opset_import` vem de um `set` de strings e varia com o `PYTHONHASHSEED`. Corrigido ordenando os opsets por domínio antes de serializar; conferido com 3 exportações em processos separados. |
| CI | O job `tests` instala o grupo `onnx`; os jobs `lint` e `docker-build` não foram alterados. |

## Próximos passos possíveis

Não implementados nesta etapa e dependentes de decisão:

- servir o modelo ONNX na API e medir a latência ponta a ponta de `/predict`;
- repetir o benchmark em Linux (Docker ou CI) para comparar ambientes;
- fixar o número de threads do ONNX Runtime para isolar a origem do ganho individual.
