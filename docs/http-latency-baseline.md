# Baseline de latência HTTP

Este documento registra a latência ponta a ponta de `POST /predict` medida contra a API em container Docker. É a baseline exigida na Etapa 1 do enunciado e a referência para os buckets do Histogram da instrumentação Prometheus.

O benchmark de [`onnx-benchmark.md`](onnx-benchmark.md) mede o modelo isolado. Aqui a medição inclui cliente HTTP, rede do Docker, validação Pydantic, inferência e serialização JSON da resposta.

## Estado confirmado em 26/10/2026

| Item | Resultado |
| :--- | :--- |
| Alvo | Imagem atual do `Dockerfile`, backend Scikit-learn (`.joblib`) |
| Requisições | 3.080 por execução (split `test` completo), 100 de aquecimento, 3 execuções |
| Latência p50 | 2,47–2,48 ms |
| Latência p95 | 3,08–3,19 ms |
| Latência p99 | 3,71–4,31 ms |
| Throughput sequencial | 387,2–391,4 req/s (1 cliente, sem concorrência) |

## Ambiente da medição

| Item | Valor |
| :--- | :--- |
| Host | macOS 15.7.9, `x86_64`, Intel Core i9-9980HK @ 2,40 GHz, 16 CPUs lógicas |
| Cliente | Python 3.12.2 no host, `http.client` da biblioteca padrão |
| Docker | Docker Desktop 29.1.5, VM `linux/amd64`, kernel `6.12.65-linuxkit`, 16 CPUs e ~7,65 GiB atribuídos à VM |
| Container | `python:3.12-slim`, `uvicorn` com 1 processo, sem limites de CPU ou memória no `docker run` |
| Threads | `OMP_NUM_THREADS` e `MKL_NUM_THREADS` não definidos |

**Artefatos copiados para a imagem:**

| Artefato | SHA-256 |
| :--- | :--- |
| `artifacts/baseline_pipeline.joblib` | `8eb8f85fd48c326ea80a8a179f0fe4e4e37f310cf2967e572fc0c6e8e2285514` |
| `artifacts/label_mapping.json` | `2a0729c0d558057bbd2a1e6b690e09c37be565d6278f18603df8b3d602fa4bc7` |

São os mesmos artefatos do benchmark ONNX de 24/10/2026.

## Reprodução

### Pré-requisitos

- `uv` e Python 3.12, Docker em execução e a porta 8000 livre.
- Artefatos em `artifacts/`. Se não existirem, gere-os com `final_training`, que precisa do Hugging Face Hub ou do cache local do dataset.
- O benchmark lê o split `test` do BANKING77 (`PolyAI/banking77`, revisão `refs/pr/6`), do cache local ou do Hub.
- Não precisa do grupo `onnx`.

### Comandos

```bash
# 1. Artefatos do modelo (somente se ainda não existirem)
uv run --frozen python -m banking_intent_classifier.final_training

# 2. Imagem e container da API
docker build -t banking-intent-classifier:baseline .
docker run -d --rm --name bic-baseline -p 8000:8000 banking-intent-classifier:baseline

# 3. Medição (repetir para obter várias execuções)
uv run --frozen python -m banking_intent_classifier.http_latency_benchmark --name sklearn

# 4. Encerramento
docker stop bic-baseline
```

**Opções do benchmark:**

| Opção | Padrão | Uso |
| :--- | :--- | :--- |
| `--base-url` | `http://localhost:8000` | Endereço da API |
| `--name` | `sklearn` | Rótulo do alvo, usado no relatório e no nome do arquivo |
| `--requests` | split `test` inteiro | Quantidade de requisições medidas |
| `--warmup` | `100` | Requisições de aquecimento, fora das medições |
| `--output` | `artifacts/http_latency_<name>.json` | Caminho do relatório |

| Entrada | Saída |
| :--- | :--- |
| API em execução e split `test` do BANKING77 | Relatório JSON em `artifacts/` (ignorado pelo Git) e resumo no terminal |

Nas execuções registradas abaixo, cada relatório foi gravado em um arquivo próprio com `--output artifacts/http_latency_sklearn_run<N>.json`. A janela medida de cada execução levou de 7,87 s a 7,96 s (`result.wall_time_s`); o tempo total de cada comando é maior, pois inclui o carregamento do dataset, as 100 requisições de aquecimento e a consulta ao `/health`, que ficam fora da medição.

As três execuções foram feitas na mesma instância do contêiner. Aguarde a API responder ao `/health` antes de medir — uma execução iniciada durante a subida do contêiner é interrompida com `RuntimeError`, por decisão de projeto, em vez de produzir medição inválida:

```bash
until curl -sf http://localhost:8000/health >/dev/null; do sleep 1; done
```

### Verificação

```bash
uv run python -c "import json; r = json.load(open('artifacts/http_latency_sklearn.json')); print(r['dataset']['samples'], r['parameters'], r['result'])"
```

O resultado esperado tem `samples` igual a `3080`, `concurrency` igual a `1`, e os percentis em `result`, em milissegundos.

### Testes

```bash
uv run --frozen pytest tests/application/test_http_latency_benchmark.py tests/test_http_prediction_client.py tests/test_http_latency_benchmark.py tests/application/test_inference_benchmark.py -v
```

Os testes não usam Docker nem a internet. O cliente HTTP é testado contra um servidor local efêmero em `127.0.0.1`. O dataset e a API são substituídos por objetos falsos.

## Metodologia

