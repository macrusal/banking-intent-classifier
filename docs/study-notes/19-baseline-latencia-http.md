# Study Note 19 — Baseline de latência HTTP da API

## Objetivo

Medir a latência ponta a ponta de `POST /predict` contra a API em container, estabelecendo
a baseline exigida na Etapa 1 do enunciado e a referência quantitativa para calibrar os
buckets do Histogram da instrumentação Prometheus.

## Por que o benchmark do modelo não serve como baseline

O projeto já tinha uma medição de latência, registrada em
[`onnx-benchmark.md`](../onnx-benchmark.md). Ela mede o **modelo isolado**, chamando o
Pipeline diretamente em processo. A baseline pedida no enunciado é outra coisa: mede o
**serviço**, como o cliente o percebe.

A diferença é o que fica entre as duas medições:

| Etapa | Benchmark do modelo | Baseline HTTP |
| :--- | :---: | :---: |
| Cliente HTTP e conexão TCP | — | incluído |
| Encaminhamento de porta e rede do Docker | — | incluído |
| Validação Pydantic do corpo da requisição | — | incluído |
| Inferência do Pipeline | incluído | incluído |
| Serialização JSON da resposta | — | incluído |

Confundir as duas é um erro de interpretação com consequência prática: o p50 do modelo é de
cerca de 0,6 ms e o do serviço é de cerca de 2,5 ms. Calibrar a instrumentação pelo número
errado produziria um Histogram cego, como se verá adiante.

## Resultado medido

Três execuções de 3.080 requisições cada, em 26/10/2026, na mesma instância do contêiner,
contra a imagem atual do `Dockerfile` com backend Scikit-learn:

| Métrica | Faixa observada |
| :--- | :--- |
| p50 | 2,47–2,48 ms |
| p95 | 3,08–3,19 ms |
| p99 | 3,71–4,31 ms |
| Throughput sequencial | 387,2–391,4 req/s |

O p50 variou menos de 0,01 ms entre execuções, o que indica medição estável. A cauda é
curta: o p99 ficou abaixo de 4,4 ms.

O máximo isolado merece um registro à parte. Na primeira execução após subir o contêiner,
ele foi cerca de duas vezes maior que nas seguintes, mesmo com as 100 requisições de
aquecimento: 10,2 ms contra 5,6–6,4 ms. O padrão já tinha aparecido numa sessão anterior
(13,4 ms na primeira execução). A causa não foi investigada. O efeito fica só no máximo e
não desloca os percentis, mas é um bom motivo para descartar uma execução inteira de
aquecimento antes de medir, como foi feito na calibração dos buckets
([nota 20](20-instrumentacao-prometheus-e-buckets.md)).

> **Registro histórico:** uma primeira sessão de medição, no mesmo dia, deu p50 de
> 2,53–2,57 ms, p95 de 3,00–3,22 ms e p99 de 3,47–4,22 ms. A sessão acima a substituiu como
> referência oficial e é a que está em
> [`http-latency-baseline.md`](../http-latency-baseline.md). A diferença de ~0,06 ms no p50
> entre sessões é maior que a variação dentro de cada sessão (< 0,04 ms). Isso mostra que
> comparar números de sessões diferentes exige cuidado, mesmo na mesma máquina.

Os números completos, os hashes dos artefatos medidos e as condições de ambiente estão em
[`http-latency-baseline.md`](../http-latency-baseline.md).

## Decisões de metodologia e o que cada uma protege

### Aquecimento fora da amostra

As primeiras requisições a um serviço recém-iniciado são sistematicamente mais lentas:
carregamento tardio de código, alocações iniciais, caches frios. Incluí-las na amostra
desloca a média e infla a cauda. Cem requisições de aquecimento são descartadas antes de
qualquer medição.

**O que isso protege:** a representatividade do p95 e do p99, que são justamente os números
usados para dimensionar alertas.

### Conexão persistente

