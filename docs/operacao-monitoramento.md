# Operação da stack de monitoramento

Este documento concentra a arquitetura operacional, a reprodução, a verificação e o diagnóstico da stack Prometheus + Grafana da API Banking Intent Classifier.

As métricas expostas pela API e a calibração dos buckets estão em [`prometheus-instrumentation.md`](prometheus-instrumentation.md). Aqui estão a coleta e a visualização.

## Estado confirmado em 26/10/2026

A stack foi recriada do zero (`down` seguido de `up -d --build`) e validada com carga real gerada por `http_latency_benchmark`, com três execuções de 3.080 requisições.

| Verificação | Resultado |
| :--- | :--- |
| Target no Prometheus | `banking-intent-api`, `http://api:8000/metrics`, `health=up`, sem erro de scrape |
| Datasource no Grafana | `uid=banking-intent-prometheus`, `url=http://prometheus:9090`, `timeInterval=5s` |
| Dashboard | `Banking Intent API` (`uid=banking-intent-api`), provisionado e definido como página inicial |
| Acesso anônimo | Datasource, dashboard e consultas lidos via API do Grafana sem autenticação |
| Logs | Sem erros de provisionamento no Grafana nem erros no Prometheus |

**Valores exibidos pelos painéis** (consultas do `api.json` executadas pela API do Grafana, último ponto da série):

| Painel | Sem tráfego | Durante a carga (21:55:48 UTC) | 60 s após a carga |
| :--- | :--- | :--- | :--- |
| Taxa de requisições | `/health` 0,00 req/s | `/predict` 265,40 req/s; `/health` 0,07 req/s | `/predict` 0,00 req/s |
| Latência p95 — `POST /predict` | sem série (nenhuma requisição) | 2,91 ms | último ponto: 2,22 ms; a série termina quando o tráfego para |
| Taxa de erro (5xx) | 0,00% | 0,00% | 0,00% |

**Como ler esses números:**

- **Taxa de requisições abaixo do throughput do cliente** (~380–390 req/s). Entre uma execução e outra, o benchmark recarrega o dataset e faz o aquecimento, e a janela do `rate` pega essas pausas.
- **p95 de 2,91 ms durante a carga.** Esta foi a primeira carga depois de subir o contêiner. O cliente mediu p95 de 4,26 ms na primeira execução, contra 2,95–3,20 ms nas seguintes: é o efeito de primeira execução registrado na [nota 19](study-notes/19-baseline-latencia-http.md). Numa rodada anterior, com o contêiner já aquecido, o painel exibiu 2,27 ms durante a carga.
- **0,00% de erro com tráfego.** Nenhuma requisição retornou 5xx, e a carga não provoca falhas. O caminho com erro é coberto pelo label `status_code`, testado em `tests/presentation/test_metrics.py`. Ele não foi exercitado de ponta a ponta no painel.

## Decisões de arquitetura e justificativas

| Decisão | Justificativa e consequência |
| :--- | :--- |
| `compose.monitoring.yaml` separado de `compose.airflow.yaml` | O Airflow sobe api-server, scheduler, dag-processor e PostgreSQL. Juntar as stacks tornaria a demonstração pesada e frágil, sem ganho. |
| Serviço `api` construído do `Dockerfile` do projeto | A stack observa a mesma imagem validada pelo CI, não uma variante. |
| `./artifacts:/app/artifacts:ro` no serviço `api` | Mesmo padrão do Airflow. `artifacts/` é ignorado pelo Git, então o modelo vem do host. Somente leitura: a API não escreve artefatos. |
| Scrape de `api:8000`, nunca `localhost` | Dentro do contêiner do Prometheus, `localhost` é o próprio Prometheus. A comunicação usa o DNS interno do Compose, como o `EXECUTION_API_SERVER_URL` do Airflow. |
| `scrape_interval: 5s` | O padrão de 15 s faria o gráfico reagir tarde demais durante a gravação do vídeo. |
| Datasource com `uid` fixo, referenciado no dashboard | Sem `uid` fixo, o Grafana gera um aleatório, e o painel provisionado mostra "datasource not found". `tests/test_monitoring_config.py` protege a correspondência. |
| `jsonData.timeInterval: 5s` | O `$__rate_interval` passa a ser calculado com o intervalo real de scrape: no mínimo 4 × 5 s = 20 s. A janela do `rate` fica curta e reativa, sem ficar menor que dois scrapes. |
| Dashboard em arquivo (`allowUiUpdates: false`, `editable: false`) | O JSON versionado é a fonte da verdade. Ajustes feitos na UI não sobrevivem à recriação e não divergem do repositório. |
| Acesso anônimo com papel `Viewer` | O avaliador abre `localhost:3000` e vê o dashboard sem login. O papel `Viewer` não permite editar. |
| Dashboard como página inicial | `GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH` aponta para o `api.json`. |
| Montar só `provisioning/datasources` e `provisioning/dashboards` | Montar o diretório `provisioning/` inteiro escondia os subdiretórios `plugins/` e `alerting/` da imagem e gerava erros no log. |
| `GF_PLUGINS_PREINSTALL_DISABLED=true` | Nenhum plugin extra é usado. Desligar a instalação na subida elimina uma chamada de rede e um erro de log (`Failed to install plugin`). |
| Versões fixas: `prom/prometheus:v3.12.0`, `grafana/grafana:13.0.1` | Com `latest`, a mesma configuração poderia subir em versões diferentes em cada máquina. |
| Sem volumes persistentes para Prometheus e Grafana | A série temporal e o estado do Grafana são descartáveis numa demonstração local; tudo o que importa está em arquivo. Um `down` recomeça do zero. |

