# Acompanhamento da entrega — Tech Challenge Fase 3

## Rubrica e situação técnica (checkpoint 23/10/2026)

| Critério | Peso | Situação | Evidência / pendência |
| :--- | ---: | :--- | :--- |
| Apache Airflow | 15% | Implementado e validado | DAG concluída, métricas, hashes e testes |
| Prometheus + Grafana | 20% | Pendente | Instrumentação, coleta e dashboards |
| ONNX + benchmark | 20% | Parcial | Baseline pronto; conversão e benchmark pendentes |
| Arquitetura Cloud | 15% | Pendente | Diagrama, serviços, segurança e justificativas |
| CI/CD | 15% | Parcial | Workflows existentes; conferir aderência à rubrica |
| Apresentação / vídeo STAR | 15% | Pendente | Adiado para depois das frentes técnicas |

**Atenção:** os percentuais são pesos da rubrica, não notas atribuídas. Validar os critérios na rubrica oficial integral.

## Checkpoints

- **21/10/2026:** preparação da lógica reutilizável para orquestração Airflow.
- **22/10/2026:** DAG Airflow 3.1.0 `ingest → train → publish` executada com sucesso.
- **23/10/2026:** inspeção pós-run confirmou métricas e hashes; Ruff aprovado, 36 testes aprovados (1 warning); `main` e `dev` com árvores idênticas no checkpoint. Airflow integrado por PR #34.

## Regras de trabalho e integração

- Fluxo GitFlow `feature/* → dev → main`, por Pull Requests; sem merge direto na `main` protegida.
- Documentação e mensagens de commit em PT-BR.
- Toda afirmação quantitativa usada na avaliação acompanha um comando reproduzível.
- Alterações validadas incrementalmente, com revisão de diff antes da integração.
- Segredos, `.env`, logs, caches, datasets intermediários e artefatos grandes ficam fora do versionamento.

## Próximos passos

1. ONNX: exportação, equivalência de predições e benchmark reproduzível.
2. Prometheus e Grafana: instrumentação e dashboard.
3. Arquitetura Cloud documentada.
4. Revisão CI/CD e evidências integradas.
5. Vídeo STAR em momento posterior.

## Referências

- [Operação Airflow](operacao-airflow.md)
- [Arquitetura](architecture.md)
- [Notas de estudo](study-notes/README.md)