O cliente mantém uma conexão TCP aberta (keep-alive) durante toda a medição. Abrir uma
conexão por requisição acrescentaria o custo do handshake a cada amostra, medindo o
estabelecimento de conexão em vez do tempo de resposta do serviço.

**O que isso protege:** a medição reflete o cenário real de um cliente que faz várias
chamadas, que é o caso de uso do projeto.

### Concorrência de um cliente, sequencial

Um único cliente, uma requisição por vez. Isso mede **latência**, não capacidade.

É importante não confundir os dois: com um cliente sequencial, o throughput observado é
simplesmente o inverso da latência média. Os ~389 req/s **não** são a capacidade máxima da
API; são uma consequência aritmética de cada requisição levar ~2,57 ms. Medir capacidade
exigiria vários clientes em paralelo e saturação deliberada do serviço, que é outro
experimento.

### Falha interrompe a medição

Qualquer resposta com status diferente de 200 aborta o benchmark. Uma requisição que falhou
rápido entraria na estatística como se fosse uma resposta rápida, melhorando artificialmente
os percentis.

### Percentis compartilhados com o benchmark ONNX

A função `summarize_latencies` foi extraída para a camada de aplicação e passou a ser usada
pelos dois benchmarks. Além de evitar duplicação, isso garante que os dois conjuntos de
números são comparáveis: mesma definição de percentil, mesma interpolação.

## Da medição à decisão: os buckets do Histogram

Este é o ponto onde a nota deixa de ser sobre medição e passa a ser sobre observabilidade.

Um `Histogram` do Prometheus não guarda cada observação. Ele guarda **contadores por
faixa** (buckets), e o `histogram_quantile` estima percentis a partir dessas contagens. A
consequência é direta: **a resolução do gráfico é limitada pelos buckets escolhidos.**

Os buckets padrão do `prometheus_client` começam em 5 ms. A latência medida fica entre 2 e
3,2 ms. Com o padrão, praticamente toda observação cairia no primeiro bucket, e o
`histogram_quantile` não teria informação para distinguir 2 ms de 4,9 ms — o painel de p95
exibiria uma linha praticamente reta, independentemente do que acontecesse com o serviço.

O erro é silencioso: nada falha, nenhum teste quebra, o dashboard sobe e parece funcionar.
Só não informa nada.

Buckets propostos nesta etapa como ponto de partida, cobrindo a faixa medida com resolução
e deixando margem para degradação (em segundos, conforme a convenção do Prometheus):

```text
0.001, 0.002, 0.0025, 0.003, 0.004, 0.005, 0.0075, 0.01, 0.025, 0.05, 0.1, 0.25
```

Equivalem a 1; 2; 2,5; 3; 4; 5; 7,5; 10; 25; 50; 100 e 250 ms. Os valores entre 2 e 7,5 ms
dão resolução exatamente onde estão o p50, o p95 e o p99; os maiores existem para que uma
degradação real tenha onde ser registrada.

Um ponto de atenção ficou registrado: o p50 do cliente (2,47–2,48 ms) ficava logo abaixo da
fronteira de 2,5 ms. Uma deriva de 0,03 ms bastaria para mudar o bucket da estimativa.

**Decisão adiada, depois fechada.** Esta medição foi feita do host para o contêiner. O
Histogram, porém, mede de dentro do servidor, sem o encaminhamento de porta do Docker
Desktop, e por isso deveria registrar latências menores. A decisão final ficou para depois
da primeira coleta real.

Essa coleta confirmou a expectativa: a média no servidor ficou entre 1,80 e 1,92 ms, cerca
de 0,7 ms abaixo da média do cliente. Ela também mostrou que a proposta acima tinha o
problema no lugar errado. O p50 do servidor fica longe de 2,5 ms; é o **p95** que encosta
nessa fronteira. Além disso, a maior parte das observações caía num único bucket de 1 ms.
As fronteiras finais usam passos de 0,25 ms entre 1 e 3 ms. O raciocínio completo está na
[nota 20](20-instrumentacao-prometheus-e-buckets.md).

