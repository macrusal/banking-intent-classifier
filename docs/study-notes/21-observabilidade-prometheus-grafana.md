# Study Note 21 — Observabilidade com Prometheus e Grafana como código

## Objetivo

Transformar as métricas expostas pela API ([nota 20](20-instrumentacao-prometheus-e-buckets.md))
em uma stack de observabilidade que qualquer pessoa sobe com um comando e que já abre com o
dashboard funcionando: coleta pelo Prometheus, visualização pelo Grafana, sem nenhum clique
de configuração.

## O que foi construído

```text
compose.monitoring.yaml
 ├── api         build do Dockerfile, ./artifacts montado (ro), porta 8000
 ├── prometheus  coleta api:8000/metrics a cada 5 s, porta 9090
 └── grafana     datasource + dashboard provisionados, leitura anônima, porta 3000
```

```text
API ──/metrics──► Prometheus ──PromQL──► Grafana ──► avaliador em localhost:3000
     (texto)      (séries no tempo)      (3 painéis)
```

Cada componente tem uma responsabilidade:
- **a API** só **expõe** o estado atual dos contadores;
- **o Prometheus** **puxa** esse estado periodicamente e guarda a série temporal;
- **o Grafana** **consulta** o Prometheus e desenha.

A API não sabe que o Prometheus existe, e o Prometheus não sabe que o Grafana existe. É o
modelo *pull*, e é por isso que a instrumentação da nota 20 não precisou de nenhuma
configuração de destino.

## Por que provisionar como código

O caminho intuitivo é montar o dashboard clicando na UI e exportar o JSON depois. Ele tem
três problemas:

1. **O resultado depende de quem clicou.** Ninguém reproduz exatamente a mesma sequência de
   cliques; o avaliador receberia instruções em vez de um sistema.
2. **O estado mora no banco interno do Grafana**, fora do repositório. Recriar o contêiner
   apaga tudo, e o que está versionado é só uma fotografia exportada, que pode não ser o que
   está rodando.
3. **Não há revisão.** Uma mudança na consulta de um painel não passa por diff nem por Pull
   Request.

Com provisionamento, o Grafana lê arquivos na subida:

| Arquivo | Papel |
| :--- | :--- |
| `provisioning/datasources/prometheus.yml` | Declara a conexão com o Prometheus |
| `provisioning/dashboards/dashboards.yml` | *Provider*: diz ao Grafana em que diretório procurar dashboards |
| `dashboards/api.json` | O dashboard em si: painéis, consultas e unidades |

`allowUiUpdates: false` e `editable: false` fecham o ciclo. A UI não consegue divergir do
arquivo, então **o repositório é a única fonte da verdade**. É o mesmo princípio que já
governa o resto do projeto: o `Dockerfile` em vez de "instale isto na máquina", a DAG em
arquivo em vez de agendamento manual, o `uv.lock` em vez de "use uma versão recente".

O mesmo raciocínio levou a fixar as versões das imagens (`prom/prometheus:v3.12.0`,
`grafana/grafana:13.0.1`). Com `latest`, os mesmos arquivos poderiam subir em versões
diferentes em cada máquina.

## A armadilha do uid do datasource

Este é o erro mais comum em dashboard provisionado, e o mais confuso, porque tudo parece
correto.

Um painel não referencia o datasource pelo nome. Ele referencia um **uid**:

```json
"datasource": { "type": "prometheus", "uid": "banking-intent-prometheus" }
```

Se o arquivo do datasource **não declarar** um `uid`, o Grafana gera um aleatório na subida.
O dashboard, escrito antes, aponta para um uid que não existe, e todos os painéis exibem
**"datasource not found"**. O datasource existe, o dashboard existe, a consulta está certa, e
mesmo assim nada aparece.

A correção tem duas partes:

1. **Fixar o uid no datasource**: `uid: banking-intent-prometheus`.
2. **Usar exatamente esse uid em todo lugar do JSON**, no painel e em cada consulta.

Um contrato entre dois arquivos que ninguém verifica tende a quebrar na próxima edição.
Por isso o teste `test_dashboard_references_provisioned_datasource_uid` lê os dois arquivos
e exige que o conjunto de uids usados no dashboard seja exatamente o uid declarado. Um
renomeio descuidado quebra o CI, não a demonstração.

O mesmo vale para os nomes das métricas: `test_dashboard_queries_use_only_exported_metrics`
extrai os nomes `http_*` das consultas e compara com os que o código de `metrics.py`
realmente registra. Se alguém renomear o Counter, o teste falha antes de o painel ficar
vazio.

