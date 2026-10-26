# Instrumentação Prometheus da API

Este documento descreve as métricas expostas pela API em `GET /metrics`, as decisões de desenho da instrumentação e a calibração dos buckets do Histogram com a latência medida do lado servidor.

A baseline vista pelo cliente está em [`http-latency-baseline.md`](http-latency-baseline.md). Aqui a medição é a do próprio serviço, sem o caminho de rede entre o host e o contêiner.

## Métricas expostas

| Métrica | Tipo | Labels | Uso |
| :--- | :--- | :--- | :--- |
| `http_requests_total` | Counter | `endpoint`, `status_code` | Taxa de requisições e, filtrando `status_code`, taxa de erro |
| `http_request_duration_seconds` | Histogram | `endpoint` | Latência: `_bucket`, `_sum` e `_count` |

O `prometheus_client` também expõe as métricas padrão do processo (`process_*`, `python_gc_*`, `python_info`).

A taxa de erro não tem métrica própria. Ela deriva do Counter:

```promql
sum(rate(http_requests_total{status_code=~"5.."}[1m]))
  / sum(rate(http_requests_total[1m]))
```

## Decisões de desenho

| Decisão | Motivo |
| :--- | :--- |
| Middleware ASGI puro (`PrometheusMiddleware`), não decorators por endpoint | Cobre todas as rotas de uma vez e mantém `api.py` só com o registro do middleware e da rota |
| Duração medida do início da chamada ASGI até o envio da resposta | Inclui validação Pydantic, inferência e serialização JSON: o equivalente, no servidor, ao que o cliente mede, menos a rede |
| `endpoint` é o template da rota (`scope["route"].path`) | Paths arbitrários não criam séries novas. Requisições sem rota correspondente (404) ficam em `endpoint="unmatched"` |
| `GET /metrics` não é instrumentado | Com scrape a cada 5 s, ele poluiria a taxa de requisições e o Histogram do serviço |
| Exceção não tratada é registrada como `status_code="500"` | O `finally` do middleware registra a requisição mesmo quando a aplicação falha antes de responder |
| Registry padrão do `prometheus_client` | Um processo `uvicorn`. Com vários workers, seria preciso o modo multiprocesso, fora do escopo atual |

## Calibração dos buckets

### Método

O quantil estimado pelo Histogram (`histogram_quantile`) não foi usado para decidir as fronteiras. Ele é limitado pelas próprias fronteiras, e o raciocínio ficaria circular. Foram usados dois valores que não dependem dos buckets:

- **média exata:** `_sum / _count`;
- **distribuição:** contagem acumulada de cada bucket.

Cada execução do benchmark foi isolada por diferença entre dois snapshots do `/metrics`, um antes e outro depois. O delta contém 3.180 `POST /predict`: as 3.080 requisições medidas mais as 100 de aquecimento do próprio benchmark. Antes da primeira execução de cada sessão houve uma execução de aquecimento, descartada.

**Ambiente:** o mesmo de [`http-latency-baseline.md`](http-latency-baseline.md) (macOS Intel, Docker Desktop 29.1.5, imagem do `Dockerfile` com backend Scikit-learn e os mesmos artefatos).

### Rodada 1 — buckets provisórios (26/10/2026, 20:59–21:00 UTC)

Fronteiras: 1; 2; 2,5; 3; 4; 5; 7,5; 10; 25; 50; 100; 250 ms.

| Execução | Média servidor (ms) | Média cliente (ms) | ≤ 1 ms | ≤ 2 ms | ≤ 2,5 ms | ≤ 3 ms | ≤ 4 ms | ≤ 5 ms |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1,8339 | 2,5199 | 0,00% | 86,42% | 99,25% | 99,87% | 100% | 100% |
| 2 | 1,8591 | 2,5318 | 0,00% | 83,33% | 97,39% | 99,09% | 99,87% | 100% |
| 3 | 1,9237 | 2,6051 | 0,00% | 71,73% | 96,10% | 99,34% | 99,84% | 99,94% |

