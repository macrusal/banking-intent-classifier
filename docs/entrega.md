# Acompanhamento da entrega — Tech Challenge Fase 3

## Rubrica e situação técnica (checkpoint 24/10/2026)

| Critério | Peso | Situação | Evidência / pendência |
| :--- | ---: | :--- | :--- |
| Apache Airflow | 15% | Implementado e validado | DAG concluída, métricas, hashes e testes |
| Prometheus + Grafana | 20% | Pendente | Instrumentação, coleta e dashboards |
| ONNX + benchmark | 20% | Implementado e medido (local) | Equivalência de 100% no teste oficial; latência individual 4–7× menor; lote em empate técnico; ver [`onnx-benchmark.md`](onnx-benchmark.md). Pendente de decisão: API servindo ONNX e benchmark em Linux |
| Arquitetura Cloud | 15% | Pendente | Diagrama, serviços, segurança e justificativas |
| CI/CD | 15% | Parcial | Workflows existentes; conferir aderência à rubrica |
| Apresentação / vídeo STAR | 15% | Pendente | Adiado para depois das frentes técnicas |

**Atenção:** os percentuais são pesos da rubrica, não notas atribuídas. Validar os critérios na rubrica oficial integral.

## Checkpoints

- **21/10/2026:** preparação da lógica reutilizável para orquestração Airflow.
- **22/10/2026:** DAG Airflow 3.1.0 `ingest → train → publish` executada com sucesso.
- **23/10/2026:** inspeção pós-run confirmou métricas e hashes; Ruff aprovado, 36 testes aprovados (1 warning); `main` e `dev` com árvores idênticas no checkpoint. Airflow integrado por PR #34.
- **24/10/2026:** ambiente local alinhado ao CI (Python 3.12); grupo de dependências `onnx` (`skl2onnx`, `onnxruntime` 1.23.x); exportação ONNX determinística; 5 execuções do benchmark no split `test` com 100% de concordância; job `tests` do CI passa a instalar o grupo `onnx` (aguardando execução no GitHub Actions).

## Regras de trabalho e integração

- Fluxo GitFlow `feature/* → dev → main`, por Pull Requests; sem merge direto na `main` protegida.
- Documentação e mensagens de commit em PT-BR.
- Toda afirmação quantitativa usada na avaliação acompanha um comando reproduzível.
- Alterações validadas incrementalmente, com revisão de diff antes da integração.
- Segredos, `.env`, logs, caches, datasets intermediários e artefatos grandes ficam fora do versionamento.

## Próximos passos

1. ~~ONNX: exportação, equivalência de predições e benchmark reproduzível.~~ Concluído em 24/10/2026 ([`onnx-benchmark.md`](onnx-benchmark.md)).
2. Prometheus e Grafana: instrumentação e dashboard (**próxima atividade**).
3. Arquitetura Cloud documentada.
4. Revisão CI/CD e evidências integradas.
5. Vídeo STAR em momento posterior.

## Referências

- [Operação Airflow](operacao-airflow.md)
- [Exportação ONNX e benchmark](onnx-benchmark.md)
- [Arquitetura](architecture.md)
- [Notas de estudo](study-notes/README.md)