## Por que a unidade do eixo importa

O Histogram registra em **segundos**, a convenção do Prometheus. O p95 do servidor fica em
torno de 0,0022–0,0029 s. Sem unidade configurada, o painel exibe:

```text
0.00291
```

Um número assim parece quebrado, ou zero. O avaliador não sabe se são segundos,
milissegundos ou uma razão. Com `"unit": "s"`, o Grafana escala automaticamente e exibe:

```text
2.91 ms
```

O dado é o mesmo; o que muda é se ele comunica alguma coisa. Um painel existe para ser lido
em segundos por alguém que não escreveu a consulta. A unidade faz parte da informação, não
é acabamento.

O mesmo cuidado vale para os outros dois painéis: `reqps` (requisições por segundo) na
taxa e `percentunit` no erro. Neste último, a consulta devolve uma razão entre 0 e 1, e o
Grafana a exibe como porcentagem.

## Três painéis a partir de duas métricas

A API expõe só duas métricas: um Counter e um Histogram. Os três painéis da rubrica saem
delas.

### 1. Taxa de requisições — do Counter

```promql
sum by (endpoint) (rate(http_requests_total[$__rate_interval]))
```

O valor absoluto de um Counter (quantas requisições desde a subida) não interessa. `rate`
calcula a derivada por segundo na janela, e `sum by (endpoint)` soma os `status_code` de
cada endpoint.

### 2. Latência p95 — do Histogram

```promql
histogram_quantile(0.95,
  sum by (le) (rate(http_request_duration_seconds_bucket{endpoint="/predict"}[$__rate_interval])))
```

Três passos:
- `rate` transforma as contagens acumuladas de cada bucket em taxa na janela recente;
- `sum by (le)` agrega mantendo só a fronteira do bucket, que é o que o
  `histogram_quantile` precisa;
- `histogram_quantile` interpola o percentil.

Sem o `by (le)`, a fronteira some e a função não tem o que interpolar. O filtro em
`/predict` mantém o painel no endpoint de negócio, onde os buckets foram calibrados.

### 3. Taxa de erro — do mesmo Counter, outra vez

```promql
(sum(rate(http_requests_total{status_code=~"5.."}[$__rate_interval])) or vector(0))
  / (sum(rate(http_requests_total[$__rate_interval])) > 0)
  or vector(0)
```

O mesmo Counter do painel 1, filtrado por `status_code`. **Não existe métrica de erro**, e é
isso que garante a consistência: numerador e denominador vêm da mesma série. Não há como o
painel de erro "contar" uma requisição que o painel de taxa não contou.

**O caso sem tráfego.** Sem requisições, numerador e denominador valem 0, e 0/0 vira `NaN`.
Pior: se nunca houve um 5xx, a série `status_code=~"5.."` nem existe, e o numerador é um
vetor vazio. A consulta trata os dois casos:

| Situação | Mecanismo | Resultado |
| :--- | :--- | :--- |
| Tráfego sem nenhum 5xx | `or vector(0)` no numerador | `0 / total` = 0 |
| Sem tráfego | `> 0` descarta o denominador zero; `or vector(0)` final | 0 |
| Tráfego com 5xx | Razão normal | fração entre 0 e 1 |

A precedência do PromQL faz a consulta funcionar sem parênteses extras: `/` é avaliado
antes de `or`.

**Por que só 5xx.** Um 422 (texto vazio) é erro do cliente; o serviço funcionou. Contar 4xx
como erro faria um cliente mal configurado disparar o alarme do serviço. Eles continuam no
Counter, disponíveis para outra consulta.

## Detalhes de coleta que mudam o que se vê

- **`scrape_interval: 5s`.** Com os 15 s padrão, entre falar "agora vou gerar carga" e o
  gráfico subir passariam até 15 s, mais a janela do `rate`. Na gravação do vídeo, isso
  pareceria um painel quebrado.
- **`$__rate_interval` e `timeInterval: 5s`.** Uma janela de `rate` precisa conter pelo menos
  dois scrapes. O `$__rate_interval` do Grafana calcula essa janela (no mínimo 4 × o
  intervalo de scrape), mas só se souber qual é o intervalo. Por isso o datasource declara
  `timeInterval: 5s`, e a janela fica em ~20 s: curta para reagir, longa para não
  oscilar.
- **Alvo `api:8000`, não `localhost:8000`.** Dentro do contêiner do Prometheus, `localhost` é
  o próprio Prometheus. Na rede do Compose, cada serviço é resolvido pelo nome. É o mesmo
  aprendizado do `EXECUTION_API_SERVER_URL` do Airflow ([nota 18](airflow-training-pipeline.md)).