A lição para esta nota: **a baseline do cliente era necessária para chegar à ordem de
grandeza, mas não bastava para calibrar um instrumento que mede em outro ponto do
caminho.**

## O que estes números não sustentam

Registrar o limite de uma medição é parte da medição.

**Não isolam o custo do HTTP.** O benchmark do modelo rodou em macOS nativo; este rodou em
Linux dentro da VM do Docker Desktop. A diferença de ~2 ms entre os dois inclui a mudança de
ambiente de execução, não só a camada HTTP.

**Não se transferem para outros ambientes.** No macOS, o encaminhamento de porta do host
para a VM acrescenta um custo que não existe em Linux nativo nem em infraestrutura de nuvem.
Os números valem para esta máquina, nesta configuração.

**Não dizem nada sobre carga.** Conforme explicado acima, capacidade exigiria outro
experimento.

## Arquitetura da solução

A implementação separa três responsabilidades, seguindo o padrão em camadas do projeto:

| Componente | Camada | Responsabilidade |
| :--- | :--- | :--- |
| `application/inference_benchmark.py` | Aplicação | `summarize_latencies`: média, percentis, mínimo e máximo |
| `application/http_latency_benchmark.py` | Aplicação | Aquecimento e laço de medição sequencial |
| `infrastructure/http_prediction_client.py` | Infraestrutura | Conexão persistente, `POST /predict`, `GET /health` |
| `http_latency_benchmark.py` | Ponto de entrada | Argumentos, dataset, verificação do `/health`, relatório |

A decisão de desenho que vale registrar: **a camada de aplicação não conhece HTTP.**
`HttpLatencyBenchmark.measure` recebe o envio da requisição como um `Callable[[str], object]`
e um cronômetro como parâmetro. O benefício aparece nos testes — a medição é testável com
funções falsas e um cronômetro determinístico, sem subir servidor, sem rede e sem Docker.
O cliente HTTP real é testado separadamente, contra um servidor efêmero em `127.0.0.1`.

Isso é o mesmo princípio que já governa o resto do projeto: a camada de aplicação orquestra,
a de infraestrutura fala com o mundo externo.

## Reprodutibilidade

```bash
# 1. Artefatos do modelo, se ainda não existirem
uv run --frozen python -m banking_intent_classifier.final_training

# 2. Imagem e container da API
docker build -t banking-intent-classifier:baseline .
docker run -d --rm --name bic-baseline -p 8000:8000 banking-intent-classifier:baseline

# 3. Medição
uv run --frozen python -m banking_intent_classifier.http_latency_benchmark --name sklearn

# 4. Encerramento
docker stop bic-baseline
```

Testes da feature, sem Docker e sem rede externa:

```bash
uv run --frozen pytest \
  tests/application/test_http_latency_benchmark.py \
  tests/test_http_prediction_client.py \
  tests/test_http_latency_benchmark.py \
  tests/application/test_inference_benchmark.py -v
```

O procedimento completo, as opções de linha de comando e a verificação do relatório JSON
estão em [`http-latency-baseline.md`](../http-latency-baseline.md).

## Conceitos aprendidos

- **Latência de serviço e latência de modelo são medições distintas**, e a diferença entre
  elas é o que a engenharia acrescenta ao redor do modelo.
- **Aquecimento, keep-alive e tratamento de falhas** não são detalhes de implementação: cada
  um protege uma propriedade específica da estatística resultante.
- **Throughput sob concorrência unitária é o inverso da latência**, não capacidade.
- **Um Histogram do Prometheus é tão informativo quanto seus buckets.** Escolhê-los sem
  medir antes produz um painel que sobe, não falha e não informa.
- **Medir antes de instrumentar** inverte a ordem intuitiva e é o que torna a
  instrumentação útil.
- **Injetar a dependência externa como função** mantém a lógica de medição na camada de
  aplicação e testável sem infraestrutura.