Diagnóstico:

- **Diferença cliente × servidor:** a média no servidor ficou entre 1,83 e 1,92 ms, cerca de 0,7 ms abaixo da média do cliente. Essa diferença é o caminho host → VM do Docker Desktop mais o cliente.
- **Faixa de 1 a 2 ms:** 72% a 86% das observações caíram num único bucket de 1 ms de largura. O p50 ficava ali dentro, sem nenhuma resolução.
- **Fronteira de 2,5 ms:** o ponto de atenção registrado na baseline (p50 do cliente encostado em 2,5 ms) não se aplica ao servidor, onde o p50 fica abaixo de 2 ms. A fronteira de 2,5 ms passou a encostar no **p95**: o acumulado em 2,5 ms foi de 96,1% a 99,25%, e na execução 3 ficou só 1,1 ponto acima de 95%. Com um bucket de 0,5 ms de largura, a estimativa do p95 do painel teria erro de até 0,5 ms.

### Rodada 2 — buckets finais (26/10/2026, 21:03 UTC)

Fronteiras: 0,5; 1; 1,25; 1,5; 1,75; 2; 2,25; 2,5; 2,75; 3; 4; 5; 7,5; 10; 25; 50; 100; 250 ms.

| Execução | Média servidor (ms) | Média cliente (ms) | ≤ 1,5 ms | ≤ 1,75 ms | ≤ 2 ms | ≤ 2,25 ms | ≤ 2,5 ms | ≤ 2,75 ms | ≤ 3 ms | ≤ 4 ms |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 1,8049 | 2,4685 | 0,03% | 44,69% | 89,34% | 98,11% | 99,21% | 99,47% | 99,75% | 100% |
| 5 | 1,8338 | 2,5010 | 0,00% | 39,37% | 86,35% | 96,45% | 98,74% | 99,37% | 99,62% | 100% |
| 6 | 1,8913 | 2,5630 | 0,00% | 31,04% | 75,72% | 93,18% | 97,86% | 99,09% | 99,62% | 99,97% |

Nas três execuções, os buckets até 1,25 ms ficaram vazios. Na execução 6 houve uma observação entre 5 e 7,5 ms.

### Decisão e justificativa

```text
0.0005, 0.001, 0.00125, 0.0015, 0.00175, 0.002, 0.00225, 0.0025, 0.00275, 0.003,
0.004, 0.005, 0.0075, 0.01, 0.025, 0.05, 0.1, 0.25
```

- **Passos de 0,25 ms entre 1 e 3 ms:** é onde fica toda a massa observada. O p50 cai entre 1,75 e 2 ms (acumulado de 31–45% em 1,75 ms e de 76–89% em 2 ms). O p95 cai entre 2 e 2,5 ms (acumulado de 93–98% em 2,25 ms). Com isso, o erro de interpolação do `histogram_quantile` fica limitado a 0,25 ms nos dois percentis do painel. Antes eram 1 ms no p50 e 0,5 ms no p95.
- **Fronteira de 2,5 ms:** foi mantida. O problema não era a fronteira em si, mas a largura do bucket ao redor do percentil. Com vizinhos em 2,25 e 2,75 ms, cruzar 2,5 ms produz uma variação de no máximo 0,25 ms na estimativa, não um salto.
- **O p95 cruzando 2,25 ms entre as execuções** (acima de 95% nas execuções 4 e 5, abaixo na 6) acompanha uma variação real: a média subiu de 1,80 para 1,89 ms. Não é efeito de fronteira.
- **1 ms e 1,25 ms:** mantidos, embora vazios nesta medição. Na 2.2 a API passará a servir ONNX, cujo modelo isolado é cerca de 0,5 ms mais rápido no p50 ([`onnx-benchmark.md`](onnx-benchmark.md)). Esses buckets dão resolução a essa faixa.
- **0,5 ms:** piso de segurança, sem evidência de que será ocupado. Os dois últimos itens são uma **previsão, não medição**, e devem ser reavaliados na 2.3 com o ONNX servido.
- **De 3 a 250 ms:** mantidos como reserva para degradação e picos. O máximo observado do lado do cliente foi de 14,1 ms.
- **Custo:** 18 fronteiras mais `+Inf` dão 19 séries `_bucket` por valor de `endpoint`, que tem poucos valores possíveis. Cardinalidade desprezível.

