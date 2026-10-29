# Study Note 20 — Instrumentação Prometheus e calibração dos buckets

## Objetivo

Expor métricas da API no formato Prometheus (taxa de requisições, latência e taxa de erro)
e escolher os buckets do Histogram a partir da latência medida **dentro do servidor**, não
por suposição nem pela medição do cliente.

## O que foi implementado

| Componente | Responsabilidade |
| :--- | :--- |
| `presentation/metrics.py` | `PrometheusMiddleware` (ASGI), Counter, Histogram, buckets e a rota de `/metrics` |
| `presentation/api.py` | Duas linhas: `add_middleware` e `add_route("/metrics")` |
| `tests/presentation/test_metrics.py` | Formato do `/metrics`, incremento após `/predict`, erro como label, cardinalidade |

| Métrica | Tipo | Labels |
| :--- | :--- | :--- |
| `http_requests_total` | Counter | `endpoint`, `status_code` |
| `http_request_duration_seconds` | Histogram | `endpoint` |

A taxa de erro **não** é uma métrica própria. Ela é uma consulta sobre o Counter:

```promql
sum(rate(http_requests_total{status_code=~"5.."}[1m])) / sum(rate(http_requests_total[1m]))
```

Criar um `http_errors_total` separado duplicaria a informação e abriria espaço para
inconsistência: dois contadores que precisam concordar e podem divergir.

## Conceitos de Prometheus que a tarefa exigiu

### Counter, Histogram e o que cada um guarda

- **Counter:** só cresce. O valor absoluto quase não interessa; o que importa é a taxa
  (`rate`) num intervalo.
- **Histogram:** não guarda as observações. Guarda três coisas:
  - `_count`: quantas observações houve;
  - `_sum`: a soma de todas elas;
  - `_bucket{le="x"}`: quantas foram **menores ou iguais** a `x`. As contagens são
    acumuladas, não por faixa.

Daí saem duas propriedades importantes:

1. **`_sum / _count` dá a média exata**, independentemente dos buckets.
2. **Percentis são estimativas.** O `histogram_quantile` encontra o bucket onde o percentil
   cai e interpola linearmente dentro dele. O erro máximo da estimativa é a largura desse
   bucket.

### Labels e cardinalidade

Cada combinação de valores de labels é uma série temporal separada. Usar o path bruto como
label faria cada `/rota-inexistente/123` criar séries novas, e um varredor de URLs poderia
inflar a memória do Prometheus sem limite.

Por isso, o label `endpoint` usa o **template da rota** (`scope["route"].path`), que o
roteador do Starlette grava no scope. Requisições sem rota correspondente caem num valor
único, `unmatched`. O teste `test_unknown_path_and_scrape_do_not_create_labels` protege
essa decisão.

### Middleware ASGI em vez de decorators

Um decorator por endpoint depende de alguém lembrar de aplicá-lo em cada rota nova, e não
enxerga respostas geradas fora dos endpoints: o 404 do roteador e o 422 de validação do
FastAPI. O middleware envolve a aplicação inteira e vê tudo. Ele intercepta a mensagem
`http.response.start` para ler o status e registra a observação num `finally`, o que
garante o registro mesmo se a aplicação lançar uma exceção. Nesse caso, a requisição fica
como `status_code="500"`.

### Onde a latência é medida muda o significado do número

O cronômetro começa quando a requisição entra no middleware e termina quando a chamada à
aplicação retorna, depois do envio da resposta. O número inclui validação Pydantic,
inferência e serialização JSON. **Não** inclui a rede até o cliente nem o parsing HTTP feito
pelo `uvicorn` antes do middleware. É uma decisão de desenho, e precisa ser declarada junto
com o número.

### O scrape não deve medir a si mesmo

O Prometheus vai consultar `/metrics` a cada 5 s. Se essa rota fosse instrumentada, o
painel de taxa de requisições mostraria um tráfego de fundo que não é do serviço. O
middleware ignora `/metrics`.

## Calibração dos buckets: o raciocínio

### Por que não usar o percentil estimado para decidir

A tentação era ler o p50 e o p95 que o próprio Histogram estima e ajustar as fronteiras por
eles. O problema é que essa estimativa é feita **a partir das fronteiras**. Usá-la para
escolher as fronteiras é circular: o instrumento estaria validando a si mesmo.

Foram usados dois valores que não dependem dos buckets: a média exata (`_sum / _count`) e a
contagem acumulada de cada bucket. Os buckets dizem **onde a massa está**; não foram usados
para dizer exatamente onde fica o percentil.

### Como isolar uma execução

O Counter e o Histogram acumulam desde a subida do processo. Para medir uma execução, foi
tirado um snapshot do `/metrics` antes e outro depois, e calculada a diferença entre eles.
Antes de tudo, uma execução inteira de aquecimento foi descartada, pelo padrão do máximo
alto na primeira execução registrado na [nota 19](19-baseline-latencia-http.md).

### O que a primeira coleta mostrou

Com os buckets provisórios (1; 2; 2,5; 3; 4; 5 ms…):

| Execução | Média servidor | Média cliente | ≤ 2 ms | ≤ 2,5 ms |
| :--- | ---: | ---: | ---: | ---: |
| 1 | 1,83 ms | 2,52 ms | 86,4% | 99,3% |
| 2 | 1,86 ms | 2,53 ms | 83,3% | 97,4% |
| 3 | 1,92 ms | 2,61 ms | 71,7% | 96,1% |

Três achados:

1. **Servidor cerca de 0,7 ms abaixo do cliente.** É o custo do caminho host → VM do Docker
   Desktop mais o cliente. A previsão da nota 19 se confirmou.