## Serviços, portas e persistência

| Serviço | Imagem | Porta local | Papel |
| :--- | :--- | :--- | :--- |
| `api` | `banking-intent-classifier:monitoring` (build local) | `8000` | API FastAPI com `/predict`, `/health` e `/metrics` |
| `prometheus` | `prom/prometheus:v3.12.0` | `9090` | Coleta `api:8000/metrics` a cada 5 s |
| `grafana` | `grafana/grafana:13.0.1` | `3000` | Dashboard provisionado, leitura anônima |

Arquivos versionados:

```text
compose.monitoring.yaml
monitoring/
├── prometheus.yml
└── grafana/
    ├── provisioning/
    │   ├── datasources/prometheus.yml   # uid fixo: banking-intent-prometheus
    │   └── dashboards/dashboards.yml    # provider de arquivos
    └── dashboards/api.json              # três painéis
```

## Reproduzir e verificar

### Pré-requisitos

- Docker Desktop ou Engine com Compose, e as portas 8000, 9090 e 3000 livres.
- `uv` e Python 3.12, para gerar os artefatos e a carga.
- **Artefatos do modelo em `artifacts/`.** Eles não são versionados, e o `Dockerfile` os copia no build. Sem eles, o `docker compose up --build` falha no `COPY artifacts/`.

```bash
uv run --frozen python -m banking_intent_classifier.final_training
ls -lh artifacts/baseline_pipeline.joblib artifacts/label_mapping.json
```

O `final_training` baixa o BANKING77 do Hugging Face Hub, ou usa o cache local.

### Subir a stack

```bash
docker compose -f compose.monitoring.yaml config --quiet
docker compose -f compose.monitoring.yaml up -d --build
docker compose -f compose.monitoring.yaml ps
```

| Interface | Endereço |
| :--- | :--- |
| API (Swagger) | <http://localhost:8000/docs> |
| Métricas da API | <http://localhost:8000/metrics> |
| Targets do Prometheus | <http://localhost:9090/targets> |
| Grafana (dashboard inicial, sem login) | <http://localhost:3000> |

### Gerar carga

```bash
until curl -sf http://localhost:8000/health >/dev/null; do sleep 1; done
for i in 1 2 3; do
  uv run --frozen python -m banking_intent_classifier.http_latency_benchmark --name stack --output artifacts/http_latency_stack_run$i.json
done
```

Cada execução envia 100 requisições de aquecimento e as 3.080 do split `test`, em cerca de 10 s. O dashboard atualiza a cada 5 s.

### Verificar sem a UI

```bash
# Target UP
curl -s http://localhost:9090/api/v1/targets | python3 -c "import json, sys; [print(t['scrapeUrl'], t['health'], t['lastError'] or '-') for t in json.load(sys.stdin)['data']['activeTargets']]"

# Datasource e dashboard provisionados, lidos sem autenticação
curl -s http://localhost:3000/api/datasources/uid/banking-intent-prometheus
curl -s http://localhost:3000/api/dashboards/uid/banking-intent-api | python3 -c "import json, sys; d = json.load(sys.stdin); print(d['meta']['provisioned'], [p['title'] for p in d['dashboard']['panels']])"

# Valores atuais dos três painéis, direto no Prometheus (janela fixa de 1 min)
for q in \
  'sum by (endpoint) (rate(http_requests_total[1m]))' \
  'histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{endpoint="/predict"}[1m])))' \
  '(sum(rate(http_requests_total{status_code=~"5.."}[1m])) or vector(0)) / (sum(rate(http_requests_total[1m])) > 0) or vector(0)'; do
  curl -s --get http://localhost:9090/api/v1/query --data-urlencode "query=$q" | python3 -c "import json, sys; print([(r['metric'], r['value'][1]) for r in json.load(sys.stdin)['data']['result']])"
done
```