## Reprodução

### Testes

```bash
uv run --frozen pytest tests/presentation/test_metrics.py tests/presentation/test_api.py -v
uv run --frozen --group onnx pytest
```

Os testes usam modelo falso e não acessam rede nem Docker. Eles cobrem:
- formato e content type do `/metrics`;
- incremento do Counter e do Histogram após `POST /predict`;
- `status_code="422"` como label;
- agregação de rotas inexistentes em `unmatched`;
- exclusão do próprio `/metrics`.

### Verificação manual

```bash
docker build -t banking-intent-classifier:metrics .
docker run -d --rm --name bic-metrics -p 8000:8000 banking-intent-classifier:metrics
until curl -sf http://localhost:8000/health >/dev/null; do sleep 1; done

curl -s -X POST http://localhost:8000/predict -H 'Content-Type: application/json' -d '{"text":"I am still waiting on my card"}'
curl -s http://localhost:8000/metrics | grep -E '^http_request'
```

O esperado é `http_requests_total{endpoint="/predict",status_code="200"} 1.0` e as séries `http_request_duration_seconds_*` com `endpoint="/predict"`.

### Distribuição do lado servidor

```bash
# Aquecimento descartado
uv run --frozen python -m banking_intent_classifier.http_latency_benchmark --name warm --output artifacts/http_latency_warm.json

curl -s http://localhost:8000/metrics > artifacts/metrics_before.txt
uv run --frozen python -m banking_intent_classifier.http_latency_benchmark --name metrics --output artifacts/http_latency_metrics.json
curl -s http://localhost:8000/metrics > artifacts/metrics_after.txt

uv run --frozen python - <<'EOF'
from prometheus_client.parser import text_string_to_metric_families

def histogram(path):
    values = {}
    for family in text_string_to_metric_families(open(path).read()):
        if family.name == "http_request_duration_seconds":
            for sample in family.samples:
                if sample.labels.get("endpoint") == "/predict":
                    values[(sample.name, sample.labels.get("le"))] = sample.value
    return values

before = histogram("artifacts/metrics_before.txt")
after = histogram("artifacts/metrics_after.txt")
delta = {key: after[key] - before.get(key, 0.0) for key in after}
count = delta[("http_request_duration_seconds_count", None)]
total = delta[("http_request_duration_seconds_sum", None)]
print(f"count={count:.0f} media={total / count * 1000:.4f} ms")
for (name, le), value in sorted(
    ((k, v) for k, v in delta.items() if k[0].endswith("_bucket")),
    key=lambda item: float(item[0][1]),
):
    print(f"le={le:>8} acumulado={value:6.0f} ({value / count:7.2%})")
EOF

docker stop bic-metrics
```

Os arquivos em `artifacts/` são ignorados pelo Git.

## Limitações

- **Ambiente:** as medições valem para Docker Desktop no macOS Intel. Em Linux nativo ou na nuvem, a latência do servidor pode mudar.
- **Concorrência:** a carga foi de 1 cliente sequencial. Sob concorrência, a cauda tende a crescer; os buckets de 3 a 250 ms existem para isso.
- **Aquecimento no delta:** o delta inclui as 100 requisições de aquecimento do benchmark, cerca de 3% da amostra, depois de uma execução inteira de aquecimento descartada.
- **Faixa abaixo de 1,25 ms:** os buckets dessa faixa dependem da 2.2 e da 2.3 para serem confirmados ou removidos.