2. **72% a 86% das observações num único bucket de 1 ms** (entre 1 e 2 ms). O p50 estava ali
   dentro, sem nenhuma resolução.
3. **O ponto de atenção mudou de percentil.** A nota 19 temia o p50 do cliente encostado em
   2,5 ms. No servidor, o p50 fica longe dali, e quem encosta é o **p95**: o acumulado em
   2,5 ms foi de 96,1% na execução 3, a 1,1 ponto de 95%. Como o p95 é o painel exigido,
   o problema ficou mais sério do que o previsto.

### A decisão

Fronteiras finais, em ms: 0,5; 1; 1,25; 1,5; 1,75; 2; 2,25; 2,5; 2,75; 3; 4; 5; 7,5; 10;
25; 50; 100; 250.

Remedição com as fronteiras novas:

| Execução | Média servidor | ≤ 1,75 ms | ≤ 2 ms | ≤ 2,25 ms | ≤ 2,5 ms |
| :--- | ---: | ---: | ---: | ---: | ---: |
| 4 | 1,80 ms | 44,7% | 89,3% | 98,1% | 99,2% |
| 5 | 1,83 ms | 39,4% | 86,4% | 96,5% | 98,7% |
| 6 | 1,89 ms | 31,0% | 75,7% | 93,2% | 97,9% |

A massa agora se espalha por quatro ou cinco buckets. O p50 fica entre 1,75 e 2 ms, e o
p95 entre 2 e 2,5 ms. Nos dois, o erro de interpolação cai para no máximo 0,25 ms.

**A lição central:** o problema nunca foi a fronteira de 2,5 ms em si, e sim **a largura do
bucket ao redor do percentil**. O `histogram_quantile` interpola linearmente; com vizinhos a
0,25 ms de distância, cruzar uma fronteira move a estimativa pouco, sem salto no painel. A
solução sugerida na nota 19, um bucket extra em 2,25 ms, estava certa, mas pelo motivo
errado e para o percentil errado.

O p95 também cruzou 2,25 ms entre as execuções 5 e 6. Isso acompanhou uma mudança real: a
média subiu de 1,83 para 1,89 ms. É o comportamento desejado: o painel reage a uma variação
de verdade.

### Medição e decisão de reserva

Os buckets de 1 e 1,25 ms ficaram vazios, e o de 0,5 ms também. Foram mantidos por uma
**decisão registrada**: são uma reserva de resolução para um backend mais rápido. O modelo
isolado em ONNX é cerca de 0,5 ms mais rápido no p50 que o Scikit-learn
([`onnx-benchmark.md`](../onnx-benchmark.md)). Servir ONNX na API ficou fora do escopo
desta entrega, então essa faixa não será medida aqui. Por isso o texto não a trata como
previsão a confirmar. A documentação separa o que foi medido (a distribuição de 1,5 a 4 ms)
do que foi decidido sem medição (a reserva abaixo de 1,25 ms). Misturar os dois, sem
distinguir, é uma das formas mais comuns de documentação técnica enganosa.

**Custo da granularidade:** 18 fronteiras mais `+Inf` dão 19 séries `_bucket` por valor de
`endpoint`, que tem poucos valores possíveis. A resolução extra é praticamente gratuita.

## Incidentes do processo

| Incidente | O que ensinou |
| :--- | :--- |
| `uv add prometheus-client` negado pelo controle de permissões do agente | A autorização dada em texto não muda as regras configuradas em `.claude/settings.json`. O agente parou em vez de contornar (editar o `pyproject.toml` à mão e rodar `uv lock`), e o comando foi executado pelo autor com `! uv add prometheus-client`. |
| Label `method` acrescentado sem ter sido pedido | Escopo extra entra discretamente, mesmo numa boa intenção. Foi removido antes dos testes; a especificação pedia `endpoint` e `status_code`. |
| Comando com `curl` e `rm` negado durante a validação | A validação foi refeita com Python, contra `localhost`, e os arquivos temporários ficaram em `artifacts/`, que é ignorado pelo Git. |
| Nota 19 com a faixa de uma sessão de medição superada | Quando uma medição é refeita, o documento principal e as notas precisam ser atualizados juntos. Foi corrigido nesta etapa, mantendo o número antigo como registro histórico. |

## Reprodutibilidade

```bash
uv run --frozen pytest tests/presentation/test_metrics.py -v
uv run --frozen ruff check .
uv run --frozen --group onnx pytest
```

O procedimento de coleta do lado servidor está em
[`prometheus-instrumentation.md`](../prometheus-instrumentation.md#reprodução), com
snapshots antes e depois e o código de extração do delta embutido. Ele já foi executado.

## Conceitos aprendidos

- **Um Histogram dá a média exata e percentis estimados.** O erro da estimativa é a
  largura do bucket onde o percentil cai.
- **Calibrar buckets pelo quantil que eles próprios estimam é circular.** Use `_sum`,
  `_count` e as contagens acumuladas.
- **O ponto de medição define o número.** Cliente e servidor diferem em cerca de 0,7 ms
  neste ambiente, e o p95 de um não serve para calibrar o instrumento do outro.
- **Cardinalidade é decisão de projeto.** Template da rota, valor único para rotas
  inexistentes e scrape fora da medição.
- **Taxa de erro é consulta, não métrica.** Derivar do Counter evita duas fontes de
  verdade.
- **Decisão sem medição deve ser rotulada como tal.** Os buckets abaixo de 1,25 ms são
  reserva para um backend mais rápido, decidida e registrada. Não são uma previsão deixada
  sem verificação.