O Grafana usa `$__rate_interval` (~20 s); a verificação acima usa 1 min. Os valores podem diferir enquanto a carga varia.

### Testes da configuração

```bash
uv run --frozen pytest tests/test_monitoring_config.py -v
```

Os testes conferem:
- os três serviços e o volume de artefatos;
- o scrape de `api:8000` a cada 5 s;
- o uid do datasource igual ao do dashboard;
- que as consultas usam só métricas que a API expõe;
- as unidades dos painéis.

### Encerrar

```bash
docker compose -f compose.monitoring.yaml down
```

**Não é preciso usar `-v`:** a stack não declara volumes nomeados, e o `-v` não traz ganho nenhum. O `compose.airflow.yaml` é um projeto separado (`banking-intent-airflow`), e o `down` desta stack não o afeta.

## Painéis e consultas

As duas métricas da API sustentam os três painéis:

| Painel | Consulta | Unidade |
| :--- | :--- | :--- |
| Taxa de requisições | `sum by (endpoint) (rate(http_requests_total[$__rate_interval]))` | `reqps` |
| Latência p95 — `POST /predict` | `histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{endpoint="/predict"}[$__rate_interval])))` | `s` |
| Taxa de erro (5xx) | `(sum(rate(http_requests_total{status_code=~"5.."}[$__rate_interval])) or vector(0)) / (sum(rate(http_requests_total[$__rate_interval])) > 0) or vector(0)` | `percentunit` |

- **Latência filtrada em `/predict`:** é o endpoint de negócio, onde os buckets foram calibrados. Agregar `/health` e `/docs` misturaria latências de outra natureza.
- **Unidade `s`:** o Histogram está em segundos. Com a unidade, o Grafana escala para "2.91 ms"; sem ela, exibiria "0.00291".
- **Taxa de erro sem tráfego:** o denominador `> 0` descarta o total zero, que faria a razão virar 0/0, e o `or vector(0)` final exibe 0. Quando há tráfego sem nenhum 5xx, o `or vector(0)` do numerador evita um vetor vazio.
- **O que conta como erro:** só 5xx. Erros 4xx, como o 422 de texto vazio, são falhas do cliente. Eles continuam contados no Counter, mas não entram no painel.

## Incidentes, diagnóstico e segurança

```bash
docker compose -f compose.monitoring.yaml logs --tail=100 api prometheus grafana
docker compose -f compose.monitoring.yaml logs grafana | grep -E "level=error"
docker compose -f compose.monitoring.yaml exec api sh -c 'ls -l /app/artifacts'
```

| Sintoma | Causa provável e correção |
| :--- | :--- |
| `COPY artifacts/` falha no build | Artefatos não gerados: rodar `final_training` |
| Target `down` em `/targets` | A API não subiu ou falhou ao carregar o modelo: ver `logs api` |
| Painel com "datasource not found" | `uid` do datasource diferente do usado no `api.json`: rodar `tests/test_monitoring_config.py` |
| Painéis sem dado | Nenhuma requisição ainda; gerar carga. A latência só tem série quando há `POST /predict` na janela |
| Erros `provisioning/plugins` ou `alerting` no log | Diretório `provisioning/` inteiro montado por cima do da imagem; montar só os subdiretórios usados |
| Porta 8000 ocupada | Outro contêiner da API (por exemplo, `bic-baseline`) em execução; pará-lo antes |

Histórico desta entrega: os dois erros de log descritos nas decisões (subdiretórios de provisionamento e instalação de plugin) apareceram na primeira subida e foram corrigidos na configuração. A validação final foi feita depois da correção, com a stack recriada.

**Segurança.** A stack é local e de demonstração:
- O acesso anônimo dá apenas leitura (`Viewer`).
- O usuário administrador do Grafana usa a credencial padrão da imagem (`admin`/`admin`, com troca pedida no primeiro login). Não exponha estas portas fora da máquina local.
- A configuração não contém segredos.
- Numa implantação real, o acesso anônimo seria desligado e a credencial viria de um segredo. Isso fica para a frente de arquitetura em nuvem.

Para aprofundamento técnico: [nota de estudo 21](study-notes/21-observabilidade-prometheus-grafana.md).