- **O scrape não se mede.** Como o middleware ignora `/metrics` (nota 20), o painel de taxa
  mostra o tráfego do serviço, não o do próprio Prometheus a cada 5 s.

## Validação com carga real

"O painel subiu" não é critério de pronto; um painel pode subir e não mostrar nada. A
validação executou as **consultas do próprio `api.json` pela API do Grafana**, o mesmo
caminho que o painel usa, inclusive a expansão do `$__rate_interval`. Foi feita com a
stack recriada do zero:

| Painel | Sem tráfego | Durante a carga |
| :--- | :--- | :--- |
| Taxa de requisições | 0,00 req/s | 265,40 req/s em `/predict` (média da janela, não vazão) |
| Latência p95 | sem série | 2,91 ms |
| Taxa de erro | 0,00% | 0,00% |

Três leituras que a tabela ensina:

1. **A taxa ficou abaixo dos ~380–390 req/s medidos pelo cliente** porque a janela de ~20 s
   pega as pausas entre execuções do benchmark. O painel mostra a média da janela, não o
   pico. Por isso, 265,40 req/s **não é a vazão da API** e não deve ser citado como tal.
2. **O p95 de 2,91 ms foi medido na primeira carga após a subida.** Numa rodada com o
   contêiner aquecido, o mesmo painel mostrou 2,27 ms. É o efeito de primeira execução da
   nota 19, agora visível também no servidor. Para a gravação, convém aquecer a stack antes.
3. **O 0,00% sem tráfego prova o tratamento do 0/0.** O 0,00% com tráfego mostra que a carga
   não provocou erros, mas **não prova que o painel detecta erros**. Esse caminho é coberto
   pelos testes do label `status_code`, não por uma falha provocada de ponta a ponta.

## Incidentes do processo

| Incidente | O que ensinou |
| :--- | :--- |
| Log do Grafana com `provisioning/plugins` e `provisioning/alerting` não encontrados | Montar `provisioning/` inteiro **substitui** o diretório da imagem, e os subdiretórios padrão somem. A solução foi montar só `datasources/` e `dashboards/`. Um volume é uma sobreposição, não uma fusão. |
| `Failed to install plugin` no log | O Grafana tenta instalar ou atualizar plugins na subida, o que exige rede. `GF_PLUGINS_PREINSTALL_DISABLED=true` remove a dependência de rede que a demonstração não precisa. |
| Script de leitura dos painéis quebrou num frame sem campos | "Sem dado" volta como um frame vazio, não como valor nulo. Quem escreve a verificação também precisa tratar o caso sem dado, o mesmo que o painel de erro trata. |

## Reprodutibilidade

```bash
uv run --frozen python -m banking_intent_classifier.final_training
docker compose -f compose.monitoring.yaml up -d --build
# abrir http://localhost:9090/targets e http://localhost:3000
for i in 1 2 3; do
  uv run --frozen python -m banking_intent_classifier.http_latency_benchmark --name stack --output artifacts/http_latency_stack_run$i.json
done
docker compose -f compose.monitoring.yaml down

uv run --frozen pytest tests/test_monitoring_config.py -v
uv run --frozen --group onnx pytest
```

O procedimento completo, a verificação sem UI e o diagnóstico estão em
[`operacao-monitoramento.md`](../operacao-monitoramento.md).

## Conceitos aprendidos

- **Modelo pull:** a aplicação expõe, o Prometheus coleta, o Grafana consulta. Cada camada
  ignora a seguinte.
- **Provisionamento torna o dashboard reproduzível e revisável.** O repositório vira a fonte
  da verdade, e a UI vira só leitura.
- **O uid do datasource é um contrato entre arquivos.** Contratos sem verificação quebram, e
  o teste transforma um erro de demonstração num erro de CI.
- **Unidade faz parte do dado.** "0.00291" e "2.91 ms" são o mesmo número e informações
  diferentes.
- **Poucas métricas bem desenhadas bastam.** Um Counter com `status_code` dá taxa e erro;
  um Histogram dá latência. Métricas derivadas por consulta não divergem.
- **Consultas precisam tratar o caso vazio.** 0/0 e séries inexistentes são o estado normal
  de um serviço sem tráfego.
- **Intervalo de coleta e janela de `rate` são decisões de produto.** Definem quanto o
  gráfico demora para reagir.
- **Validar é ler o valor, não ver o painel subir.**