| Parâmetro | Valor | Observação |
| :--- | :--- | :--- |
| Requisições | 3.080 textos do split `test`, uma por texto | Mesmos textos do benchmark ONNX |
| Aquecimento | 100 requisições | Não entram nas medições |
| Concorrência | 1 cliente sequencial | Mede latência, não capacidade máxima |
| Conexão | Persistente (keep-alive) | Sem o custo de abrir uma conexão TCP por requisição |
| Cronômetro | `time.perf_counter`, do envio até a leitura completa do corpo | Visão do cliente |
| Validação | Respostas com status diferente de 200 interrompem a medição | Nenhuma requisição com erro entra na estatística |
| Percentis | `summarize_latencies` (`numpy.percentile`, interpolação linear) | Mesma função usada pelo benchmark ONNX |

## Resultados das 3 execuções (26/10/2026, UTC)

| # | Horário | Média (ms) | p50 (ms) | p95 (ms) | p99 (ms) | Mín (ms) | Máx (ms) | Throughput (req/s) |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 19:13:04 | 2,5823 | 2,4773 | 3,1935 | 4,3132 | 2,1467 | 10,2197 | 387,2 |
| 2 | 19:13:28 | 2,5540 | 2,4805 | 3,0777 | 3,7111 | 2,0924 | 5,5977 | 391,4 |
| 3 | 19:13:51 | 2,5683 | 2,4747 | 3,1809 | 3,9696 | 2,1461 | 6,4359 | 389,3 |

O `timestamp_utc` do relatório é coletado ao final da execução, não no início da medição.

## Interpretação e limitações

**O que as medições sustentam, nesta máquina:**

- A latência de `/predict` vista pelo cliente fica concentrada entre 2 e 3,2 ms. O p50 variou menos de 0,01 ms entre as execuções.
- A cauda é curta: o p99 ficou abaixo de 4,4 ms. O máximo isolado de 10,2 ms (execução 1) não se repetiu nas seguintes.
- **A primeira execução após subir o contêiner apresenta o máximo isolado cerca de duas vezes maior que as seguintes**, mesmo com as 100 requisições de aquecimento. O padrão se repetiu em duas sessões de medição independentes, com máximos de 13,4 ms e 10,2 ms na primeira execução contra 5,6–6,5 ms nas demais. A causa não foi investigada; o efeito aparece apenas no máximo isolado e não desloca os percentis.
- Os buckets padrão do `prometheus_client` começam em 5 ms. Com eles, praticamente todas as observações cairiam no primeiro bucket, o que confirma a restrição da tarefa 1.1.

**O que elas não sustentam:**

- **Custo do HTTP isolado.** O benchmark do modelo (p50 de ~0,6 ms) rodou no macOS nativo, e este rodou em Linux dentro da VM do Docker Desktop. A diferença de ~2 ms não pode ser atribuída só ao HTTP.
- **Rede do Docker Desktop.** No macOS, o encaminhamento de porta do host para a VM acrescenta um custo que não existe em Linux nativo nem em nuvem. A latência medida de dentro do servidor (Prometheus) tende a ser menor.
- **Carga concorrente.** Com 1 cliente sequencial, o throughput de ~389 req/s é o inverso da latência, não a capacidade da API.
- **Outros ambientes.** Os números não se transferem automaticamente para o CI ou para a nuvem.

## Recomendação para os buckets do Histogram (tarefa 1.1)

Os buckets precisam de resolução entre 2 e 5 ms, onde ficam o p50, o p95 e o p99 medidos, e de cobertura para picos e degradações. Ponto de partida, em segundos (convenção do Prometheus):

```text
0.001, 0.002, 0.0025, 0.003, 0.004, 0.005, 0.0075, 0.01, 0.025, 0.05, 0.1, 0.25
```

Isso corresponde a 1; 2; 2,5; 3; 4; 5; 7,5; 10; 25; 50; 100; 250 ms. Os buckets de 2, 3, 4 e 7,5 ms acrescentam resolução à sugestão inicial do plano, justamente na faixa medida. A decisão final é da tarefa 1.1, depois de ver se a latência medida dentro do servidor fica abaixo de 2 ms.

**Ponto de atenção para a tarefa 1.1:** o p50 medido (2,47–2,48 ms) fica imediatamente abaixo da fronteira do bucket de 2,5 ms. Uma deriva de 0,03 ms desloca a estimativa do p50 para o bucket seguinte e produz um salto no painel sem degradação real. Considere acrescentar um bucket em 2,25 ms ou deslocar o de 2,5 ms, decidindo com a latência coletada de dentro da rede do Compose.

**Decisão tomada em 26/10/2026:** a medição do lado servidor (média de 1,80–1,92 ms) deslocou o problema do p50 para o p95. As fronteiras finais usam passos de 0,25 ms entre 1 e 3 ms. Medições e justificativa estão em [`prometheus-instrumentation.md`](prometheus-instrumentation.md#calibração-dos-buckets).

## Componentes

| Componente | Camada | Responsabilidade |
| :--- | :--- | :--- |
| `application/inference_benchmark.py` | Aplicação | `summarize_latencies`: média, percentis, mínimo e máximo, compartilhados com o benchmark ONNX |
| `application/http_latency_benchmark.py` | Aplicação | Aquecimento e medição sequencial; recebe o envio como função, sem conhecer HTTP |
| `infrastructure/http_prediction_client.py` | Infraestrutura | Conexão persistente com `http.client`, `POST /predict`, `GET /health` e erro em status diferente de 200 |
| `http_latency_benchmark.py` | Ponto de entrada | Argumentos, leitura do dataset, conferência do `/health` e relatório JSON |
